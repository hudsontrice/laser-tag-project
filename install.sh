#!/bin/bash
# Laser Tag Project Install Script for Ubuntu

set -e

echo "Updating package list..."
sudo apt-get update

echo "Installing Python3, pip, and PostgreSQL..."
sudo apt-get install -y python3 python3-pip python3-tk postgresql postgresql-contrib

echo "Installing required Python packages..."
pip3 install --upgrade pip
pip3 install psycopg2-binary

echo
cat << EOF
Make sure PostgreSQL is running and you have created:
- A database named 'photon'
- A table 'players' with columns 'id' (int, primary key) and 'codename' (varchar)

Edit src/ui/player_entry.py with your actual database username and password.
EOF

echo
read -p "Run the app (splash -> player entry) now? (y/n): " run_now
if [ "$run_now" == "y" ]; then
    # Run as a module to ensure package imports work
    python3 -m src.main.app
fi
