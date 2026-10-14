@echo off
setlocal
py -m pip install -r requirements-build.txt
py -m PyInstaller --noconfirm --clean --onefile --windowed --add-data "IRCAB_IR_ICON.ZD2;." --name Zoom_G1X_FOUR_IR_to_ZD2 main.py
echo.
echo Executable: dist\Zoom_G1X_FOUR_IR_to_ZD2.exe
pause
