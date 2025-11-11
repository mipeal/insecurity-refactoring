## Folder structure

 - sca_patterns_master: I addded simple test, currently the most simple one that fails is test01.php
 - phpjoern-master
 - joern
 - neo4j-community-3.5.13


# Prerequisites


I'm currently using Manjaro, but I have also tried step-by-step installation in a virtual machine with Ubuntu, that's why some packages will be either for Ubuntu or Manjaro. First we need to install:

 - Python (version used: 3.8.1)
 - Java JDK 11
 - Maven
 - php (version used:  PHP 7.4.2 (cli) (built: Jan 21 2020 18:16:58) ( NTS ))
 - php-dev
 - curl
 - Install php-ast (see section php-ast)
 - Install joern + requirements (see section joern)

## php-ast


Now we install the extension following all steps found [here](https://github.com/malteskoruppa/phpjoern#prerequisite-installing-the-php-ast-extension), which are:
```
git clone https://github.com/nikic/php-ast
cd php-ast
phpize
./configure
make
sudo make install
```

Lastly, add the line  `extension=ast.so`  to your  `php.ini`  file. (Ubuntu php7.4 -> /etc/php/7.4/cli/php.ini)

## joern

Latest version of Joern **that had php support**. First we need to install all of the necessary libraries:

1. Install Gradle (4.10.3)
Recommended: install Gradle with [SDK Man](https://sdkman.io/):
```
curl -s "https://get.sdkman.io" | bash
```
Open a new terminal
```
sdk install gradle 4.10.3
```

2. Install graphviz and required python tools
```
sudo apt-get install python3-distutils python3-pip python3-setuptools
pip3 install graphviz
sudo apt-get install libgraphviz-dev pkg-config
```

## Compile joern / joernphp
As last step joern and joernphp are compiled using following command in the base folder of this project:
```
./compile_all
```

# Insecurity Refactoring
The project itself is found in the directory: `{ProjectFolder}/InsecurityRefactoring`

## Compile

It can be compile with following commands:
```
cd InsecurityRefactoring
mvn package
```
## Run the project
A simple script is added to run the project
```
sh run_insec.sh -g
```
The -g parameter starts the user interface.
You can use it from cli to find possible injection points/vulnerabilities. Further information can be found by the -h parameter


# Neo4j 
The code property graph is stored in the provided neo4j database. You can access the database for testing on following url:
http://localhost:7474/

# Python Application (NEW)

A modern Python implementation of the Insecurity Refactoring tool is now available with enhanced Neo4j integration!

## Quick Start with Python

### Prerequisites
- Python 3.10 or higher
- Neo4j 5.x+ (the existing neo4j-community-3.5.13 can still be used)

### Installation

```bash
# Install Python dependencies
pip install -r requirements.txt

# Or install in development mode
pip install -e .
```

### Configuration

Create a `.env` file (use `.env.example` as template):
```bash
cp .env.example .env
# Edit .env with your Neo4j credentials if needed
```

### Usage

#### Command Line Interface (CLI)

```bash
# Test Neo4j connection
insecurity-cli connect-test

# Scan for vulnerabilities
insecurity-cli scan /path/to/php/code

# Scan with verbose output
insecurity-cli scan /path/to/php/code --output --verbose

# Show version
insecurity-cli version
```

#### REST API

Start the API server:
```bash
# Option 1: Using the provided script
./start_api.sh

# Option 2: Directly with uvicorn
uvicorn insecurity_refactoring_py.api:app --reload
```

Access the API:
- API Root: http://localhost:8000/
- Interactive Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

#### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=insecurity_refactoring_py

# Run specific test file
pytest tests/test_db.py -v
```

## Python Application Features

- 🐍 **Modern Python Stack**: Built with Python 3.10+ and type hints
- 🔌 **Enhanced Neo4j Integration**: Using the latest neo4j-driver (5.x)
- 🖥️ **CLI with Typer**: Rich terminal interface with beautiful output
- 🌐 **FastAPI REST API**: OpenAPI/Swagger documentation included
- ✅ **Well Tested**: Comprehensive test suite with pytest
- 📦 **Easy Deployment**: Simple pip installation

## Architecture

The Python application provides:
- `insecurity_refactoring_py/db.py` - Neo4j database layer
- `insecurity_refactoring_py/scanner.py` - Vulnerability detection engine
- `insecurity_refactoring_py/cli.py` - Command-line interface
- `insecurity_refactoring_py/api.py` - REST API
- `insecurity_refactoring_py/config.py` - Configuration management

See `insecurity_refactoring_py/README.md` for detailed documentation.


