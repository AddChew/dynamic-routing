[![linting: pylint](https://github.com/AddChew/dynamic-routing/actions/workflows/pylint.yml/badge.svg)](https://github.com/AddChew/dynamic-routing/actions/workflows/pylint.yml/badge.svg)
[![Pytest](https://github.com/AddChew/dynamic-routing/actions/workflows/pytest.yml/badge.svg)](https://github.com/AddChew/dynamic-routing/actions/workflows/pytest.yml)

# Dynamic Routing

Application to add, edit or remove FastAPI endpoints dynamically at runtime without having to restart the application.

Built with:
* FastAPI
* Tortoise ORM
* PostgreSQL

## Motivation

## Demo

## How the app works

## Installation

#### Run via docker compose

#### Run locally

## Usage

## Limitations

## How to run tests

1. Navigate to the project root folder (i.e. dynamic-routing)

2. Create and activate conda environment
```shell
conda create -n dynamic-routing-tests python=3.10 -y
conda activate dynamic-routing-tests
```

3. Install the necessary dependencies
```shell
pip install -r deploy/src/requirements.txt
pip install pylint pytest coverage httpx
```

4. Run code quality checks
```shell
pylint $(git ls-files '*.py')
```

5. Run unittests
```shell
coverage run -m pytest -v
```

6. Run code coverage
```shell
coverage report -m
```
