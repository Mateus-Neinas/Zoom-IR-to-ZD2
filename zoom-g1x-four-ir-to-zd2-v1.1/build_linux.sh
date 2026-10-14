#!/usr/bin/env bash
set -euo pipefail
python3 -m pip install -r requirements-build.txt
python3 -m PyInstaller --noconfirm --clean --onefile --add-data "IRCAB_IR_ICON.ZD2:." --name Zoom_G1X_FOUR_IR_to_ZD2 main.py
echo "Executable: dist/Zoom_G1X_FOUR_IR_to_ZD2"
