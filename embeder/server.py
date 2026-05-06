import logging
import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from .config import API_KEY_ENV_VAR, MODEL_NAME_ENV_VAR

logger = logging.getLogger(__name__)

_model: "SentenceTransformer | None" = None
_api_key: str = ""

api_key_header = APIKeyHeader(name="X-API-Key")


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _api_key

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    model_name = os.environ.get(MODEL_NAME_ENV_VAR)
    if not model_name:
        raise ValueError(f"Missing ${MODEL_NAME_ENV_VAR} environment variable")

    _api_key = os.environ.get(API_KEY_ENV_VAR, "")
    if not _api_key:
        raise ValueError(f"Missing ${API_KEY_ENV_VAR} environment variable")

    from sentence_transformers import SentenceTransformer

    logger.info("Loading model: %s", model_name)
    _model = SentenceTransformer(model_name)
    logger.info("Model ready")

    yield


app = FastAPI(lifespan=lifespan)


class EmbedRequest(BaseModel):
    text: str


class EmbedResponse(BaseModel):
    embedding: list[float]


def _require_api_key(key: str = Security(api_key_header)) -> None:
    if key != _api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/embed", response_model=EmbedResponse)
def embed(body: EmbedRequest, _: None = Depends(_require_api_key)):
    assert _model is not None
    return EmbedResponse(embedding=_model.encode(body.text).tolist())


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)


if __name__ == "__main__":
    main()
