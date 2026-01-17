# haskell-json-fmt

A JSON formatter with Haskell/Elm-style leading commas and braces.

## Output Style

```json
{ "services":
  { "tangled-knot":
    { "image": "tngl/knot:v1.10.0-alpha"
    , "env":
      { "KNOT_SERVER_HOSTNAME": "knot.nea.moe"
      , "KNOT_SERVER_OWNER": "did:plc:xovnmfdi36npcfhdl5qnaez5"
      }
    }
  }
}
```

## Standalone Usage

```bash
# stdin/stdout
haskell-json-fmt < input.json

# File to stdout
haskell-json-fmt input.json

# Format in place
haskell-json-fmt -i input.json

# Batch format
haskell-json-fmt -i *.json

# Custom indentation
haskell-json-fmt --indent 4 input.json
```

## Nix Flake Usage

### Run directly

```bash
nix run github:lineargraph/haskell-json-fmt -- -i myfile.json
```

### Add to your project with treefmt-nix

```nix
{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
    haskell-json-fmt.url = "github:lineargraph/haskell-json-fmt";
    haskell-json-fmt.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { self, nixpkgs, treefmt-nix, haskell-json-fmt }:
    let
      system = "x86_64-linux";
      pkgs = nixpkgs.legacyPackages.${system};

      treefmtEval = treefmt-nix.lib.evalModule pkgs {
        projectRootFile = "flake.nix";
        imports = [ haskell-json-fmt.treefmtModules.default ];

        # Add other formatters
        programs.nixfmt.enable = true;
      };
    in
    {
      formatter.${system} = treefmtEval.config.build.wrapper;
      checks.${system}.formatting = treefmtEval.config.build.check self;
    };
}
```

Then just run:

```bash
nix fmt
```

### Advanced: Custom configuration

Use `lib.mkTreefmtModule` for more control:

```nix
imports = [
  (haskell-json-fmt.lib.mkTreefmtModule {
    inherit pkgs;
    indent = 4;                    # 4-space indentation
    includes = [ "*.json" ];       # default
    excludes = [
      "package-lock.json"
      "node_modules/**/*.json"
    ];
  })
];
```

### Using the overlay

```nix
{
  nixpkgs.overlays = [ haskell-json-fmt.overlays.default ];
}
# Then pkgs.haskell-json-fmt is available
```

## Exports

| Export | Description |
|--------|-------------|
| `packages.${system}.haskell-json-fmt` | The formatter package |
| `packages.${system}.default` | Same as above |
| `overlays.default` | Nixpkgs overlay adding `haskell-json-fmt` |
| `treefmtModules.default` | treefmt-nix module with default settings |
| `lib.mkTreefmtModule` | Function to create a customized treefmt module |

## License

MIT
