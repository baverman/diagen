.PHONY: fmt lint all watch codegen

fmt:
	ruff check --select I --fix
	ruff format

lint:
	ruff check
	mypy

all: fmt lint

diagen/props.py: diagen/props-gen.py
	python diagen/props-gen.py

codegen: diagen/props.py
