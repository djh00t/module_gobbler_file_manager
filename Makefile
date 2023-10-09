# Makefile for klingon-file-manager Python package

# Variables
APP_NAME = "klingon-file-manager"
TWINE_USERNAME ?= __token__
TEST_TWINE_PASSWORD ?= $(TEST_PYPI_USER_AGENT)
PYPI_TWINE_PASSWORD ?= $(PYPI_USER_AGENT)

# Clean up build files
clean:
	rm -rf build dist *.egg-info .mypy_cache .pytest_cache */__pycache__

## check-packages: Check for required pip packages and requirements.txt, install if missing
check-packages:
	@echo "Checking for required pip packages and requirements.txt..."
	@if [ ! -f requirements.txt ]; then \
		echo "requirements.txt not found. Please add it to the project root."; \
		exit 1; \
	fi
	@echo "Installing missing packages from requirements.txt..."
	@pip install -r requirements.txt
	@echo "Installing twine and wheel..."
	@pip install twine wheel

## sdist: Create a source distribution package
sdist: clean
	python setup.py sdist

## wheel: Create a wheel distribution package
wheel: clean
	python setup.py sdist bdist_wheel

## upload-test: Run tests, if they pass update version number, echo it to console and upload the distribution package to TestPyPI
upload-test: test wheel
	@echo "Uploading Version $$NEW_VERSION to TestPyPI..."
	twine upload --repository-url https://test.pypi.org/legacy/ --username $(TWINE_USERNAME) --password $(TEST_TWINE_PASSWORD) dist/*

## upload: Run tests, if they pass update version number and upload the distribution package to PyPI
upload: test wheel
	@echo "Uploading Version $$NEW_VERSION to PyPI..."
	twine upload --username $(TWINE_USERNAME) --password $(PYPI_TWINE_PASSWORD) dist/*

## install: Install the package locally
install:
	pip install -e .

## install-pip: Install the package locally using pip
install-pip:
	pip install $(APP_NAME)

## install-pip-test: Install the package locally using pip from TestPyPI
install-pip-test:
	pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple $(APP_NAME)

## uninstall: Uninstall the local package
uninstall:
	pip uninstall $(APP_NAME)

# Run tests
test:
	@echo "Running unit tests..."
	pytest tests


## update-version: Read the version number from VERSION file, it will look like A.B.C Increment the third (C) number by 1 and write it back to the VERSION file
update-version:
	@echo "Updating version number..."
	@NEW_VERSION=$$(awk -F. '{print $$1"."$$2"."$$3+1}' VERSION); \
	echo $$NEW_VERSION > VERSION; \
	sed -i '' "s/version='[0-9]*\.[0-9]*\.[0-9]*'/version='$$NEW_VERSION'/g" setup.py; \
	echo "New version number is $$NEW_VERSION"

## generate-pyproject: Generate a pyproject.toml file
generate-pyproject:
	@echo "[build-system]" > pyproject.toml
	@echo "requires = ['setuptools', 'wheel']" >> pyproject.toml
	@echo "build-backend = 'setuptools.build_meta'" >> pyproject.toml

.PHONY: clean check-packages sdist wheel upload-test upload install uninstall test update-version generate-pyproject
