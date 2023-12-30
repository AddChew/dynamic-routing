[![linting: pylint](https://github.com/AddChew/dynamic-routing/actions/workflows/pylint.yml/badge.svg)](https://github.com/AddChew/dynamic-routing/actions/workflows/pylint.yml/badge.svg)
[![Pytest](https://github.com/AddChew/dynamic-routing/actions/workflows/pytest.yml/badge.svg)](https://github.com/AddChew/dynamic-routing/actions/workflows/pytest.yml)

# Dynamic Routing

Application to add, edit or remove FastAPI endpoints dynamically at runtime without having to restart the application.

Built with:
* FastAPI
* Tortoise ORM
* PostgreSQL

## Context

## Project setup

## How to run tests

1. Navigate to the project root folder (i.e. dynamic-routing)

2. Install the necessary dependencies
```shell
pip install -r deploy/src/requirements.txt
pip install pylint pytest coverage httpx
```

3. Run code quality checks
```shell
pylint $(git ls-files '*.py')
```

4. Run unittests
```shell
coverage run -m pytest -v
```

5. Run code coverage
```shell
coverage report -m
```
