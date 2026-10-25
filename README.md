# TORDISSX86

Cyber OSINT Research & Learning Platform.

## Features
- Web Dashboard
- OSINT Power Control
- Module Center
- Interactive CLI
- Reports
- System Diagnostics
- Password Generator

## Requirements
- Python 3
- Termux or Linux
- Flask

## Local Installation

```bash
git clone YOUR_REPOSITORY_URL
cd TORDISSX86
pip install -r requirements.txt
python web_panel.py

cd ~/TORDISSX86 || exit 1

cat > .gitignore <<'EOF'
__pycache__/
*.pyc
.env
.venv/
venv/
*.log
*.tar.gz
*.zip
reports/*
evidence/*
cases/*
secrets*
