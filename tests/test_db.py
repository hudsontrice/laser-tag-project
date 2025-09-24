import os
import sys
import psycopg2
from psycopg2 import OperationalError

db_name = os.getenv("PHOTON_DB_NAME", "photon")
db_user = os.getenv("PHOTON_DB_USER", "student")
db_password = os.getenv("PHOTON_DB_PASSWORD", "")
db_host = os.getenv("PHOTON_DB_HOST", "localhost")
db_port = os.getenv("PHOTON_DB_PORT", "5432")

test_id = 99999
test_codename = "TEST_PLAYER_AUTOTEST"

def main():
    try:
        conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
    except OperationalError as e:
        print(f"DB connection failed: {e}")
        sys.exit(1)
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id INTEGER PRIMARY KEY,
                    codename VARCHAR(255) NOT NULL
                );
            """)
            conn.commit()
            cur.execute(
                "INSERT INTO players (id, codename) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING;",
                (test_id, test_codename)
            )
            conn.commit()
            cur.execute("SELECT id, codename FROM players WHERE id=%s;", (test_id,))
            row = cur.fetchone()
            if row:
                print(f"OK: Found test row: {row}")
                sys.exit(0)
            else:
                print("WARN: Test row not found after insert.")
                sys.exit(2)
    except Exception as e:
        print(f"Error during DB ops: {e}")
        sys.exit(3)
    finally:
        conn.close()

if __name__ == "__main__":
    main()
