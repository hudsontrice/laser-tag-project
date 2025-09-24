#!/bin/bash
# Laser Tag Project Install Script for Ubuntu

set -e

echo "Updating package list..."
sudo apt-get update

echo "Installing Python3, pip, and PostgreSQL..."
sudo apt-get install -y python3 python3-pip python3-tk postgresql postgresql-contrib

echo "Installing required Python packages..."
pip3 install --upgrade pip
if [ -f requirements.txt ]; then
    pip3 install -r requirements.txt
else
    pip3 install psycopg2-binary
fi

echo
cat << EOF
PostgreSQL expectations:
    Database: photon
    Table: players(id int primary key, codename varchar(255))

You may export environment variables before running:
    export PHOTON_DB_NAME=photon
    export PHOTON_DB_USER=student
    export PHOTON_DB_PASSWORD=secret
    export PHOTON_DB_HOST=localhost
    export PHOTON_DB_PORT=5432

Or let this script create a .env file.
EOF

read -p "Create a .env file now? (y/n): " make_env
if [ "$make_env" = "y" ]; then
    read -p "DB user (default: student): " DBU; DBU=${DBU:-student}
    read -p "DB password (blank allowed): " DBP
    read -p "DB host (default: localhost): " DBH; DBH=${DBH:-localhost}
    read -p "DB port (default: 5432): " DBPORT; DBPORT=${DBPORT:-5432}
    cat > .env << ENVEOF
PHOTON_DB_NAME=photon
PHOTON_DB_USER=$DBU
PHOTON_DB_PASSWORD=$DBP
PHOTON_DB_HOST=$DBH
PHOTON_DB_PORT=$DBPORT
ENVEOF
    echo ".env created in $(pwd)/.env"
    echo "To load it into this shell run:"
    echo "  set -a; source ./.env; set +a"
    echo "Or start a new shell that sources .env, or export individual variables as needed."
fi

echo
echo "Running DB connectivity test..."
python3 tests/test_db.py
if [ $? -eq 0 ]; then
    echo "Database test succeeded."
else
    echo "Database test failed. See output above."
fi

read -p "Run the player entry screen now? (y/n): " run_now
if [ "$run_now" == "y" ]; then
    python3 src/ui/player_entry.py
fi
