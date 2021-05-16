import subprocess
import time
from pathlib import Path

from rich import print

main_base = "cesp.py"
script_dir: Path = Path(__file__).parent.resolve()
repo_dir: Path = Path(script_dir / "..").resolve()
main_py: Path = Path(repo_dir / main_base)
env_dir: Path = Path(repo_dir / "cesp_venv")

if not env_dir.is_dir():
    env_dir = Path(repo_dir / "env")

if not env_dir.is_dir():
    env_dir = Path(repo_dir / "env")
    raise RuntimeError("Could not find virtual env folder")

python_exe = env_dir / "Scripts" / "python.exe"

cmd = [
    str(python_exe),
    "-m",
    "PyInstaller",
    "-F",
    "-c",
    "--icon",
    "NONE",
    "--clean",
    str(main_py),
]

start_time = time.time()
subprocess.call(cmd, shell=True)
elapsed_time = time.time() - start_time


str_time = f"Finished building dist in {elapsed_time:.2f} seconds"
str_symbol = "#"
str_underline = "".join([str_symbol for i in range(len(str_time) + 4)])

print(cmd)

print(f"\n{str_underline}\n{str_symbol} {str_time} {str_symbol}\n{str_underline}")
