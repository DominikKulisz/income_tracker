#!/bin/bash
# ============================================================
# Finance Tracker – skrypt instalacji i uruchomienia
# ============================================================

set -e

VENV_DIR="$HOME/.finance_tracker_env"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "💰 Finance Tracker – Instalacja"
echo "================================"

# Sprawdź Python 3
if ! command -v python3 &>/dev/null; then
    echo "❌ Python 3 nie jest zainstalowany. Pobierz z https://python.org"
    exit 1
fi

# Utwórz virtualenv jeśli nie istnieje
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Tworzę środowisko wirtualne..."
    python3 -m venv "$VENV_DIR"
fi

# Aktywuj i zainstaluj zależności
source "$VENV_DIR/bin/activate"
echo "📥 Instaluję zależności..."
pip install --quiet --upgrade pip
pip install --quiet rumps

echo "✅ Instalacja zakończona!"
echo ""
echo "🚀 Uruchamiam aplikację..."
cd "$APP_DIR"
python3 app.py
