# embeder
Basic short sentence embeder

## What is this

Embeder is a service that turns sentences or groups of words into an embedded vector representation using the [sentence-transformers](https://sbert.net/docs/installation.html) library.

Embeder communicates with clients via a Unix socket and is packaged as a NixOS module.

It is meant to be used a systemd service alongside other applications on your server.

## How do I use it

If you are using a nix flake to manage your server's configuration, you can do so by updating the system's flake with

```
modules = [
  ./nixos/configuration.nix
  embeder.nixosModules.default
];
```

then you can enable the service in your configuration file (`configuration.nix`) in teh above example via
```
# Enable the embeder service
services.embeder = {
  enable = true;
  offlineMode = false;
};
```
