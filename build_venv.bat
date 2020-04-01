SET venv_var=cesp_venv

call python -m venv %venv_var%
call %venv_var%\Scripts\activate.bat

pip install -r requirements.txt