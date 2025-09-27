#!/usr/bin/env python3
"""
Debug script to test database connections and identify issues
Run this script to test your database configuration before starting migration
"""

import os
import sys
from dotenv import load_dotenv
from database_manager import DatabaseManager

def test_database_connections():
    """Test database connections and provide detailed feedback"""
    print("🔍 Database Connection Debug Tool")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Get database configuration
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', '')
    }
    
    postgres_config = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', 5432)),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
        'database': os.getenv('POSTGRES_DATABASE', '')
    }
    
    print("📋 Configuration Check:")
    print(f"MySQL Host: {mysql_config['host']}:{mysql_config['port']}")
    print(f"MySQL User: {mysql_config['user']}")
    print(f"MySQL Database: {mysql_config['database'] or 'NOT SET'}")
    print(f"MySQL Password: {'SET' if mysql_config['password'] else 'NOT SET'}")
    print()
    print(f"PostgreSQL Host: {postgres_config['host']}:{postgres_config['port']}")
    print(f"PostgreSQL User: {postgres_config['user']}")
    print(f"PostgreSQL Database: {postgres_config['database'] or 'NOT SET'}")
    print(f"PostgreSQL Password: {'SET' if postgres_config['password'] else 'NOT SET'}")
    print()
    
    # Check for missing configuration
    missing_config = []
    if not mysql_config['database']:
        missing_config.append("MYSQL_DATABASE")
    if not mysql_config['password']:
        missing_config.append("MYSQL_PASSWORD")
    if not postgres_config['database']:
        missing_config.append("POSTGRES_DATABASE")
    if not postgres_config['password']:
        missing_config.append("POSTGRES_PASSWORD")
    
    if missing_config:
        print("❌ Missing Configuration:")
        for config in missing_config:
            print(f"   - {config}")
        print()
        print("💡 Solution: Create a .env file with the missing configuration.")
        print("   Copy config_template.txt to .env and update with your database credentials.")
        return False
    
    # Test connections
    db_manager = DatabaseManager()
    
    print("🔌 Testing MySQL Connection...")
    try:
        mysql_conn = db_manager.create_mysql_connection(mysql_config)
        print("✅ MySQL connection successful!")
        
        # Test table listing
        tables = db_manager.get_mysql_tables(mysql_conn)
        print(f"📊 Found {len(tables)} tables in MySQL database")
        if tables:
            print(f"   Sample tables: {', '.join(tables[:3])}{'...' if len(tables) > 3 else ''}")
        
        mysql_conn.close()
        print("🔌 MySQL connection closed")
        
    except Exception as e:
        print(f"❌ MySQL connection failed: {e}")
        print("💡 Common solutions:")
        print("   - Check if MySQL server is running")
        print("   - Verify host, port, username, and password")
        print("   - Ensure the database exists")
        print("   - Check firewall settings")
        return False
    
    print()
    print("🔌 Testing PostgreSQL Connection...")
    try:
        postgres_conn = db_manager.create_postgres_connection(postgres_config)
        print("✅ PostgreSQL connection successful!")
        
        # Test table listing
        cursor = postgres_conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables_count = cursor.fetchone()[0]
        cursor.close()
        print(f"📊 Found {tables_count} tables in PostgreSQL database")
        
        postgres_conn.close()
        print("🔌 PostgreSQL connection closed")
        
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("💡 Common solutions:")
        print("   - Check if PostgreSQL server is running")
        print("   - Verify host, port, username, and password")
        print("   - Ensure the database exists")
        print("   - Check firewall settings")
        return False
    
    print()
    print("🎉 All database connections successful!")
    print("✅ You can now start the migration process.")
    return True

if __name__ == "__main__":
    success = test_database_connections()
    sys.exit(0 if success else 1)
