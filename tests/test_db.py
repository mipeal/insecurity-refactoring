"""
Unit tests for the Neo4j database layer
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from insecurity_refactoring_py.db import Neo4jDB


def test_neo4j_db_init():
    """Test Neo4jDB initialization"""
    db = Neo4jDB(uri="bolt://localhost:7687", user="test", password="test")
    assert db.uri == "bolt://localhost:7687"
    assert db.user == "test"
    assert db.password == "test"
    assert db._driver is None


def test_neo4j_db_connect_success():
    """Test successful database connection"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        mock_driver = Mock()
        mock_gdb.driver.return_value = mock_driver
        
        db = Neo4jDB()
        result = db.connect()
        
        assert result is True
        mock_gdb.driver.assert_called_once()
        mock_driver.verify_connectivity.assert_called_once()


def test_neo4j_db_connect_failure():
    """Test failed database connection"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        from neo4j.exceptions import ServiceUnavailable
        mock_gdb.driver.return_value.verify_connectivity.side_effect = ServiceUnavailable("Test error")
        
        db = Neo4jDB()
        result = db.connect()
        
        assert result is False


def test_neo4j_db_close():
    """Test closing database connection"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        mock_driver = Mock()
        mock_gdb.driver.return_value = mock_driver
        
        db = Neo4jDB()
        db.connect()
        db.close()
        
        mock_driver.close.assert_called_once()


def test_neo4j_db_context_manager():
    """Test Neo4jDB as context manager"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        mock_driver = Mock()
        mock_gdb.driver.return_value = mock_driver
        
        with Neo4jDB() as db:
            assert db is not None
        
        mock_driver.close.assert_called_once()


def test_execute_read():
    """Test executing a read query"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        mock_driver = Mock()
        mock_session = MagicMock()
        mock_result = Mock()
        
        # Setup mocks - session needs to be a MagicMock for context manager
        mock_gdb.driver.return_value = mock_driver
        mock_driver.session = MagicMock(return_value=mock_session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.run.return_value = mock_result
        
        # Create mock records
        mock_record = {'name': 'test', 'value': 123}
        mock_result.__iter__ = Mock(return_value=iter([mock_record]))
        
        db = Neo4jDB()
        db.connect()
        
        results = db.execute_read("MATCH (n) RETURN n")
        
        assert len(results) > 0
        mock_session.run.assert_called_once()


def test_find_node():
    """Test finding a node by ID"""
    with patch('insecurity_refactoring_py.db.GraphDatabase') as mock_gdb:
        mock_driver = Mock()
        mock_session = MagicMock()
        mock_result = Mock()
        
        mock_gdb.driver.return_value = mock_driver
        mock_driver.session = MagicMock(return_value=mock_session)
        mock_session.__enter__ = MagicMock(return_value=mock_session)
        mock_session.__exit__ = MagicMock(return_value=False)
        mock_session.run.return_value = mock_result
        
        mock_record = {'n': {'id': 123, 'name': 'test'}}
        mock_result.__iter__ = Mock(return_value=iter([mock_record]))
        
        db = Neo4jDB()
        db.connect()
        
        node = db.find_node(123)
        
        assert node is not None
        mock_session.run.assert_called_once()
