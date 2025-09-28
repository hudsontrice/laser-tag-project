from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator, Optional, Tuple

import psycopg2
from psycopg2.extensions import connection as PGConnection

_DB_PARAMS = {
	"dbname": os.getenv("PHOTON_DB_NAME", "photon"),
	"user": os.getenv("PHOTON_DB_USER", "student"),
	#"password": os.getenv("PHOTON_DB_PASSWORD", "student"),
	#"host": os.getenv("PHOTON_DB_HOST", "localhost"),
	#"port": os.getenv("PHOTON_DB_PORT", "5432"),
}


@contextmanager
def get_connection() -> Iterator[PGConnection]:
	# Yield a live psycopg2 connection and ensure it closes afterwards.
	conn = psycopg2.connect(**_DB_PARAMS)
	try:
		yield conn
	finally:
		conn.close()


def fetch_player(player_id: int) -> Optional[Tuple[int, str]]:
	"""Return (id, codename) if the player exists, otherwise ``None``. -HT"""
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT id, codename FROM players WHERE id=%s", (player_id,))
			row = cur.fetchone()
	return (int(row[0]), str(row[1])) if row else None


def upsert_player(player_id: int, codename: str) -> None:
	"""Insert or update a player's codename. -HT"""
	with get_connection() as conn:
		with conn.cursor() as cur:
			cur.execute("SELECT 1 FROM players WHERE id=%s", (player_id,))
			exists = cur.fetchone() is not None
			if exists:
				cur.execute("UPDATE players SET codename=%s WHERE id=%s", (codename, player_id))
			else:
				cur.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (player_id, codename))
		conn.commit()

__all__ = [
	"fetch_player",
	"get_connection",
	"upsert_player",
]
