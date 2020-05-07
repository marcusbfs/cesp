rem @echo off

REM Common variables
call "%~dp0variables.bat"

set sname=cesp.bat
set python_exe="%venv_dir%\Scripts\python.exe"

(
    echo @echo off
    echo %python_exe% %main_py_file% %%*

) > %sname%
