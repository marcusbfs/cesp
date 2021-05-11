import os
import pathlib
import subprocess
import time

main_base = "cesp.py"
script_dir = pathlib.Path(__file__).parent.absolute()
repo_dir = os.path.abspath(os.path.join(script_dir, ".."))
main_py = os.path.join(repo_dir, main_base)
env_dir = "cesp_venv"
python_exe = os.path.join(repo_dir, env_dir, "Scripts", "python.exe")

cmd = [python_exe, "-m", "PyInstaller", "-F", "-c", main_py]

start_time = time.time()
subprocess.call(cmd, shell=True)
elapsed_time = time.time() - start_time

str_time = f"Finished building dist in {elapsed_time:.2f} seconds"
str_symbol = "#"
str_underline = "".join([str_symbol for i in range(len(str_time) + 4)])

print(f"\n{str_underline}\n{str_symbol} {str_time} {str_symbol}\n{str_underline}")
