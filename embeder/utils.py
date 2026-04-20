import socket
import struct


def send_msg(sock: socket.socket, msgtype: int, msgbody: bytes):
    msglen = len(msgbody) + 1
    msg = struct.pack(">I", msglen) + struct.pack("B", msgtype) + msgbody
    sock.sendall(msg)


def read_msg(sock: socket.socket) -> tuple[int | None,  bytearray | None]:
    raw_msglen = _recv_n(sock, 4)
    if raw_msglen is None:
        return None, None
    msglen = struct.unpack(">I", raw_msglen)[0]
    payload = _recv_n(sock, msglen)
    if payload is None:
        return None, None
    return (int(payload[0]), payload[1:])


def _recv_n(sock: socket.socket, n: int) -> bytearray | None:
    data = bytearray()
    # Read from the socket until we've gotten all the data we want or bail
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


