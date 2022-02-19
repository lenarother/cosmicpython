help:
	@echo "test - run tests"

test:
	pytest --flake8 --isort --mypy
