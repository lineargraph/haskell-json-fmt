{
  description = "Haskell-style JSON formatter";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      supportedSystems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (system: rec {
        haskell-json-fmt = (pkgsFor system).callPackage ./default.nix { };
        default = haskell-json-fmt;
      });

      overlays.default = final: prev: {
        haskell-json-fmt = final.callPackage ./default.nix { };
      };

      treefmtModules.default =
        { pkgs, ... }:
        {
          settings.formatter.haskell-json-fmt = {
            command = "${pkgs.callPackage ./default.nix { }}/bin/haskell-json-fmt";
            options = [ "-i" ];
            includes = [ "*.json" ];
          };
        };

      lib.mkTreefmtModule =
        {
          pkgs,
          includes ? [ "*.json" ],
          excludes ? [ ],
          allowYaml ? false,
        }:
        {
          settings.formatter.haskell-json-fmt = {
            command = "${pkgs.callPackage ./default.nix { }}/bin/haskell-json-fmt";
            options = [
              "-i"
            ]
            ++ (if allowYaml then [ "--yaml" ] else [ ]);
            inherit includes excludes;
          };
        };
    };
}
