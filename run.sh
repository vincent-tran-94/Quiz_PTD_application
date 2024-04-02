#!/bin/bash

# Build the Docker image using the Dockerfile
docker build -t application-ptdlegalquizz-parser .

# Run the Docker container, passing in environment variables from .env file
docker run -p 5000:5000 application-ptdlegalquizz-parser
