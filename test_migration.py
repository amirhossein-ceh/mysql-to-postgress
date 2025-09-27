#!/usr/bin/env python3
"""
Simple test script to isolate the migration issue
"""

import os
import sys
from dotenv import load_dotenv
from database_manager import DatabaseManager

def test_migration_steps():
    """Test each step of the migration process"""
    print("🔍 Testing Migration Steps")
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
    
    db_manager = DatabaseManager()
    
    try:
        # Step 1: Connect to MySQL
        print("Step 1: Connecting to MySQL...")
        mysql_conn = db_manager.connect_mysql(mysql_config)
        print("✅ MySQL connection successful")
        
        # Step 2: Get tables
        print("Step 2: Getting table list...")
        tables = db_manager.get_mysql_tables(mysql_conn)
        print(f"✅ Found {len(tables)} tables: {tables}")
        
        # Step 3: Connect to PostgreSQL
        print("Step 3: Connecting to PostgreSQL...")
        postgres_conn = db_manager.connect_postgres(postgres_config)
        print("✅ PostgreSQL connection successful")
        
        # Step 4: Test table structure retrieval
        print("Step 4: Testing table structure retrieval...")
        if tables:
            test_table = tables[0]
            print(f"Testing with table: {test_table}")
            structure = db_manager.get_mysql_table_structure(mysql_conn, test_table)
            print(f"✅ Got structure for {test_table}: {len(structure)} columns")
            
            # Step 5: Test record count
            print("Step 5: Testing record count...")
            count = db_manager.get_mysql_table_count(mysql_conn, test_table)
            print(f"✅ Table {test_table} has {count} records")
        
        # Step 6: Test PostgreSQL table creation
        print("Step 6: Testing PostgreSQL table creation...")
        if tables:
            test_table = tables[0]
            print(f"Creating PostgreSQL table: {test_table}")
            db_manager.create_postgres_table(postgres_conn, test_table, structure)
            print(f"✅ Created PostgreSQL table: {test_table}")
        
        print("\n🎉 All migration steps completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during migration test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Clean up connections
        try:
            if 'mysql_conn' in locals():
                mysql_conn.close()
                print("🔌 MySQL connection closed")
        except:
            pass
        
        try:
            if 'postgres_conn' in locals():
                postgres_conn.close()
                print("🔌 PostgreSQL connection closed")
        except:
            pass
    
    return True

if __name__ == "__main__":
    success = test_migration_steps()
    sys.exit(0 if success else 1)
