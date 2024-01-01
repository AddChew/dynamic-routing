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

Each uploaded script functions as an independent sub application, with its own authorization method and Swagger UI, mounted onto the main application at the path /{username}/{project_name}.

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

1. From project root folder (i.e. dynamic-routing), run the following command:
```
./local_setup.sh
```

2. Navigate to the following urls to access the respective services:

| URL                              | Service       |
| -------------------------------- |-------------- |
| http://localhost:8000/docs       | SwaggerUI     |
| http://localhost:8000/redoc      | Redoc         |

## Usage

## Limitations

#### Shared conda environment

Each sub application can only use libraries that are installed in the shared conda environment. This could be resolved by building the main application with [Ray Serve](https://docs.ray.io/en/latest/ray-core/handling-dependencies.html), which supports independent runtime environments per serve deployment.

#### Single app file

All of the logic of a sub application has to be confined within one file (i.e. app.py). In most cases, this should suffice, given that each sub application only hosts mock APIs with simple logic.

#### Fixed variable name for FastAPI app

The FastAPI app variable in each sub application has to be named "app" (i.e. app = FastAPI()).

## How to run tests

From project root folder (i.e. dynamic-routing), execute the following command:
```shell
./run_tests.sh
```