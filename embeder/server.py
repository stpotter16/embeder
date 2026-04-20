import json
import logging
import os
import socket

from sentence_transformers import SentenceTransformer

from .config import MODEL_NAME, SOCKET_PATH_ENV_VAR, MSGTYPE_ECHO, MSGTYPE_EMBED
from .utils import read_msg, send_msg

logger = logging.getLogger(__name__)


def _embed(model: SentenceTransformer, payload: str) -> bytes:
    embedding = model.encode(payload)
    return json.dumps(embedding.tolist()).encode("utf-8")


def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
     )

    socket_path = os.environ.get(SOCKET_PATH_ENV_VAR)
    if socket_path is None:
        raise ValueError(f"Missing ${SOCKET_PATH_ENV_VAR} environment variable")

    model_name = os.environ.get(MODEL_NAME)
    if model_name is None:
        raise ValueError(f"Missing ${MODEL_NAME} environment variable")

    logger.info("Downloading model: %s", model_name)
    model = SentenceTransformer(model_name)

    logger.info("Using socket path: %s", socket_path)
    if os.path.exists(socket_path):
        logger.debug("Removing existing socket file at %s", socket_path)
        os.remove(socket_path)

    logger.debug("Connecting to socket")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(socket_path)
    sock.listen(1)

    try:
        while True:
            conn = sock.accept()[0]
            logger.debug("Accepted connection: %s", conn)

            msgtype, msg = read_msg(conn)
            if msgtype is None:
                logger.debug("Could not read message type")
                break
            elif msgtype == MSGTYPE_ECHO and msg is not None:
                logger.info("Echoing message")
                send_msg(conn, MSGTYPE_ECHO, bytes(msg))
            elif msgtype == MSGTYPE_EMBED and msg is not None:
                logger.info("Generating embedding")
                decoded_msg = bytes(msg).decode("utf-8")
                embeded_payload = _embed(model, decoded_msg)
                send_msg(conn, MSGTYPE_EMBED, embeded_payload)
            else:
                if msg is not None:
                    logger.debug("Received invalid msgtyp: %d", msgtype)
                else:
                    logger.debug("Received empty message")
                break
            conn.close()
    except Exception as e:
        logger.info("Unrecoverable exception: %s", e)
    finally:
        sock.close()
        os.remove(socket_path)


if __name__ == "__main__":
    main()
