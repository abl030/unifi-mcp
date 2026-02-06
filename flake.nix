{
  description = "AI-generated MCP server for the Ubiquiti UniFi Network Controller API — 137 tools";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { self, nixpkgs }:
    let
      forAllSystems = nixpkgs.lib.genAttrs [
        "x86_64-linux"
        "aarch64-linux"
      ];
    in
    {
      packages = forAllSystems (system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
          pythonEnv = pkgs.python3.withPackages (ps: [
            ps.fastmcp
            ps.httpx
          ]);
        in
        {
          default = pkgs.writeShellApplication {
            name = "unifi-mcp";
            runtimeInputs = [ pythonEnv ];
            text = ''
              exec fastmcp run ${./generated/server.py}
            '';
          };
        }
      );
    };
}
