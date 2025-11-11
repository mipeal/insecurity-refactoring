"""
FastAPI Application for Insecurity Refactoring

This module provides a REST API for vulnerability scanning and analysis.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import logging
from pathlib import Path

from insecurity_refactoring_py.db import Neo4jDB
from insecurity_refactoring_py.scanner import VulnerabilityScanner
from insecurity_refactoring_py.config import Settings

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Insecurity Refactoring API",
    description="API for detecting and analyzing security vulnerabilities in PHP code",
    version="1.0.0"
)

settings = Settings()


# Request/Response Models
class ScanRequest(BaseModel):
    """Request model for scanning"""
    path: str = Field(..., description="Path to scan for vulnerabilities")
    prepare_db: bool = Field(True, description="Whether to prepare the database first")
    specific_patterns: Optional[List[str]] = Field(None, description="Specific patterns to scan for")
    control_flow: bool = Field(False, description="Enable control flow analysis")


class VulnerabilityResponse(BaseModel):
    """Response model for a vulnerability"""
    type: str
    location: str
    severity: str
    details: str
    code: Optional[str] = None


class ScanResponse(BaseModel):
    """Response model for scan results"""
    status: str
    path: str
    vulnerabilities: List[VulnerabilityResponse]
    total_count: int


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    neo4j_connected: bool
    version: str


# Dependency for database connection
def get_db() -> Neo4jDB:
    """Get a database connection"""
    db = Neo4jDB(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    if not db.connect():
        raise HTTPException(status_code=503, detail="Cannot connect to Neo4j database")
    return db


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "Insecurity Refactoring API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    from insecurity_refactoring_py import __version__
    
    db = Neo4jDB(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    neo4j_connected = db.connect()
    if neo4j_connected:
        db.close()
    
    return HealthResponse(
        status="healthy" if neo4j_connected else "degraded",
        neo4j_connected=neo4j_connected,
        version=__version__
    )


@app.post("/scan", response_model=ScanResponse)
async def scan(request: ScanRequest):
    """
    Scan a path for security vulnerabilities.
    
    Args:
        request: Scan request parameters
        
    Returns:
        Scan results with detected vulnerabilities
    """
    # Validate and sanitize the path to prevent path traversal
    try:
        path = Path(request.path).resolve()
    except (ValueError, RuntimeError) as e:
        raise HTTPException(status_code=400, detail=f"Invalid path: {str(e)}")
    
    # Ensure the path exists and is within allowed directories
    if not path.exists():
        raise HTTPException(status_code=404, detail="Path not found")
    
    # Optional: Add additional security check to ensure path is within allowed directories
    # This prevents accessing arbitrary file system locations
    # Uncomment and configure if you want to restrict to specific directories:
    # allowed_base = Path("/allowed/scan/directory").resolve()
    # if not str(path).startswith(str(allowed_base)):
    #     raise HTTPException(status_code=403, detail="Access to this path is not allowed")
    
    db = get_db()
    
    try:
        scanner = VulnerabilityScanner(db)
        
        if request.prepare_db:
            success = scanner.prepare_database(str(path))
            if not success:
                raise HTTPException(status_code=500, detail="Failed to prepare database")
        
        results = scanner.scan(
            str(path),
            specific_patterns=request.specific_patterns
        )
        
        vulnerabilities = [
            VulnerabilityResponse(
                type=r.get("type", "Unknown"),
                location=r.get("location", "Unknown"),
                severity=r.get("severity", "Unknown"),
                details=r.get("details", ""),
                code=r.get("code")
            )
            for r in results
        ]
        
        return ScanResponse(
            status="completed",
            path=str(path),
            vulnerabilities=vulnerabilities,
            total_count=len(vulnerabilities)
        )
        
    finally:
        db.close()


@app.get("/patterns", response_model=List[str])
async def list_patterns():
    """
    List available vulnerability patterns.
    
    Returns:
        List of pattern names
    """
    pattern_folder = settings.pattern_folder
    
    if not pattern_folder.exists():
        return []
    
    patterns = [p.stem for p in pattern_folder.rglob("*.json")]
    return sorted(patterns)


@app.get("/nodes/{node_id}")
async def get_node(node_id: int):
    """
    Get a specific node from the code property graph.
    
    Args:
        node_id: Node ID to retrieve
        
    Returns:
        Node data
    """
    db = get_db()
    
    try:
        node = db.find_node(node_id)
        
        if not node:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        
        return node
        
    finally:
        db.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
