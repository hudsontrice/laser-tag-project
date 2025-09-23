# Laser Tag Project Install Script
# This script installs required Python packages and runs the player entry UI

Write-Host "Checking Python installation..."
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "Python is not installed or not in PATH. Please install Python 3.x and try again."
    exit 1
}

Write-Host "Installing required Python packages..."
python -m pip install --upgrade pip
python -m pip install psycopg2-binary

Write-Host "\nMake sure you have PostgreSQL installed and running."
Write-Host "You must create a database named 'photon' and a table 'players' with columns 'id' (int, primary key) and 'codename' (varchar)."
Write-Host "Edit src/ui/player_entry.py with your actual database username and password."

Write-Host "\nRunning the Player Entry UI..."
python src/ui/player_entry.py
