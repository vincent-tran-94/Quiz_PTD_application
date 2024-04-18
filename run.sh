#!/bin/bash

# Build the Docker image using the Dockerfile

docker-compose -f ../flask_app/ build

# Run the Docker container, passing in environment variables from .env file
docker-compose -f ../flask_app/ up
