.PHONY = fmt t tn

all: fmt

fmt:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place cesp.py scripts/make_exe.py
	isort cesp.py scripts/make_exe.py
	black cesp.py scripts/make_exe.py


t: setup_test
	python .\cesp.py -rdubscall test_folder

tn: setup_test
	python .\cesp.py -rdubscall test_folder -n


setup_test:
	rm -rf test_folder
	python scripts\create_test_folder.py