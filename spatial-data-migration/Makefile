.PHONY: install test lint format clean

install:
	poetry install

test:
	poetry run pytest tests/ --cov=src/

lint:
	poetry run flake8 src/ tests/
	poetry run mypy src/ tests/

format:
	poetry run black src/ tests/

clean:
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
