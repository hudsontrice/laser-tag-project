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
    Table: players(id int primary key, codename varchar(50))

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
    echo ".env created. To load into current shell run:" 
    echo "  export \"$(grep -v '^#' .env | xargs)\"" | sed 's/ /"\n  export "/g' > .env.exports.tmp
    echo "  set -a; source .env; set +a   # (alternative)" 
    # Simple one-liner export hint (without newlines if xargs -d unsupported)
    echo "One-line load: export $(grep -v '^#' .env | xargs)"
fi

echo
read -p "Run the player entry screen now? (y/n): " run_now
if [ "$run_now" == "y" ]; then
    python3 src/ui/player_entry.py
fi
