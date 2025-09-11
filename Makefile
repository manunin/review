# Makefile for running tests and development tasks

.PHONY: help test test-unit test-integration test-performance test-security test-health test-coverage test-quick clean install lint format check

# Default target
help:
	@echo "Available targets:"
	@echo "  install          - Install dependencies"
	@echo "  test             - Run all tests"
	@echo "  test-unit        - Run unit tests only"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-security    - Run security tests only"
	@echo "  test-health      - Run health check tests only"
	@echo "  test-coverage    - Run tests with coverage report"
	@echo "  test-quick       - Run quick tests (exclude slow tests)"
	@echo "  lint             - Run linting"
	@echo "  format           - Format code"
	@echo "  check            - Run all checks (lint, format, tests)"
	@echo "  clean            - Clean temporary files"

# Install dependencies
install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

# Run all tests
test:
	python -m pytest tests/ -v

# Run unit tests only
test-unit:
	python -m pytest tests/ -m "not integration" -v

# Run integration tests only
test-integration:
	python -m pytest tests/integration/ -v

# Run performance tests
test-performance:
	python -m pytest tests/integration/test_performance.py -v

# Run security tests
test-security:
	python -m pytest tests/integration/test_security.py -v

# Run health check tests
test-health:
	python -m pytest tests/integration/test_health.py -v

# Run tests with coverage
test-coverage:
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term-missing

# Run quick tests (exclude slow tests)
test-quick:
	python -m pytest tests/ -m "not slow" -v

# Run specific test file
test-file:
	@echo "Usage: make test-file FILE=tests/integration/test_openapi_compliance.py"
	@if [ -n "$(FILE)" ]; then \
		python -m pytest $(FILE) -v; \
	fi

# Run specific test
test-case:
	@echo "Usage: make test-case CASE=test_single_task_creation_and_result"
	@if [ -n "$(CASE)" ]; then \
		python -m pytest tests/ -k "$(CASE)" -v; \
	fi

# Linting
lint:
	@echo "Running linting..."
	@python -m flake8 app/ tests/ --max-line-length=100
	@python -m mypy app/ --ignore-missing-imports

# Format code
format:
	@echo "Formatting code..."
	@python -m black app/ tests/
	@python -m isort app/ tests/

# Run all checks
check: lint test

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type d -name "*.egg-info" -exec rm -rf {} +
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf coverage.xml
	@rm -rf .mypy_cache/

# Development server
dev:
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests with docker compose (if you have docker setup)
test-docker:
	docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# Generate test report
test-report:
	python -m pytest tests/ --html=report.html --self-contained-html

# Run tests in parallel (if pytest-xdist is installed)
test-parallel:
	python -m pytest tests/ -n auto -v

# Debug specific test
test-debug:
	@echo "Usage: make test-debug CASE=test_single_task_creation_and_result"
	@if [ -n "$(CASE)" ]; then \
		python -m pytest tests/ -k "$(CASE)" -v -s --pdb; \
	fi

# Run load testing
load-test:
	@echo "Running load tests..."
	python -m pytest tests/integration/test_performance.py::TestPerformanceAndLoad -v

# Verify OpenAPI compliance
verify-openapi:
	python -m pytest tests/integration/test_openapi_compliance.py -v

# Check test coverage for specific module
coverage-module:
	@echo "Usage: make coverage-module MODULE=app.tasks.service"
	@if [ -n "$(MODULE)" ]; then \
		python -m pytest tests/ --cov=$(MODULE) --cov-report=term-missing; \
	fi
