.PHONY:fmt t tn tests

all: fmt tests

fmt:
	autoflake --remove-all-unused-imports --remove-unused-variables --in-place cesp.py scripts tests -r
	isort cesp.py scripts/make_exe.py tests
	black cesp.py scripts/make_exe.py tests


tests:
	pytest --cov cesp tests

t: setup_test
	python .\cesp.py -rdubscall test_folder

tn: setup_test
	python .\cesp.py -rdubscall test_folder -n


setup_test:
	rm -rf test_folder
	python scripts\create_test_folder.py