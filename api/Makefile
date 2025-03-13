.PHONY: install up down logs shell test lint

# Install dependencies
install:
	pipenv install

# Start the API and database
up:
	docker compose up -d
	pipenv run uvicorn main:app --reload --host $$(python -c "from config import API_HOST; print(API_HOST)") --port $$(python -c "from config import API_PORT; print(API_PORT)")

# Stop the API and database
down:
	docker compose down

# View API logs
logs:
	docker compose logs -f

# Open a shell in the API container
shell:
	docker compose exec mongodb mongosh

# Run tests
test:
	pipenv run pytest

# Run linters
lint:
	pipenv run black .
	pipenv run isort .
	pipenv run flake8

# Clean up
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} +
	find . -type d -name "*.egg" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".coverage" -exec rm -r {} +
	find . -type d -name "htmlcov" -exec rm -r {} + 