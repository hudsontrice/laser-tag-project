import os
import psycopg2
from psycopg2 import sql, OperationalError

DB_NAME = os.getenv("PHOTON_DB_NAME", "photon")
DB_USER = os.getenv("PHOTON_DB_USER", "student")
DB_PASSWORD = os.getenv("PHOTON_DB_PASSWORD", "your_password")
DB_HOST = os.getenv("PHOTON_DB_HOST", "localhost")
DB_PORT = os.getenv("PHOTON_DB_PORT", "5432")

def get_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def fetch_players():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql.SQL("SELECT id, codename FROM players ORDER BY id;"))
                return cur.fetchall()
    except OperationalError as e:
        print(f"[DB ERROR] Could not connect: {e}")
    except Exception as e:
        print(f"[UNEXPECTED ERROR] {e}")
    return []

if __name__ == "__main__":
    rows = fetch_players()
    if rows:
        for r in rows:
            print(f"Player {r[0]}: {r[1]}")
    else:
        print("No players found or unable to query.")
