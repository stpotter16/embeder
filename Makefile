shell:
	nix develop -c $$SHELL

service/deploy:
	./dev-scripts/deploy.sh
