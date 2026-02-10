#!/usr/bin/env python3
"""LLM-powered endpoint discovery for UniFi API using Claude Code CLI.

Uses `claude -p` (Claude Code CLI) to reason about unconfirmed endpoints
(404s, 400s, unverified commands). Claude uses curl via its Bash tool to
make HTTP requests. No Python dependencies beyond stdlib — just needs
`claude` and `curl` on PATH.

Usage:
    python llm-probe/llm_probe.py \
        --host localhost --port 8443 \
        --username admin --password testpassword123 \
        --no-verify-ssl

    # Dry run — show what would be probed:
    python llm-probe/llm_probe.py --dry-run

    # Only probe 400 endpoints (highest value — they definitely exist):
    python llm-probe/llm_probe.py --only-category 400 ...

    # Limit to first 5 for testing:
    python llm-probe/llm_probe.py --max-endpoints 5 ...
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent.parent
NOT_FOUND_FILE = ROOT / "not-found-endpoints.json"
DISCOVERIES_FILE = Path(__file__).parent / "discoveries.json"

DEFAULT_MODEL = "sonnet"

SYSTEM_PROMPT = """\
You are probing a UniFi Network Controller API (v10.0.162, standalone) to discover \
if endpoints exist and how to call them correctly.

You have a pre-authenticated curl cookie file. Use curl via the Bash tool to make \
HTTP requests. The prompt will give you the exact curl prefix to use.

UniFi API patterns:
- Standard response: {"meta": {"rc": "ok"}, "data": [...]}
- Error response: {"meta": {"rc": "error", "msg": "..."}, "data": []}
- Site-scoped paths: /api/s/default/{category}/{resource}
- v2 paths: /v2/api/site/default/{resource}
- stat/ endpoints often need POST with {} or {"start": 0, "end": 9999999999}
- set/ endpoints are PUT-only (GET returns 404). Read current value with \
GET /api/s/default/get/setting/{name} first, then PUT to set/.
- upd/ endpoints need PUT with a resource ID suffix
- list/ endpoints returning 400 may need POST with {} body
- Commands: POST /api/s/default/cmd/{manager} with {"cmd": "command-name"}

Safety rules — NEVER make requests to:
- /api/system/poweroff or /api/system/reboot
- cmd/devmgr or cmd/stamgr with mutation commands (restart, adopt, kick, block, etc.)
Do NOT execute commands that modify device/client state. Only probe for existence.
For set/ endpoints, PUT back the exact same data from get/ — that's a no-op.

Be efficient — try the most likely approach first based on the hints. \
If you get a clear 404 or "api.err.Invalid", the endpoint probably doesn't exist. \
Max 3-4 curl attempts.

IMPORTANT: End your response with exactly one verdict line in this format:
VERDICT: FOUND — description of how to call it
VERDICT: NOT_FOUND — endpoint does not exist on this controller version
VERDICT: NEEDS_DEVICE — endpoint likely works but requires adopted devices/clients
VERDICT: UNCERTAIN — got ambiguous results, explain what happened

Keep your response concise.\
"""


# ── Endpoint flattening ────────────────────────────────────────────────────
def flatten_endpoints(data: dict) -> list[dict]:
    """Flatten not-found-endpoints.json into a list of probe targets."""
    endpoints: list[dict] = []

    # 404 endpoints
    nf = data.get("not_found_404", {})
    for section_key in ("rest_endpoints", "list_endpoints", "stat_endpoints",
                        "upd_endpoints", "group_endpoints", "set_endpoints",
                        "websocket_endpoints"):
        for ep in nf.get(section_key, []):
            category = section_key.replace("_endpoints", "")
            endpoints.append({
                "source_category": "404",
                "category": category,
                "name": ep["name"],
                "path": ep.get("path", ""),
                "method_tried": ep.get("method_tried", "GET"),
                "note": ep.get("note", ""),
                "try_next": ep.get("try_next", []),
                "original_status": 404,
            })

    # 400 endpoints
    amb = data.get("ambiguous_400", {})
    for section_key in ("global_endpoints", "rest_endpoints", "list_endpoints",
                        "stat_endpoints", "v2_endpoints", "cnt_endpoints"):
        for ep in amb.get(section_key, []):
            category = section_key.replace("_endpoints", "")
            endpoints.append({
                "source_category": "400",
                "category": category,
                "name": ep["name"],
                "path": ep.get("path", ""),
                "method_tried": ep.get("method_tried", "GET"),
                "note": ep.get("note", ""),
                "try_next": ep.get("try_next", []),
                "original_status": 400,
            })

    # Unverified commands
    uv = data.get("unverified_commands", {})
    for manager, mgr_info in uv.get("managers", {}).items():
        mgr_path = mgr_info.get("path", "")
        for cmd_info in mgr_info.get("commands", []):
            endpoints.append({
                "source_category": "cmd",
                "category": "cmd",
                "name": f"{manager}/{cmd_info['cmd']}",
                "path": mgr_path,
                "method_tried": "none",
                "note": cmd_info.get("note", ""),
                "try_next": [],
                "original_status": None,
                "cmd": cmd_info["cmd"],
                "cmd_params": cmd_info.get("params", []),
                "safe_to_try": cmd_info.get("safe_to_try", False),
                "manager": manager,
            })

    return endpoints


# ── Cookie-based auth via curl ─────────────────────────────────────────────
def login_curl(host: str, port: int, username: str, password: str,
               verify_ssl: bool, cookie_file: str) -> tuple[bool, str | None]:
    """Login via curl and save cookies to file. Returns (ok, csrf_token)."""
    cmd = [
        "curl", "-s", "-X", "POST",
        f"https://{host}:{port}/api/login",
        "-H", "Content-Type: application/json",
        "-d", json.dumps({"username": username, "password": password}),
        "-c", cookie_file,
    ]
    if not verify_ssl:
        cmd.append("-k")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        return False, None

    # Extract CSRF token from cookie file
    csrf_token = None
    try:
        with open(cookie_file) as f:
            for line in f:
                if "csrf_token" in line:
                    parts = line.strip().split("\t")
                    if len(parts) >= 7:
                        csrf_token = parts[6]
    except Exception:
        pass

    try:
        resp = json.loads(result.stdout)
        if resp.get("meta", {}).get("rc") == "ok":
            return True, csrf_token
    except (json.JSONDecodeError, AttributeError):
        pass
    return False, None


# ── Build prompt for each endpoint ──────────────────────────────────────────
def build_prompt(ep: dict, site: str, cookie_file: str,
                 csrf_token: str | None, base_url: str,
                 verify_ssl: bool) -> str:
    """Build the prompt for a single endpoint probe."""
    path = ep["path"].replace("{site}", site)

    # Build curl prefix
    curl_parts = ["curl", "-s", "-b", cookie_file, "-c", cookie_file]
    if csrf_token:
        curl_parts.extend(["-H", f'"X-Csrf-Token: {csrf_token}"'])
    if not verify_ssl:
        curl_parts.append("-k")
    curl_base = " ".join(curl_parts)

    lines = [
        f"Probe this UniFi API endpoint: {ep['category']}/{ep['name']}",
        f"Base URL: {base_url}",
        f"Full path: {path}",
        "",
        f"Curl prefix (already authenticated):",
        f"  {curl_base}",
        "",
        f"Example GET:  {curl_base} {base_url}{path}",
        f"Example POST: {curl_base} -X POST -H 'Content-Type: application/json' -d '{{}}' {base_url}{path}",
    ]

    if ep["source_category"] == "cmd":
        cmd = ep.get("cmd", "")
        params = ep.get("cmd_params", [])
        safe = ep.get("safe_to_try", False)
        lines.append("")
        lines.append(f'This is a command: POST {path} with body {{"cmd": "{cmd}"}}')
        if params:
            lines.append(f"Expected params: {', '.join(params)}")
        if safe:
            lines.append("This command is SAFE to try (read-only/reversible).")
        else:
            lines.append(
                "This command is NOT safe to execute. Only verify the manager path "
                "exists (POST with empty JSON body — if you get 400 with 'api.err.Invalid', "
                "the manager exists). Do NOT execute the actual command."
            )
    else:
        lines.append(f"")
        lines.append(f"Previously tried: {ep['method_tried']} -> {ep['original_status']}")

    if ep.get("note"):
        lines.append(f"Note: {ep['note']}")

    if ep.get("try_next"):
        lines.append(f"Hints: {'; '.join(ep['try_next'])}")

    lines.append("")
    lines.append("Make curl requests to determine if this endpoint works. "
                  "Give your VERDICT at the end.")

    return "\n".join(lines)


# ── Parse verdict from Claude's output ──────────────────────────────────────
def parse_verdict(text: str) -> tuple[str, str]:
    """Extract verdict and notes from Claude's output."""
    for line in reversed(text.split("\n")):
        # Strip markdown bold markers only (keep underscores — needed for NOT_FOUND)
        clean = re.sub(r'\*+', '', line.strip())
        clean = re.sub(r'`', '', clean)
        if "VERDICT:" in clean.upper():
            idx = clean.upper().index("VERDICT:")
            rest = clean[idx + len("VERDICT:"):].strip()
            for v in ("FOUND", "NOT_FOUND", "NEEDS_DEVICE", "UNCERTAIN"):
                if rest.upper().startswith(v):
                    notes = rest[len(v):].strip().lstrip("\u2014-:").strip()
                    return v, notes
            return "UNCERTAIN", rest
    return "UNCERTAIN", "No verdict line found"


# ── Probe one endpoint ─────────────────────────────────────────────────────
def probe_endpoint(ep: dict, site: str, cookie_file: str,
                   csrf_token: str | None, base_url: str,
                   verify_ssl: bool, index: int, total: int,
                   model: str) -> dict:
    """Probe one endpoint using claude -p. Returns a result dict."""

    path_display = ep["path"].replace("{site}", site)

    # Print header
    print(f"\n{'=' * 70}")
    print(f"[{index}/{total}] {ep['category']}/{ep['name']}")
    print(f"  Path: {path_display}")
    if ep["original_status"]:
        print(f"  Previous: {ep['method_tried']} -> {ep['original_status']}")
    if ep.get("try_next"):
        print(f"  Hints: {'; '.join(ep['try_next'][:3])}")
    print(f"{'-' * 70}")
    sys.stdout.flush()

    prompt = build_prompt(ep, site, cookie_file, csrf_token,
                          base_url, verify_ssl)

    cmd = [
        "claude", "-p",
        "--permission-mode", "bypassPermissions",
        "--model", model,
        "--append-system-prompt", SYSTEM_PROMPT,
        prompt,
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180,
            env={**os.environ, "TERM": "dumb"},
        )
        output = result.stdout
    except subprocess.TimeoutExpired:
        output = "VERDICT: UNCERTAIN — timed out"
    except Exception as e:
        output = f"VERDICT: UNCERTAIN — error running claude: {e}"

    # Print Claude's output (indented)
    for line in output.strip().split("\n"):
        print(f"  {line}")

    verdict, notes = parse_verdict(output)
    print(f"\n  >>> VERDICT: {verdict}" + (f" — {notes}" if notes else ""))
    sys.stdout.flush()

    # Build result
    result_dict: dict = {
        "category": ep["category"],
        "name": ep["name"],
        "path": path_display,
        "original_status": ep["original_status"],
        "verdict": verdict,
        "notes": notes,
    }

    # Try to detect a 200 in Claude's output
    if re.search(r'(?:HTTP|status|returned|"rc":\s*"ok")\s*200|"rc":\s*"ok"', output):
        result_dict["response_status"] = 200

    return result_dict


# ── Dry run ─────────────────────────────────────────────────────────────────
def dry_run(endpoints: list[dict]):
    """Print what would be probed without calling LLM or controller."""
    by_category: dict[str, list[dict]] = {}
    for ep in endpoints:
        by_category.setdefault(ep["source_category"], []).append(ep)

    for cat, eps in sorted(by_category.items()):
        print(f"\n--- {cat.upper()} ({len(eps)} endpoints) ---")
        for ep in eps:
            hints = "; ".join(ep.get("try_next", [])[:2])
            safe = ""
            if ep["source_category"] == "cmd":
                safe = " [SAFE]" if ep.get("safe_to_try") else " [UNSAFE-skip]"
            note = f"  ({ep['note']})" if ep.get("note") else ""
            print(f"  {ep['category']}/{ep['name']:<35s} {hints}{safe}{note}")

    print(f"\nTotal: {len(endpoints)} endpoints")
    actionable = [e for e in endpoints
                  if e["source_category"] != "cmd" or e.get("safe_to_try")]
    print(f"Actionable (will probe): {len(actionable)}")
    skipped = len(endpoints) - len(actionable)
    if skipped:
        print(f"Skipped (unsafe commands): {skipped}")


# ── Main ────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="LLM endpoint discovery via Claude Code CLI",
    )
    parser.add_argument("--host", default=os.environ.get("UNIFI_HOST", ""),
                        help="Controller hostname/IP (env: UNIFI_HOST)")
    parser.add_argument("--port", type=int,
                        default=int(os.environ.get("UNIFI_PORT", "8443")),
                        help="Controller port (default: 8443)")
    parser.add_argument("--username", default=os.environ.get("UNIFI_USERNAME", ""),
                        help="Admin username (env: UNIFI_USERNAME)")
    parser.add_argument("--password", default=os.environ.get("UNIFI_PASSWORD", ""),
                        help="Admin password (env: UNIFI_PASSWORD)")
    parser.add_argument("--site", default=os.environ.get("UNIFI_SITE", "default"),
                        help="Site name (default: 'default')")
    parser.add_argument("--no-verify-ssl", action="store_true",
                        help="Disable SSL certificate verification")
    parser.add_argument("--dry-run", action="store_true",
                        help="Show what would be probed without calling LLM")
    parser.add_argument("--only-category", choices=["404", "400", "cmd"],
                        help="Only probe one category of endpoints")
    parser.add_argument("--max-endpoints", type=int, default=0,
                        help="Limit number of endpoints to probe (0=all)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="Claude model to use (default: sonnet)")
    parser.add_argument("--not-found-file", type=Path, default=NOT_FOUND_FILE,
                        help="Path to not-found-endpoints.json")
    parser.add_argument("--output", type=Path, default=DISCOVERIES_FILE,
                        help="Output discoveries file")
    args = parser.parse_args()

    # Load not-found-endpoints.json
    if not args.not_found_file.exists():
        print(f"ERROR: {args.not_found_file} not found", file=sys.stderr)
        sys.exit(1)
    data = json.loads(args.not_found_file.read_text())

    # Flatten all endpoints
    endpoints = flatten_endpoints(data)

    # Filter by category
    if args.only_category:
        endpoints = [e for e in endpoints
                     if e["source_category"] == args.only_category]

    # Apply max limit
    if args.max_endpoints > 0:
        endpoints = endpoints[:args.max_endpoints]

    if args.dry_run:
        dry_run(endpoints)
        sys.exit(0)

    # Validate required args
    if not args.host:
        print("ERROR: --host required (or set UNIFI_HOST)", file=sys.stderr)
        sys.exit(1)
    if not args.username or not args.password:
        print("ERROR: --username and --password required", file=sys.stderr)
        sys.exit(1)

    # Check claude CLI is available
    try:
        subprocess.run(["claude", "--version"], capture_output=True, timeout=10)
    except FileNotFoundError:
        print("ERROR: 'claude' CLI not found on PATH", file=sys.stderr)
        sys.exit(1)

    verify_ssl = not args.no_verify_ssl
    if os.environ.get("UNIFI_VERIFY_SSL", "").lower() in ("false", "0", "no"):
        verify_ssl = False

    base_url = f"https://{args.host}:{args.port}"

    # Create temp cookie file (persists across all probes)
    cookie_fd, cookie_file = tempfile.mkstemp(suffix=".txt", prefix="unifi_cookies_")
    os.close(cookie_fd)

    try:
        # Login
        print("Authenticating via curl...", file=sys.stderr)
        ok, csrf_token = login_curl(
            args.host, args.port, args.username, args.password,
            verify_ssl, cookie_file,
        )
        if not ok:
            print("FATAL: Authentication failed", file=sys.stderr)
            sys.exit(1)
        print(f"Authenticated. Cookie file: {cookie_file}", file=sys.stderr)

        print(f"\nProbing {len(endpoints)} endpoints with claude -p ({args.model})...\n")
        sys.stdout.flush()

        results = []
        try:
            for i, ep in enumerate(endpoints, 1):
                # Refresh cookies every 15 endpoints
                if i > 1 and i % 15 == 0:
                    print("  [Refreshing auth cookies...]", file=sys.stderr)
                    login_curl(args.host, args.port, args.username,
                               args.password, verify_ssl, cookie_file)

                result = probe_endpoint(
                    ep, args.site, cookie_file, csrf_token,
                    base_url, verify_ssl, i, len(endpoints), args.model,
                )
                results.append(result)
        except KeyboardInterrupt:
            print("\n\nInterrupted! Saving partial results...", file=sys.stderr)
    finally:
        try:
            os.unlink(cookie_file)
        except OSError:
            pass

    # Build summary
    summary = {
        "total_probed": len(results),
        "found": sum(1 for r in results if r["verdict"] == "FOUND"),
        "not_found": sum(1 for r in results if r["verdict"] == "NOT_FOUND"),
        "needs_device": sum(1 for r in results if r["verdict"] == "NEEDS_DEVICE"),
        "uncertain": sum(1 for r in results if r["verdict"] == "UNCERTAIN"),
    }

    output = {
        "probed_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "controller_version": data.get("controller_version", "unknown"),
        "model": args.model,
        "results": results,
        "summary": summary,
    }

    # Write discoveries
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n")
    print(f"\nWrote {args.output}", file=sys.stderr)

    # Print summary
    print(f"\n{'=' * 70}")
    print("  Summary")
    print(f"{'=' * 70}")
    print(f"  Total probed:  {summary['total_probed']}")
    print(f"  FOUND:         {summary['found']}")
    print(f"  NOT_FOUND:     {summary['not_found']}")
    print(f"  NEEDS_DEVICE:  {summary['needs_device']}")
    print(f"  UNCERTAIN:     {summary['uncertain']}")
    print()


if __name__ == "__main__":
    main()
