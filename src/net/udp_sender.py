"""Manual UDP sender utility for testing the receiver.

Usage examples:
	python -m src.net.udp_sender 127.0.0.1 7500 12
	python -m src.net.udp_sender 192.168.1.42 7500 "HELLO"
"""

from __future__ import annotations

import socket
import sys


def main() -> None:
	if len(sys.argv) < 4:
		print("Usage: python -m src.net.udp_sender <ip> <port> <message>")
		return
	ip = sys.argv[1]
	port = int(sys.argv[2])
	msg = " ".join(sys.argv[3:])  # allow spaces without quoting per argument
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	try:
		sock.sendto(msg.encode(), (ip, port))
		print(f"Sent {msg!r} to {ip}:{port}")
	finally:
		sock.close()


if __name__ == "__main__":
	main()

