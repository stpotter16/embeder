self: { config, lib, pkgs, ... }:
let
  cfg = config.services.embeder;
in {
  options.services.embeder = {
    enable = lib.mkEnableOption "embeder embedding service";

    socketPath = lib.mkOption {
      type = lib.types.str;
      default = "/run/embeder/embeder.sock";
      description = "Path to the Unix domain socket.";
    };

    modelName = lib.mkOption {
      type = lib.types.str;
      default = "all-MiniLM-L6-v2";
      description = "HuggingFace model name to load.";
    };

    modelCacheDir = lib.mkOption {
      type = lib.types.str;
      default = "/var/lib/embeder/models";
      description = ''
        Directory where HuggingFace models are stored. Pre-populate this
        before setting TRANSFORMERS_OFFLINE, or allow the service to
        download on first run by removing the environment variable below.
      '';
    };
  };

  config = lib.mkIf cfg.enable {
    systemd.services.embeder = {
      description = "Embeder sentence embedding service";
      wantedBy = [ "multi-user.target" ];

      environment = {
        SOCKET_PATH = cfg.socketPath;
        MODEL_NAME = cfg.modelName;
        HF_HOME = cfg.modelCacheDir;
        TRANSFORMERS_OFFLINE = "1";
      };

      serviceConfig = {
        ExecStart = "${self.packages.${pkgs.system}.default}/bin/embeder";
        RuntimeDirectory = "embeder";
        StateDirectory = "embeder";
        DynamicUser = true;
        Restart = "on-failure";
      };
    };
  };
}
