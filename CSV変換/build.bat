@echo off
echo === CSV CP942 変換ツール ビルド ===
pip install pyinstaller chardet >nul 2>&1
pyinstaller --onefile --console --name "CSV_CP942変換" convert_cp942.py
echo.
echo 完了。dist\CSV_CP942変換.exe を使ってください。
pause
