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

1. Set POSTGRES_PASSWORD environment variable
```shell
export POSTGRES_PASSWORD=<your postgres password>
```

2. From project root folder (i.e. dynamic-routing), run the following command:
```
./docker_setup.sh
```

3. Navigate to the following urls to access the respective services:

| URL                              | Service       |
| -------------------------------- |-------------- |
| http://localhost:8000/docs       | SwaggerUI     |
| http://localhost:8000/redoc      | Redoc         |

#### Run locally

## Usage

## Limitations

## How to run tests

From project root folder (i.e. dynamic-routing), execute the following command:
```shell
./run_tests.sh
```