import json
import logging
import os
import socket
import struct

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

SOCKET_PATH_ENV_VAR = "SOCKET_PATH"
MODEL_NAME = "MODEL_NAME"

MSGTYPE_ECHO = 0
MSGTYPE_EMBED = 1

def _embed(model: SentenceTransformer, payload: str) -> bytes:
    embedding = model.encode(payload)
    return json.dumps(embedding.tolist()).encode("utf-8")


def _recv_n(sock: socket.socket, n: int) -> bytearray | None:
    data = bytearray()
    # Read from the socket until we've gotten all the data we want or bail
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def _read_msg(sock: socket.socket) -> tuple[int | None,  bytearray | None]:
    raw_msglen = _recv_n(sock, 4)
    if raw_msglen is None:
        return None, None
    msglen = struct.unpack(">I", raw_msglen)[0]
    payload = _recv_n(sock, msglen)
    if payload is None:
        return None, None
    return (int(payload[0]), payload[1:])


def _send_msg(sock: socket.socket, msgtype: int, msgbody: bytes):
    msglen = len(msgbody) + 1
    msg = struct.pack(">I", msglen) + struct.pack("B", msgtype) + msgbody
    sock.sendall(msg)


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

            msgtype, msg = _read_msg(conn)
            if msgtype is None:
                logger.debug("Could not read message type")
                break
            elif msgtype == MSGTYPE_ECHO and msg is not None:
                logger.info("Echoing message")
                _send_msg(sock, MSGTYPE_ECHO, bytes(msg))
            elif msgtype == MSGTYPE_EMBED and msg is not None:
                logger.info("Generating embedding")
                decoded_msg = bytes(msg).decode("utf-8")
                embeded_payload = _embed(model, decoded_msg)
                _send_msg(sock, MSGTYPE_EMBED, embeded_payload)
            else:
                if msg is not None:
                    logger.debug("Received invalid msgtyp: %d", msgtype)
                else:
                    logger.debug("Received empty message")
                break
    except Exception as e:
        logger.info("Unrecoverable exception: %s", e)
    finally:
        sock.close()
        os.remove(socket_path)


if __name__ == "__main__":
    main()
