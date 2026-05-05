shell:
	nix develop -c $$SHELL

service/deploy:
	./dev-scripts/deploy.sh

service/status:
	fly status

secrets/api-key:
	fly secrets set EMBED_API_KEY=$$(openssl rand -hex 32)
