import argparse
import logging
import os
import socket

from .config import SOCKET_PATH_ENV_VAR, MSGTYPE_ECHO, MSGTYPE_EMBED
from .utils import read_msg, send_msg

logger = logging.getLogger(__name__)

def main() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
     )

    parser = argparse.ArgumentParser("Embeder client")
    parser.add_argument("command", type=str, help="What to do with message")
    parser.add_argument("message", type=str, help="The message")
    args = parser.parse_args()

    socket_path = os.environ.get(SOCKET_PATH_ENV_VAR)
    if socket_path is None:
        raise ValueError(f"Missing ${SOCKET_PATH_ENV_VAR} environment variable")

    logger.info("Using socket path: %s", socket_path)

    logger.debug("Connecting to socket")
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.connect(socket_path)

    try:
        if args.command == "echo":
            send_msg(sock, MSGTYPE_ECHO, args.message.encode("utf-8"))
            _, result = read_msg(sock)
            logger.info(f"Received {result.decode("utf-8")} in response")
        elif args.command == "embed":
            send_msg(sock, MSGTYPE_EMBED, args.message.encode("utf-8"))
            _, result = read_msg(sock)
            logger.info(f"Received {result.decode("utf-8")} in response")
        else:
            raise ValueError(f"Invalid command argument: {args.command}")
    except Exception as e:
        logger.info("Unrecoverable exception: %s", e)
    finally:
        sock.close()


if __name__ == "__main__":
    main()
