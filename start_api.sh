#!/usr/bin/env bash
# Script to start the Neo4j database and run the Python API server

set -e

echo "Starting Neo4j database..."
./start_neo4j.sh

echo "Waiting for Neo4j to be ready..."
sleep 5

echo "Starting Insecurity Refactoring API..."
cd "$(dirname "$0")"
python -m uvicorn insecurity_refactoring_py.api:app --host 0.0.0.0 --port 8000 --reload
