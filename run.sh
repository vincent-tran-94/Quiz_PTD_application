#!/bin/bash

# Build the Docker image using the Dockerfile
docker build -t application-ptdlegalquizz-parser .

# Run the Docker container, passing in environment variables from .env file
docker run --env-file .env -p 9400:9400 application-ptdlegalquizz-parser