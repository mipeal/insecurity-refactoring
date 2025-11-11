# Insecurity Refactoring - Python Implementation

A modern Python implementation of the Insecurity Refactoring tool with enhanced Neo4j integration, providing both CLI and API interfaces for detecting security vulnerabilities in PHP code.

## Features

- 🔍 **Security Vulnerability Detection**: Scan PHP code for common security issues
- 🗄️ **Neo4j Integration**: Leverage graph database for code property graph analysis
- 🖥️ **CLI Interface**: Command-line tool built with Typer
- 🌐 **REST API**: FastAPI-based API for programmatic access
- 🐍 **Modern Python**: Built with Python 3.10+ and modern libraries

## Installation

### Prerequisites

- Python 3.10 or higher
- Neo4j 5.x+ (running locally or accessible via network)
- Java 11+ (for phpjoern/joern integration)

### Install Package

```bash
# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

## Configuration

Create a `.env` file in the project root:

```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
LOG_LEVEL=INFO
```

## Usage

### Command Line Interface

```bash
# Test Neo4j connection
insecurity-cli connect-test

# Scan a path for vulnerabilities
insecurity-cli scan /path/to/php/code

# Scan with options
insecurity-cli scan /path/to/php/code --output --verbose

# Scan without preparing database (use existing CPG)
insecurity-cli scan /path/to/php/code --no-prepare

# Show version
insecurity-cli version
```

### REST API

Start the API server:

```bash
# Using uvicorn directly
uvicorn insecurity_refactoring_py.api:app --reload

# Or run the api module
python -m insecurity_refactoring_py.api
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

#### API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check and database status
- `POST /scan` - Scan a path for vulnerabilities
- `GET /patterns` - List available vulnerability patterns
- `GET /nodes/{node_id}` - Get a specific node from the CPG

Example API request:

```bash
curl -X POST "http://localhost:8000/scan" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/php/code",
    "prepare_db": true,
    "specific_patterns": null
  }'
```

## Architecture

The Python implementation provides:

1. **Database Layer** (`db.py`): Neo4j connection and query execution
2. **Scanner** (`scanner.py`): Vulnerability detection logic
3. **CLI** (`cli.py`): Command-line interface using Typer
4. **API** (`api.py`): REST API using FastAPI
5. **Configuration** (`config.py`): Settings management with Pydantic

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black insecurity_refactoring_py/

# Lint code
ruff check insecurity_refactoring_py/

# Type checking
mypy insecurity_refactoring_py/
```

## Migration from Java

This Python implementation provides a modern alternative to the original Java application while maintaining compatibility with the Neo4j code property graph structure. Key improvements:

- **Simpler deployment**: No Maven/JDK required for the analysis tool
- **Modern API**: RESTful API with OpenAPI documentation
- **Better CLI**: Rich terminal output with Typer
- **Easier integration**: Python ecosystem compatibility

The Java components (phpjoern, joern) are still used for creating the initial code property graph, but all analysis and querying is done in Python.

## License

See LICENSE file for details.
