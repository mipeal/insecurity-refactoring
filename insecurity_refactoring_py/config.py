"""
Configuration module for Insecurity Refactoring

Handles configuration settings and environment variables.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )
    
    # Neo4j settings
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neo4j"
    
    # Application settings
    pattern_folder: Path = Path("InsecurityRefactoring/src/main/non-packaged-resources/patterns")
    
    # Logging
    log_level: str = "INFO"

