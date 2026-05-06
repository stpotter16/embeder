FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir sentence-transformers fastapi "uvicorn[standard]"

# Pre-bake the model so the container starts without outbound network access
ENV SENTENCE_TRANSFORMERS_HOME=/app/models
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY embeder/ embeder/
RUN pip install --no-cache-dir --no-deps -e .

CMD ["uvicorn", "embeder.server:app", "--host", "::", "--port", "8080"]
