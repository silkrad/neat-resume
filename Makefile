.PHONY: all build format lint test clean

all: format lint test build

build:
	@echo "Building Python package..."
	@ORIGINAL_VERSION=$$(grep '^__version__ = ' src/neatresume/__about__.py | cut -d'"' -f2); \
	GIT_TAG=$$(git describe --tags --exact-match 2>/dev/null || echo ""); \
	if [ -n "$$GIT_TAG" ] && echo "$$GIT_TAG" | grep -E "^[0-9]+\.[0-9]+\.[0-9]+$$" > /dev/null; then \
		echo "Using semantic version tag: $$GIT_TAG"; \
		sed -i "s/^__version__ = .*/__version__ = \"$$GIT_TAG\"/" src/neatresume/__about__.py; \
	else \
		SHORT_SHA=$$(git rev-parse --short HEAD); \
		SHA_INT=$$(printf "%d" 0x$$SHORT_SHA); \
		echo "Using SHA-based version: $$ORIGINAL_VERSION-$$SHA_INT"; \
		sed -i "s/^__version__ = .*/__version__ = \"$$ORIGINAL_VERSION-$$SHA_INT\"/" src/neatresume/__about__.py; \
	fi; \
	trap 'git checkout -- src/neatresume/__about__.py' EXIT; \
	hatch clean; \
	hatch build; \
	echo "Package built successfully. Artifacts in dist/"

format:
	@echo "Running code formatters..."
	hatch fmt

lint:
	@echo "Running linters..."
	hatch fmt --check
	hatch run types:check

test:
	@echo "Running tests..."
	hatch test || [ $$? -eq 5 ] || exit $$?

clean:
	@echo "Cleaning build artifacts..."
	hatch clean
	rm -rf build/
	rm -rf dist/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name htmlcov -exec rm -rf {} +
	find . -type d -name .coverage -exec rm -rf {} +
	find . -type d -name .egg-info -exec rm -rf {} +
	find . -type d -name .mypy_cache -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -type d -name .ruff_cache -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pdf" -delete
	@echo "Restoring original version from git..."
	git checkout -- src/neatresume/__about__.py
