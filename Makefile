# Dating Profile Optimizer - Makefile

.PHONY: help install test test-coverage clean run setup

help:
	@echo "Dating Profile Optimizer - Available Commands:"
	@echo ""
	@echo "  setup          - Install all dependencies"
	@echo "  run            - Run the application"
	@echo "  test           - Run all tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  clean          - Clean up generated files"
	@echo "  install        - Install package in development mode"
	@echo ""

setup:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Setup complete!"

install:
	@echo "Installing package in development mode..."
	pip install -e .
	@echo "Installation complete!"

run:
	@echo "Starting Dating Profile Optimizer..."
	python main.py

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

test-coverage:
	@echo "Running tests with coverage..."
	python -m pytest tests/ --cov=src --cov-report=html --cov-report=term-missing -v
	@echo "Coverage report generated in htmlcov/"

test-simple:
	@echo "Running tests with simple runner..."
	python run_tests.py

clean:
	@echo "Cleaning up..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Cleanup complete!"

# Development helpers
dev-setup: setup
	@echo "Installing development dependencies..."
	pip install pytest pytest-cov black flake8
	@echo "Development setup complete!"

format:
	@echo "Formatting code..."
	black src/ tests/ *.py

lint:
	@echo "Linting code..."
	flake8 src/ tests/ *.py --max-line-length=100 --ignore=E203,W503