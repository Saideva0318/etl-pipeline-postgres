.PHONY: help install lint format test test-cov docker-up docker-down run clean

## help: Show this help message
help:
	@echo "ETL Pipeline — Available commands:"
	@sed -n 's/^##//p' $(MAKEFILE_LIST) | column -t -s ':' | sed -e 's/^/ /'

## install: Install Python dependencies
install:
	pip install -r requirements.txt
	pre-commit install

## lint: Run flake8 linter
lint:
	flake8 src/ tests/ dags/ --max-line-length=120 --ignore=E203,W503

## format: Format code with Black
format:
	black src/ tests/ dags/ --line-length 120
	isort src/ tests/ dags/

## test: Run unit tests
test:
	pytest tests/ -v --tb=short

## test-cov: Run tests with coverage report
test-cov:
	pytest tests/ -v --cov=src --cov-report=term-missing --cov-report=html

## docker-up: Start PostgreSQL + pipeline containers
docker-up:
	docker-compose up -d --build
	@echo "Waiting for PostgreSQL to be ready..."
	@sleep 5
	docker-compose exec postgres pg_isready

## docker-down: Stop all containers
docker-down:
	docker-compose down -v

## run: Execute the ETL pipeline locally
run:
	python -m src.main

## run-docker: Execute the ETL pipeline inside Docker
run-docker:
	docker-compose run --rm etl python -m src.main

## dbt-run: Run dbt models
dbt-run:
	cd dbt && dbt run --profiles-dir . --target dev

## dbt-test: Run dbt tests
dbt-test:
	cd dbt && dbt test --profiles-dir . --target dev

## clean: Remove Python cache and test artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	find . -type f -name '*.pyo' -delete
	rm -rf .pytest_cache htmlcov .coverage

## setup-env: Copy .env.example to .env
setup-env:
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env created from .env.example"; fi
