"""
Neo4j Database Connection Layer

This module provides the database interface for connecting to Neo4j
and executing Cypher queries for the insecurity refactoring tool.
"""

from typing import Any, Dict, List, Optional
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable
import logging

logger = logging.getLogger(__name__)


class Neo4jDB:
    """Neo4j database connector for insecurity refactoring"""
    
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "neo4j"):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j connection URI
            user: Database username
            password: Database password
        """
        self.uri = uri
        self.user = user
        self.password = password
        self._driver: Optional[Driver] = None
        
    def connect(self) -> bool:
        """
        Establish connection to Neo4j database.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connectivity
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at {self.uri}")
            return True
        except ServiceUnavailable as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to Neo4j: {e}")
            return False
    
    def close(self) -> None:
        """Close the database connection"""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed")
    
    def check_connection(self) -> bool:
        """
        Check if the database connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        if not self._driver:
            return False
        try:
            self._driver.verify_connectivity()
            return True
        except ServiceUnavailable:
            return False
    
    def execute_read(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a read query against Neo4j.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of record dictionaries
        """
        if not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        parameters = parameters or {}
        
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]
    
    def execute_write(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a write query against Neo4j.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of record dictionaries
        """
        if not self._driver:
            raise RuntimeError("Database not connected. Call connect() first.")
        
        parameters = parameters or {}
        
        with self._driver.session() as session:
            result = session.run(query, parameters)
            return [dict(record) for record in result]
    
    def find_node(self, node_id: int) -> Optional[Dict[str, Any]]:
        """
        Find a node by its ID.
        
        Args:
            node_id: The node ID to find
            
        Returns:
            Node data as dictionary or None if not found
        """
        query = "MATCH (n) WHERE id(n) = $node_id RETURN n"
        results = self.execute_read(query, {"node_id": node_id})
        return results[0] if results else None
    
    def find_nodes(self, label: Optional[str] = None, properties: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Find nodes by label and/or properties.
        
        Args:
            label: Optional node label to filter by
            properties: Optional properties to match
            
        Returns:
            List of matching nodes
        """
        if label:
            query = f"MATCH (n:{label})"
        else:
            query = "MATCH (n)"
        
        if properties:
            where_clauses = [f"n.{key} = ${key}" for key in properties.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
        
        query += " RETURN n"
        
        return self.execute_read(query, properties or {})
    
    def __enter__(self) -> "Neo4jDB":
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit"""
        self.close()
