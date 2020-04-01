del /f /s /q build 1>nul
rmdir /s /q build

del /f /s /q dist 1>nul
rmdir /s /q dist

del /f /s /q __pycache__ 1>nul
rmdir /s /q __pycache__