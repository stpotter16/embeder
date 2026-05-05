{
  description = "Sentence embedding service";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    #0.4.36 release
    flyctl-nixpkgs.url = "github:NixOS/nixpkgs/01fbdeef22b76df85ea168fbfe1bfd9e63681b30";
  };

  outputs = { self, nixpkgs, flake-utils, flyctl-nixpkgs }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        flyctl = flyctl-nixpkgs.legacyPackages.${system}.flyctl;
        py = pkgs.python3;

        embeder = py.pkgs.buildPythonApplication {
          pname = "embeder";
          version = "0.1.0";
          pyproject = true;

          src = pkgs.lib.cleanSource ./.;

          build-system = with py.pkgs; [ setuptools ];

          dependencies = with py.pkgs; [
            sentence-transformers
            fastapi
            uvicorn
          ];
        };
      in
      {
        packages.default = embeder;

        apps.default = {
          type = "app";
          program = "${embeder}/bin/embeder";
        };

        devShells.default = pkgs.mkShell {
          packages = [
            flyctl
            (py.withPackages (ps: with ps; [
              sentence-transformers
              fastapi
              uvicorn
              ipython
              mypy
            ]))
          ];
        };
      }
    );
}
