#!/bin/bash

env_vars="ENV=docker
SECRET_KEY=$(openssl rand -hex 16)
POSTRES_DB=postgres
POSTGRES_HOST=postgres
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_USER=postgres"

echo -n "$env_vars" > deploy/.env
docker compose up -d --build