shell:
	nix develop -c $$SHELL

run:
	MODEL_NAME=all-MiniLM-L6-v2 EMBED_API_KEY=dev uvicorn embeder.server:app --host 0.0.0.0 --port 8080 --reload

service/deploy:
	./dev-scripts/deploy.sh

service/status:
	fly status

secrets/api-key:
	fly secrets set EMBED_API_KEY=$$(openssl rand -hex 32)
