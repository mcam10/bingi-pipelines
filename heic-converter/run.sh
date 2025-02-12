#!/bin/bash

# Default values
QUALITY=${QUALITY:-50}
WORKERS=${WORKERS:-4}
INPUT_DIR=${INPUT_DIR:-$(pwd)/data}

# Create data directory if it doesn't exist
mkdir -p "$INPUT_DIR"

# Build and run the container
docker-compose up --build
