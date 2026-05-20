FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir fastembed fastapi "uvicorn[standard]"

# Pre-bake the model so the container starts without outbound network access
ENV FASTEMBED_CACHE_PATH=/app/models
RUN python -c "from fastembed import TextEmbedding; TextEmbedding('sentence-transformers/all-MiniLM-L6-v2', cache_dir='/app/models')"

COPY embeder/ embeder/
RUN pip install --no-cache-dir --no-deps -e .

CMD ["uvicorn", "embeder.server:app", "--host", "0.0.0.0", "--port", "8080"]
