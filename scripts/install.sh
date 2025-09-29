#!/usr/bin/env bash

# Bootstrap script for Photon Laser Tag project.
# Installs Python dependencies for the Photon Laser Tag project.

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	echo "[install] Unable to find Python interpreter '$PYTHON_BIN'." >&2
	echo "[install] Install Python 3.9+ and re-run this script." >&2
	exit 1
fi

if [[ ! -f "$PROJECT_ROOT/requirements.txt" ]]; then
	echo "[install] requirements.txt not found. Aborting." >&2
	exit 1
fi

echo "[install] Upgrading pip and wheel"
"$PYTHON_BIN" -m pip install --upgrade pip wheel >/dev/null

echo "[install] Installing Python dependencies"
"$PYTHON_BIN" -m pip install -r "$PROJECT_ROOT/requirements.txt"

cat <<'EOF'

Install complete.

Launch the UI:
  python -m src.main.app

If psycopg2 fails to install, ensure PostgreSQL client libraries are present.
On Debian/Ubuntu systems run:
  sudo apt-get install python3-dev libpq-dev

EOF
