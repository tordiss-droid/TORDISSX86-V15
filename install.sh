#!/data/data/com.termux/files/usr/bin/bash

set -e

echo "================================"
echo " TORDISSX86 OSINT INSTALLER"
echo "================================"

pkg update -y
pkg install python git -y

python -m pip install --upgrade pip

if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi

echo ""
echo "Installation completed."
echo "Check README.md for startup instructions."
