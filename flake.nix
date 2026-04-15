{
  description = "Sentence embedding service over a Unix socket";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        py = pkgs.python3;

        embeder = py.pkgs.buildPythonApplication {
          pname = "embeder";
          version = "0.1.0";
          pyproject = true;

          src = ./.;

          build-system = with py.pkgs; [ setuptools ];

          dependencies = with py.pkgs; [
            sentence-transformers
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
            (py.withPackages (ps: with ps; [
              sentence-transformers
              ipython
              mypy
            ]))
          ];
        };
      }
    )

    // {
      nixosModules.default = import ./nix/module.nix self;
    };
}
