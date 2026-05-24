{
  python3,
  stdenv,
  makeWrapper,
}:
let
  python = python3.withPackages (pp: [ pp.pyyaml ]);
in
stdenv.mkDerivation {
  pname = "haskell-json-fmt";
  version = "0.1.0";
  src = ./.;
  buildInputs = [ python ];
  nativeBuildInputs = [ makeWrapper ];
  installPhase = ''
    mkdir -p $out/bin
    cp haskell-json-fmt.py $out/bin/haskell-json-fmt
    chmod +x $out/bin/haskell-json-fmt
    wrapProgram $out/bin/haskell-json-fmt \
      --prefix PATH : ${python}/bin
  '';
  meta = {
    description = "JSON formatter with Haskell/Elm-style leading commas and braces";
    mainProgram = "haskell-json-fmt";
  };
}
