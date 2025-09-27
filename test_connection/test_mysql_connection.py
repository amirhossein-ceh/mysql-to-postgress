#!/usr/bin/env python3
"""
Simple MySQL connection test script
Reads MySQL configuration from .env file and tests the connection
"""

import os
import sys
from dotenv import load_dotenv

def test_mysql_connection():
    """Test MySQL connection using configuration from .env file"""
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Get MySQL configuration from environment variables
    mysql_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DATABASE', '')
    }
    
    print("=" * 60)
    print("MySQL Connection Test")
    print("=" * 60)
    
    # Display configuration (without password)
    print("Configuration:")
    print(f"  Host: {mysql_config['host']}")
    print(f"  Port: {mysql_config['port']}")
    print(f"  User: {mysql_config['user']}")
    print(f"  Database: {mysql_config['database']}")
    print(f"  Password: {'***' if mysql_config['password'] else 'Not set'}")
    print()
    
    # Check if required fields are set
    if not mysql_config['database']:
        print("❌ Error: MYSQL_DATABASE not configured in .env file")
        return False
    
    if not mysql_config['password']:
        print("❌ Error: MYSQL_PASSWORD not configured in .env file")
        return False
    
    try:
        # Try to import mysql.connector
        import mysql.connector
        print("✅ mysql.connector module imported successfully")
        
    except ImportError:
        print("❌ Error: mysql.connector module not found")
        print("   Please install it with: pip install mysql-connector-python")
        return False
    
    try:
        print("🔍 Testing MySQL connection...")
        
        # Create connection
        conn = mysql.connector.connect(**mysql_config)
        print("✅ MySQL connection established successfully!")
        
        # Test basic queries
        cursor = conn.cursor()
        
        # Get MySQL version
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"📊 MySQL Version: {version[0]}")
        
        # Get database name
        cursor.execute("SELECT DATABASE()")
        current_db = cursor.fetchone()
        print(f"📊 Current Database: {current_db[0]}")
        
        # Get table count
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"📊 Tables found: {len(tables)}")
        
        if tables:
            print("📋 Table list:")
            for i, table in enumerate(tables[:10]):  # Show first 10 tables
                print(f"   {i+1}. {table[0]}")
            if len(tables) > 10:
                print(f"   ... and {len(tables) - 10} more tables")
        
        # Get database size
        cursor.execute("""
            SELECT 
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'DB Size in MB'
            FROM information_schema.tables 
            WHERE table_schema = %s
        """, (mysql_config['database'],))
        size_result = cursor.fetchone()
        if size_result and size_result[0]:
            print(f"📊 Database Size: {size_result[0]} MB")
        
        # Close connections
        cursor.close()
        conn.close()
        
        print("✅ Connection test completed successfully!")
        return True
        
    except mysql.connector.Error as e:
        print(f"❌ MySQL Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def main():
    """Main function"""
    try:
        success = test_mysql_connection()
        
        print()
        print("=" * 60)
        if success:
            print("🎉 MySQL connection test PASSED!")
            print("   Your MySQL database is accessible and ready for migration.")
        else:
            print("❌ MySQL connection test FAILED!")
            print("   Please check your .env configuration and MySQL server status.")
        print("=" * 60)
        
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Test failed with unexpected error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
