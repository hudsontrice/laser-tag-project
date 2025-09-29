# Photon Laser Tag Project (Sprint 2)

Language: Python 3

## Team Members

| GitHub Username | Real Name |
| --------------- | --------------- |
| [`@hudsontrice`](https://github.com/hudsontrice) | *Hudson Trice* |
| [`@joshagodoy`](https://github.com/joshagodoy) | *Josh Godoy* |
| [`@houstonmyer`](https://github.com/houstonmyer) | *Houston Myer* |
| [`@jacksonharmon2`](https://github.com/jacksonharmon2) | *Jackson Harmon* |
| [`@griffinkminick`](https://github.com/griffinkminick) | *Griffin Minick* |

---

## Quick Setup

Install the Python dependencies with the helper script:

```bash
bash scripts/install.sh
```
> **Check:** If installing `psycopg2` fails on Debian/Ubuntu, run `sudo apt-get install python3-dev libpq-dev` and rerun the script.

### Run the Instructor UI

```bash
python3 -m src.main.app
```

### Run Tests (N/A for now)

```bash
pytest
```

---

## Repository Contents

```
README.md # Project documentation and instructions
requirements.txt # Python dependencies installed by the helper script
.gitignore # Specifies files Git should ignore
.gitattributes # Configures how Git handles line endings and file types
scripts/install.sh# Bash installer that bootstraps the environment
scripts/run.sh # Placeholder for future launch helpers
src/ # Application source code
tests/ # pytest-based regression tests
```

## src/ Directory Contents

- `src/assets/` – Static media used by the UI (images, sounds, countdown art) with a README describing sourcing guidelines.
- `src/db/` – Database helpers for connecting to PostgreSQL, verifying credentials, and performing player lookups.
- `src/logic/` – Core game-state and scoring rules that orchestrate how laser tag events translate into player stats.
- `src/main/` – Entry points for the instructor-facing application (`app.py`) plus module bootstrapping.
- `src/net/` – UDP networking helpers that send/receive arena events to the rest of the Photon hardware ecosystem.
- `src/ui/` – Tkinter-based user interface screens for splash, player entry, and other operator workflows.
