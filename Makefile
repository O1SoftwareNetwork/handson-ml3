# Copyright 2023 O1 Software Network. MIT licensed.

SHELL := bash -e -o pipefail

lint:
	black constant/
	isort constant/
	ruff .

test:
	python -W error -m unittest constant/*/*/*_test.py

MYPY = mypy --ignore-missing-imports --no-namespace-packages

type: typecheck
typecheck:
	$(MYPY) constant/
