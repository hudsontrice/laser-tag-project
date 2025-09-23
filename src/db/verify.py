"""Database verification helper.

Run this to confirm the application can connect to the Postgres database and
see the expected `players` table. By default it performs ONLY read / schema
checks. You can optionally test a temporary insert with a flag.

Usage:
    python -m src.db.verify                      # read-only diagnostics
    python -m src.db.verify --insert-test 42 Foo  # attempt insert id=42 codename=Foo (will warn if exists)

Environment variables used (with defaults in parentheses):
    PHOTON_DB_NAME (photon)
    PHOTON_DB_USER (student)
    PHOTON_DB_PASSWORD (blank)
    PHOTON_DB_HOST (localhost)
    PHOTON_DB_PORT (5432)

Exit codes:
    0 = success (connected, table visible)
    1 = connection failure
    2 = table missing
    3 = insert test failed
"""
from __future__ import annotations

import os
import sys
import psycopg2
from psycopg2 import sql

DB_NAME = os.getenv("PHOTON_DB_NAME", "photon")
DB_USER = os.getenv("PHOTON_DB_USER", "student")
DB_PASSWORD = os.getenv("PHOTON_DB_PASSWORD", "")
DB_HOST = os.getenv("PHOTON_DB_HOST", "localhost")
DB_PORT = os.getenv("PHOTON_DB_PORT", "5432")


def connect():  # returns connection
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
    )


def table_exists(cur, table_name: str) -> bool:
    cur.execute(
        sql.SQL(
            """
            SELECT 1 FROM information_schema.tables
            WHERE table_name = %s AND table_schema IN ('public');
            """
        ),
        (table_name,),
    )
    return cur.fetchone() is not None


def read_only_report() -> int:
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                print(f"[OK] Connected to {DB_NAME} as {DB_USER}@{DB_HOST}:{DB_PORT}")

                if not table_exists(cur, "players"):
                    print("[ERROR] Table 'players' not found in schema 'public'.")
                    return 2
                print("[OK] Found table 'players'.")

                cur.execute("SELECT COUNT(*) FROM players;")
                total = cur.fetchone()[0]
                print(f"[INFO] Existing row count: {total}")

                # Show first 10 rows (id,codename)
                cur.execute("SELECT id, codename FROM players ORDER BY id LIMIT 10;")
                rows = cur.fetchall()
                if rows:
                    print("[INFO] Sample rows:")
                    for r in rows:
                        print(f"    id={r[0]} codename={r[1]}")
                else:
                    print("[INFO] Table empty.")
                return 0
    except Exception as e:
        print(f"[ERROR] Connection or query failed: {e}")
        return 1


def insert_test(player_id: int, codename: str) -> int:
    try:
        with connect() as conn:
            with conn.cursor() as cur:
                if not table_exists(cur, "players"):
                    print("[ERROR] Table 'players' missing; aborting insert test.")
                    return 2
                cur.execute("SELECT codename FROM players WHERE id=%s", (player_id,))
                existing = cur.fetchone()
                if existing:
                    print(f"[WARN] Player id {player_id} already exists as '{existing[0]}'; not inserting.")
                    return 0
                cur.execute(
                    "INSERT INTO players (id, codename) VALUES (%s, %s)",
                    (player_id, codename),
                )
                conn.commit()
                print(f"[OK] Inserted player id={player_id} codename={codename}")
                return 0
    except Exception as e:
        print(f"[ERROR] Insert test failed: {e}")
        return 3


def main(argv: list[str]) -> int:
    if not argv:
        return read_only_report()
    if argv[0] == "--insert-test":
        if len(argv) < 3:
            print("Usage: python -m src.db.verify --insert-test <id> <codename>")
            return 3
        try:
            pid = int(argv[1])
        except ValueError:
            print("Player id must be an integer.")
            return 3
        codename = " ".join(argv[2:])
        return insert_test(pid, codename)
    print("Unknown argument.")
    return 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
