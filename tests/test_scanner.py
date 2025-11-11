"""
Unit tests for the vulnerability scanner
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from insecurity_refactoring_py.scanner import VulnerabilityScanner
from insecurity_refactoring_py.db import Neo4jDB


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock(spec=Neo4jDB)
    return db


def test_scanner_init(mock_db):
    """Test scanner initialization"""
    scanner = VulnerabilityScanner(mock_db)
    assert scanner.db == mock_db
    assert scanner.patterns == {}


def test_prepare_database(mock_db):
    """Test database preparation"""
    scanner = VulnerabilityScanner(mock_db)
    result = scanner.prepare_database("/path/to/code")
    
    # Currently returns True as it's not implemented
    assert result is True


def test_scan_basic(mock_db):
    """Test basic scanning functionality"""
    mock_db.execute_read.return_value = [
        {'n': {'code': 'echo $user_input', 'location': 'test.php:10'}}
    ]
    
    scanner = VulnerabilityScanner(mock_db)
    results = scanner.scan("/path/to/code")
    
    assert isinstance(results, list)
    mock_db.execute_read.assert_called()


def test_find_injection_points(mock_db):
    """Test finding injection points"""
    mock_db.execute_read.return_value = [
        {'n': {'code': 'eval($input)', 'type': 'AST_CALL'}},
        {'n': {'code': 'system($cmd)', 'type': 'AST_CALL'}}
    ]
    
    scanner = VulnerabilityScanner(mock_db)
    pips = scanner._find_injection_points()
    
    assert len(pips) == 2
    assert any('eval' in str(pip) for pip in pips)


def test_analyze_injection_point_eval(mock_db):
    """Test analyzing eval injection point"""
    scanner = VulnerabilityScanner(mock_db)
    
    pip = {'n': {'code': 'eval($input)', 'location': 'test.php:10'}}
    result = scanner._analyze_injection_point(pip)
    
    assert result is not None
    assert result['type'] == 'Code Injection'
    assert result['severity'] == 'High'


def test_analyze_injection_point_system(mock_db):
    """Test analyzing system command injection point"""
    scanner = VulnerabilityScanner(mock_db)
    
    pip = {'n': {'code': 'system($cmd)', 'location': 'test.php:20'}}
    result = scanner._analyze_injection_point(pip)
    
    assert result is not None
    assert result['type'] == 'Command Injection'


def test_analyze_injection_point_xss(mock_db):
    """Test analyzing XSS injection point"""
    scanner = VulnerabilityScanner(mock_db)
    
    pip = {'n': {'code': 'echo $input', 'location': 'test.php:30'}}
    result = scanner._analyze_injection_point(pip)
    
    assert result is not None
    assert result['type'] == 'XSS'


def test_analyze_empty_pip(mock_db):
    """Test analyzing empty injection point"""
    scanner = VulnerabilityScanner(mock_db)
    
    pip = {'n': {}}
    result = scanner._analyze_injection_point(pip)
    
    assert result is None
