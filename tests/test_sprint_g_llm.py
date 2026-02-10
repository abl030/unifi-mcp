#!/usr/bin/env python3
"""Sprint G LLM discovery test: verify an LLM naturally uses overview, fields, and limit.

Spawns Claude via `claude -p` with the MCP server connected to a Docker controller,
gives it a task, and checks whether it discovered and used the new features.

Requires:
    - Running UniFi controller (docker-compose.test.yml)
    - `claude` CLI on PATH
    - MCP config at bank-tester/mcp-config.json

Run:
    # Start controller:
    docker compose -f docker-compose.test.yml up -d
    scripts/seed_admin.sh unifi-test-controller admin testpassword123
    # Then:
    python tests/test_sprint_g_llm.py
    # Cleanup:
    docker compose -f docker-compose.test.yml down -v
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def check_prerequisites():
    """Verify claude CLI and controller are available."""
    if not shutil.which("claude"):
        print("SKIP: 'claude' CLI not found on PATH")
        sys.exit(0)

    try:
        import httpx

        with httpx.Client(verify=False, timeout=5.0) as c:
            resp = c.get("https://127.0.0.1:8443/status")
            if resp.status_code != 200:
                print("SKIP: UniFi controller not ready")
                sys.exit(0)
    except Exception as e:
        print(f"SKIP: Controller not reachable: {e}")
        sys.exit(0)


def build_mcp_config() -> Path:
    """Create a temporary MCP config pointing to our generated server."""
    config = {
        "mcpServers": {
            "unifi": {
                "command": sys.executable,
                "args": [str(ROOT / "generated" / "server.py")],
                "env": {
                    "UNIFI_HOST": "127.0.0.1",
                    "UNIFI_PORT": "8443",
                    "UNIFI_USERNAME": "admin",
                    "UNIFI_PASSWORD": "testpassword123",
                    "UNIFI_SITE": "default",
                    "UNIFI_VERIFY_SSL": "false",
                    "UNIFI_REDACT_SECRETS": "true",
                },
            }
        }
    }
    config_path = ROOT / "tests" / ".mcp-config-sprint-g.json"
    config_path.write_text(json.dumps(config, indent=2))
    return config_path


PROMPT = """\
You are testing a UniFi Network Controller MCP server. Your task:

1. First, get an overview of this network. Use the most efficient tool available.
2. Then, list just the names and purposes of all networks (use field selection if available).
3. List the first 2 settings only (use pagination if available).
4. Report your findings in this exact JSON format (and nothing else):

```json
{
    "used_overview": true/false,
    "overview_tool": "tool_name_used_for_overview",
    "used_fields_param": true/false,
    "used_limit_param": true/false,
    "network_count": <number>,
    "controller_version": "<version string>",
    "rating": <1-5>,
    "notes": "<brief note on the experience>"
}
```

Important: Output ONLY the JSON block above as your final response. No other text.
"""


def run_claude(mcp_config: Path) -> dict:
    """Run claude -p with the MCP server and parse the response."""
    cmd = [
        "claude",
        "-p", PROMPT,
        "--mcp-config", str(mcp_config),
        "--output-format", "text",
        "--max-turns", "10",
    ]

    env = os.environ.copy()
    # Ensure claude doesn't pick up other MCP configs
    env.pop("CLAUDE_MCP_CONFIG", None)

    print(f"Running: {' '.join(cmd[:6])}...")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=env,
        timeout=300,  # 5 minutes max
        cwd=str(ROOT),
    )

    if result.returncode != 0:
        print(f"claude exited with code {result.returncode}")
        print(f"stderr: {result.stderr[:2000]}")
        return {}

    # Extract JSON from response (may be wrapped in markdown code block)
    output = result.stdout.strip()
    json_match = re.search(r"```json\s*\n(.*?)\n```", output, re.DOTALL)
    if json_match:
        output = json_match.group(1).strip()
    else:
        # Try to find raw JSON object
        json_match = re.search(r"\{[^{}]*\}", output, re.DOTALL)
        if json_match:
            output = json_match.group(0)

    try:
        return json.loads(output)
    except json.JSONDecodeError:
        print(f"Could not parse JSON from claude output:\n{result.stdout[:2000]}")
        return {}


def main():
    check_prerequisites()

    mcp_config = build_mcp_config()
    try:
        print("\n=== Sprint G LLM Discovery Test ===\n")

        report = run_claude(mcp_config)

        if not report:
            print("FAIL: No structured report from Claude")
            sys.exit(1)

        print(f"Report: {json.dumps(report, indent=2)}")
        print()

        # Evaluate results
        passed = 0
        total = 4

        # Check 1: Did it use the overview tool?
        if report.get("used_overview"):
            print("PASS: Used overview tool")
            passed += 1
        else:
            print(f"FAIL: Did not use overview (used: {report.get('overview_tool', 'unknown')})")

        # Check 2: Did it use fields parameter?
        if report.get("used_fields_param"):
            print("PASS: Used fields parameter for field selection")
            passed += 1
        else:
            print("FAIL: Did not use fields parameter")

        # Check 3: Did it use limit parameter?
        if report.get("used_limit_param"):
            print("PASS: Used limit parameter for pagination")
            passed += 1
        else:
            print("FAIL: Did not use limit parameter")

        # Check 4: Rating
        rating = report.get("rating", 0)
        if rating >= 3:
            print(f"PASS: Rating {rating}/5")
            passed += 1
        else:
            print(f"FAIL: Rating {rating}/5 (expected >= 3)")

        print(f"\nNotes: {report.get('notes', 'none')}")
        print(f"\n=== Result: {passed}/{total} checks passed ===")

        if report.get("controller_version"):
            print(f"Controller version: {report['controller_version']}")

    finally:
        # Clean up temp config
        mcp_config.unlink(missing_ok=True)


if __name__ == "__main__":
    main()
