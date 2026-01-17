{
  description = "Haskell-style JSON formatter";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs =
    { self
    , nixpkgs
    }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forAllSystems = nixpkgs.lib.genAttrs supportedSystems;
      pkgsFor = system: nixpkgs.legacyPackages.${system};

      mkPackage = pkgs:
        pkgs.stdenv.mkDerivation {
          pname = "haskell-json-fmt";
          version = "0.1.0";
          src = ./.;
          buildInputs = [ pkgs.python3 ];
          nativeBuildInputs = [ pkgs.makeWrapper ];
          installPhase = ''
            mkdir -p $out/bin
            cp haskell-json-fmt.py $out/bin/haskell-json-fmt
            chmod +x $out/bin/haskell-json-fmt
            wrapProgram $out/bin/haskell-json-fmt \
              --prefix PATH : ${pkgs.python3}/bin
          '';
          meta = {
            description = "JSON formatter with Haskell/Elm-style leading commas and braces";
            mainProgram = "haskell-json-fmt";
          };
        };
    in
    {
      packages = forAllSystems (system: rec {
        haskell-json-fmt = mkPackage (pkgsFor system);
        default = haskell-json-fmt;
      });

      overlays.default = final: prev: {
        haskell-json-fmt = mkPackage final;
      };

      treefmtModules.default = { pkgs, ... }: {
        settings.formatter.haskell-json-fmt = {
          command = "${mkPackage pkgs}/bin/haskell-json-fmt";
          options = [ "-i" ];
          includes = [ "*.json" ];
        };
      };

      lib.mkTreefmtModule =
        { pkgs
        , includes ? [ "*.json" ]
        , excludes ? [ ]
        , indent ? 2
        }:
        {
          settings.formatter.haskell-json-fmt = {
            command = "${mkPackage pkgs}/bin/haskell-json-fmt";
            options = [ "-i" "--indent" (toString indent) ];
            inherit includes excludes;
          };
        };
    };
}
