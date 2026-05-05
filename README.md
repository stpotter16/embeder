# embeder

Basic short sentence embedder — a private REST API deployed on Fly.io that converts text into vector embeddings using [sentence-transformers](https://sbert.net/docs/installation.html).

## What is this

Embeder takes a text string and returns a high-dimensional float vector representation using the `all-MiniLM-L6-v2` model (384 dimensions). It runs as a private Fly.io app accessible only to other services in the same organization over the Fly.io private network (6PN).

## Deploying

```bash
# First time: create the app and set the API key secret
fly launch --no-deploy
fly secrets set EMBED_API_KEY=$(openssl rand -hex 32)

# Deploy
fly deploy
```

Update `primary_region` in `fly.toml` to match your other services before deploying.

## API

All endpoints require the `X-API-Key` header (value from the `EMBED_API_KEY` Fly secret).

### Health check

```bash
curl http://embeder.internal:8080/health
```

```json
{"status": "ok"}
```

### Embed text

```bash
curl http://embeder.internal:8080/embed \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $EMBED_API_KEY" \
  -d '{"text": "the quick brown fox"}'
```

```json
{"embedding": [0.031, -0.012, ...]}
```

The returned array has 384 elements (dimensions of `all-MiniLM-L6-v2`).

## Local development

```bash
make shell  # enters nix dev shell

MODEL_NAME=all-MiniLM-L6-v2 EMBED_API_KEY=dev embeder
```
