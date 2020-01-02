SET venv_var=cesp_venv

call %venv_var%\Scripts\activate.bat

black cesp.py
pyinstaller -F cesp.py

copy dist\cesp.exe exe /y