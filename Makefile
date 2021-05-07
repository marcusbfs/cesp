
python=cesp_venv\Scripts\python.exe

mypyc:
	$(python) -m  mypy .  --config-file mypy.ini

mypy:
	$(python) -m  mypy .  --ignore-missing-imports --check-untyped-defs --disallow-untyped-calls --disallow-untyped-defs

black:
	$(python) -m black cesp.py scripts