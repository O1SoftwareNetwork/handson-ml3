# Copyright 2023 O1 Software Network. MIT licensed.

SHELL := bash -e -o pipefail

lint:
	black constant/
	isort constant/
	ruff .

MYPY = mypy --ignore-missing-imports

type: typecheck
typecheck:
	$(MYPY) constant/
