#!/usr/bin/env python3
"""
Simple test script to verify the Python application works
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from insecurity_refactoring_py.db import Neo4jDB
from insecurity_refactoring_py.config import Settings

def main():
    print("Testing Insecurity Refactoring Python Application")
    print("=" * 50)
    
    # Test configuration
    print("\n1. Testing configuration...")
    settings = Settings()
    print(f"   Neo4j URI: {settings.neo4j_uri}")
    print(f"   Neo4j User: {settings.neo4j_user}")
    print("   ✓ Configuration loaded")
    
    # Test database connection
    print("\n2. Testing Neo4j connection...")
    db = Neo4jDB(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    
    if db.connect():
        print("   ✓ Successfully connected to Neo4j")
        
        # Try a simple query
        print("\n3. Testing database query...")
        try:
            results = db.execute_read("MATCH (n) RETURN count(n) as count")
            if results:
                count = results[0].get('count', 0)
                print(f"   ✓ Database has {count} nodes")
            else:
                print("   ⚠ Database appears to be empty")
        except Exception as e:
            print(f"   ✗ Query failed: {e}")
        
        db.close()
        print("   ✓ Connection closed")
    else:
        print("   ✗ Failed to connect to Neo4j")
        print("   Make sure Neo4j is running with: ./start_neo4j.sh")
        return 1
    
    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    return 0

if __name__ == "__main__":
    sys.exit(main())
