#!/usr/bin/env python3
"""
Simple migration test without Flask/socket complications
"""

import os
import sys
import threading
import time
from dotenv import load_dotenv
from database_manager import DatabaseManager
from system_monitor import SystemMonitor, MemoryController

def simple_migration():
    """Simple migration without Flask complications"""
    print("🚀 Starting Simple Migration Test")
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
    system_monitor = SystemMonitor(max_memory_mb=1024, cpu_cores=3)
    memory_controller = MemoryController(system_monitor)
    
    mysql_conn = None
    postgres_conn = None
    
    try:
        # Connect to databases
        print("🔌 Connecting to MySQL database...")
        mysql_conn = db_manager.connect_mysql(mysql_config)
        print("✓ MySQL connection established")
        
        print("🔌 Connecting to PostgreSQL database...")
        postgres_conn = db_manager.connect_postgres(postgres_config)
        print("✓ PostgreSQL connection established")
        
        # Get all tables from MySQL
        print("📋 Fetching table list from MySQL...")
        tables = db_manager.get_mysql_tables(mysql_conn)
        print(f"✓ Found {len(tables)} tables to migrate: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
        
        # Create thread pool executor for parallel table processing
        max_workers = min(system_monitor.cpu_cores, len(tables))
        print(f"⚡ Starting parallel migration with {max_workers} workers")
        
        # Test with just the first table to avoid overwhelming the system
        test_table = tables[0]
        print(f"🧪 Testing with table: {test_table}")
        
        # Get table structure
        table_structure = db_manager.get_mysql_table_structure(mysql_conn, test_table)
        print(f"✓ Retrieved structure for table {test_table} ({len(table_structure)} columns)")
        
        # Get total record count
        total_records = db_manager.get_mysql_table_count(mysql_conn, test_table)
        print(f"📈 Table {test_table} has {total_records} records")
        
        # Create table in PostgreSQL
        db_manager.create_postgres_table(postgres_conn, test_table, table_structure)
        print(f"✓ Created PostgreSQL table: {test_table}")
        
        if total_records == 0:
            print(f"⚠️ Table {test_table} is empty, skipping data migration")
        else:
            # Process a small batch to test
            batch_size = min(100, total_records)  # Small batch for testing
            print(f"📦 Testing with batch size: {batch_size}")
            
            # Get batch data
            batch_data = db_manager.get_mysql_table_data_batch(mysql_conn, test_table, 0, batch_size)
            print(f"✓ Retrieved {len(batch_data)} records from MySQL")
            
            # Insert batch data
            processed_count = db_manager.insert_postgres_data_batch(
                postgres_conn, 
                test_table, 
                batch_data, 
                table_structure
            )
            print(f"✓ Inserted {processed_count} records into PostgreSQL")
        
        print("🎉 Simple migration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close connections
        try:
            if mysql_conn:
                mysql_conn.close()
                print("🔌 MySQL connection closed")
        except Exception as e:
            print(f"⚠️ Warning: Error closing MySQL connection: {str(e)}")
        
        try:
            if postgres_conn:
                postgres_conn.close()
                print("🔌 PostgreSQL connection closed")
        except Exception as e:
            print(f"⚠️ Warning: Error closing PostgreSQL connection: {str(e)}")
    
    return True

if __name__ == "__main__":
    success = simple_migration()
    sys.exit(0 if success else 1)

