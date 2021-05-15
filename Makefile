python=cesp_venv\Scripts\python.exe
.PHONY = fmt

all: fmt

fmt:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place cesp.py scripts/make_exe.py
	isort cesp.py scripts/make_exe.py
	black cesp.py scripts/make_exe.py

mypyc:
	$(python) -m  mypy .  --config-file mypy.ini

mypy:
	$(python) -m  mypy .  --ignore-missing-imports --check-untyped-defs --disallow-untyped-calls --disallow-untyped-defs
