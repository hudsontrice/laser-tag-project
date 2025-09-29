#!/usr/bin/env bash

# Bootstrap script for Photon Laser Tag project.
# Installs Python 3 (if missing), pip, required build tooling, and the
# project Python dependencies. Designed for Debian/Ubuntu systems with apt-get.

set -euo pipefail

PROJECT_ROOT="$(cd -- "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON:-python3}"

if [[ $EUID -ne 0 ]]; then
	SUDO="sudo"
else
	SUDO=""
fi

APT_GET="$(command -v apt-get || true)"

apt_install() {
	if [[ -z "$APT_GET" ]]; then
		echo "[install] Unable to locate apt-get. Install required packages manually." >&2
		exit 1
	fi
	if [[ -z "${APT_ALREADY_UPDATED:-}" ]]; then
		echo "[install] Fetching package index via apt-get update"
		$SUDO "$APT_GET" update
		APT_ALREADY_UPDATED=1
	fi
	echo "[install] Installing system packages: $*"
	$SUDO "$APT_GET" install -y "$@"
}

ensure_python() {
	if command -v "$PYTHON_BIN" >/dev/null 2>&1; then
		return
	fi
	if [[ "$PYTHON_BIN" != "python3" ]]; then
		echo "[install] Custom PYTHON override '$PYTHON_BIN' was not found."
		apt_install python3 python3-venv
		PYTHON_BIN="python3"
		return
	fi
	apt_install python3 python3-venv
}

ensure_pip() {
	if "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
		return
	fi
	if command -v pip3 >/dev/null 2>&1; then
		return
	fi
	echo "[install] pip for Python 3 not detected. Installing python3-pip."
	apt_install python3-pip
	if ! "$PYTHON_BIN" -m pip --version >/dev/null 2>&1; then
		echo "[install] Attempting to bootstrap pip via ensurepip"
		"$PYTHON_BIN" -m ensurepip --upgrade >/dev/null 2>&1 || true
	fi
}

ensure_build_tools() {
	apt_install build-essential python3-dev libpq-dev
}

ensure_python
ensure_pip
ensure_build_tools

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
	echo "[install] Unable to find Python interpreter '$PYTHON_BIN'." >&2
	echo "[install] Install Python 3.9+ and re-run this script." >&2
	exit 1
fi

if [[ ! -f "$PROJECT_ROOT/requirements.txt" ]]; then
	echo "[install] requirements.txt not found. Aborting." >&2
	exit 1
fi

echo "[install] Upgrading pip, setuptools, and wheel"
"$PYTHON_BIN" -m pip install --upgrade pip setuptools wheel >/dev/null

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
