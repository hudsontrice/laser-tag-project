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
if (Test-Path requirements.txt) {
    python -m pip install -r requirements.txt
} else {
    python -m pip install psycopg2-binary
}

Write-Host "\nMake sure you have PostgreSQL installed and running."
Write-Host "Database expected: photon; table: players(id int primary key, codename varchar(50))."
Write-Host "You can set environment variables PHOTON_DB_NAME, PHOTON_DB_USER, PHOTON_DB_PASSWORD, PHOTON_DB_HOST, PHOTON_DB_PORT before launching."

$createEnv = Read-Host "Create a .env file for DB settings now? (y/n)"
if ($createEnv -eq 'y') {
    $dbUser = Read-Host "DB user (default: student)"
    if (-not $dbUser) { $dbUser = 'student' }
    $dbPass = Read-Host "DB password (leave blank if none)"
    $dbHost = Read-Host "DB host (default: localhost)"
    if (-not $dbHost) { $dbHost = 'localhost' }
    $dbPort = Read-Host "DB port (default: 5432)"
    if (-not $dbPort) { $dbPort = '5432' }
    Set-Content -Path .env -Value @(
        "PHOTON_DB_NAME=photon",
        "PHOTON_DB_USER=$dbUser",
        "PHOTON_DB_PASSWORD=$dbPass",
        "PHOTON_DB_HOST=$dbHost",
        "PHOTON_DB_PORT=$dbPort"
    )
    Write-Host ".env file created. Remember to load it in your shell if needed."
}

$runNow = Read-Host "Run the player entry screen now? (y/n)"
if ($runNow -eq 'y') {
    python src/ui/player_entry.py
}
