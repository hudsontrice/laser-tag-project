"""Simple UDP receiver for debugging equipment ID broadcasts.

Run this on the same machine (or another machine adjusting IP in sender) to
verify that player_entry.py UDP messages are being emitted.

Usage (from project root):
	python -m src.net.udp_receiver            # listens on 0.0.0.0:7500
	python -m src.net.udp_receiver 7600       # custom port

Press Ctrl+C to exit.
"""

from __future__ import annotations

import socket
import sys
import datetime as _dt

DEFAULT_PORT = 7500


def run(port: int = DEFAULT_PORT) -> None:
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	# Allow quick restart
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	try:
		sock.bind(("0.0.0.0", port))
	except OSError as e:
		print(f"[ERROR] Could not bind UDP port {port}: {e}")
		return
	print(f"[UDP RECEIVER] Listening on 0.0.0.0:{port} (Ctrl+C to stop)...")
	try:
		while True:
			data, addr = sock.recvfrom(4096)
			ts = _dt.datetime.now().strftime("%H:%M:%S.%f")[:-3]
			print(f"[{ts}] From {addr[0]}:{addr[1]} -> {data!r}")
	except KeyboardInterrupt:
		print("\n[UDP RECEIVER] Stopped.")
	finally:
		sock.close()


if __name__ == "__main__":
	port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
	run(port)

