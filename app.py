from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import os
from dotenv import load_dotenv
from database_manager import DatabaseManager
from system_monitor import SystemMonitor, MemoryController
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'M0d@@m')
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables for migration status
migration_status = {
    'is_running': False,
    'current_table': '',
    'total_tables': 0,
    'completed_tables': 0,
    'current_progress': 0,
    'total_records': 0,
    'processed_records': 0,
    'error_message': '',
    'success_message': '',
    'system_info': {},
    'active_tables': [],  # Track which tables are currently being processed
    'parallel_workers': 0
}

# Thread-safe locks for status updates
status_lock = threading.Lock()
progress_lock = threading.Lock()

# System monitoring and resource management
system_monitor = SystemMonitor(max_memory_mb=1024, cpu_cores=3)
memory_controller = MemoryController(system_monitor)
db_manager = DatabaseManager()

# Start system monitoring
system_monitor.start_monitoring()

def update_migration_status(updates):
    """Thread-safe function to update migration status"""
    with status_lock:
        migration_status.update(updates)
        
        # Emit progress update for important status changes
        important_keys = ['total_tables', 'parallel_workers', 'completed_tables', 'current_progress']
        if any(key in updates for key in important_keys):
            # Emit update without holding the lock
            current_status = migration_status.copy()
            try:
                socketio.emit('progress_update', {
                    'message': 'Status updated',
                    'status': current_status
                })
            except Exception as e:
                print(f"ERROR emitting status update: {e}")

def update_progress(processed_records, total_records, completed_tables, total_tables):
    """Thread-safe function to update progress"""
    with progress_lock:
        migration_status['processed_records'] += processed_records
        migration_status['completed_tables'] = completed_tables
        
        # Calculate overall progress
        if total_tables > 0 and migration_status['total_records'] > 0:
            # Simple progress calculation based on processed records vs total records
            migration_status['current_progress'] = min((migration_status['processed_records'] / migration_status['total_records']) * 100, 100)
            
            # Emit progress update
            try:
                current_status = migration_status.copy()
                socketio.emit('progress_update', {
                    'message': f'Progress: {completed_tables}/{total_tables} tables, {migration_status["processed_records"]}/{migration_status["total_records"]} records',
                    'status': current_status
                })
            except Exception as e:
                print(f"ERROR emitting progress update: {e}")

def emit_progress_safe(message, table_name=None):
    """Thread-safe function to emit progress updates"""
    try:
        with status_lock:
            if table_name:
                migration_status['current_table'] = table_name
            migration_status['system_info'] = system_monitor.get_system_info()
            # Create a copy of the current status
            current_status = migration_status.copy()
            
        # Emit without holding the lock to avoid deadlocks
        socketio.emit('progress_update', {
            'message': message,
            'status': current_status
        })
        print(f"PROGRESS: {message}")  # Also print to console for debugging
        print(f"STATUS: {current_status}")  # Debug status info
    except Exception as e:
        print(f"ERROR emitting progress: {e}")
        print(f"PROGRESS: {message}")  # Fallback to console

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    # Update system info in migration status
    migration_status['system_info'] = system_monitor.get_system_info()
    return jsonify(migration_status)

@app.route('/api/system_info')
def get_system_info():
    """Get current system information"""
    return jsonify(system_monitor.get_system_info())

@app.route('/api/system_config', methods=['GET', 'POST'])
def system_config():
    """Get or update system configuration"""
    if request.method == 'POST':
        data = request.get_json()
        
        if 'cpu_cores' in data:
            cpu_cores = int(data['cpu_cores'])
            system_monitor.set_cpu_cores(cpu_cores)
            
        if 'memory_limit_mb' in data:
            memory_limit = int(data['memory_limit_mb'])
            system_monitor.set_memory_limit(memory_limit)
            
        return jsonify({'message': 'Configuration updated successfully'})
    
    return jsonify({
        'cpu_cores': system_monitor.cpu_cores,
        'memory_limit_mb': system_monitor.max_memory_mb,
        'available_cpu_cores': system_monitor.get_cpu_info()['cpu_count']
    })

@app.route('/api/memory_history')
def get_memory_history():
    """Get memory usage history"""
    return jsonify(system_monitor.get_memory_history())

@app.route('/api/force_gc', methods=['POST'])
def force_garbage_collection():
    """Manually trigger garbage collection"""
    collected = system_monitor.force_garbage_collection()
    return jsonify({'message': f'Garbage collection completed, freed {collected} objects'})

@app.route('/api/database_config')
def get_database_config():
    """Get current database configuration (without passwords)"""
    config = {
        'mysql': {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', 3306)),
            'user': os.getenv('MYSQL_USER', 'root'),
            'database': os.getenv('MYSQL_DATABASE', ''),
            'password_set': bool(os.getenv('MYSQL_PASSWORD', ''))
        },
        'postgres': {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': int(os.getenv('POSTGRES_PORT', 5432)),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'database': os.getenv('POSTGRES_DATABASE', ''),
            'password_set': bool(os.getenv('POSTGRES_PASSWORD', ''))
        }
    }
    return jsonify(config)

@app.route('/api/database_status')
def get_database_status():
    """Check database connection status"""
    mysql_config, postgres_config = get_database_config_from_env()
    
    status = {
        'mysql': {
            'connected': False,
            'error': None,
            'tables_count': 0,
            'connection_time': None
        },
        'postgres': {
            'connected': False,
            'error': None,
            'tables_count': 0,
            'connection_time': None
        }
    }
    
    # Test MySQL connection
    if mysql_config['database'] and mysql_config['password']:
        try:
            import time
            start_time = time.time()
            mysql_conn = db_manager.create_mysql_connection(mysql_config)
            connection_time = time.time() - start_time
            
            # Get table count
            tables = db_manager.get_mysql_tables(mysql_conn)
            mysql_conn.close()
            
            status['mysql'] = {
                'connected': True,
                'error': None,
                'tables_count': len(tables),
                'connection_time': round(connection_time * 1000, 2)  # Convert to milliseconds
            }
        except Exception as e:
            status['mysql']['error'] = str(e)
    else:
        status['mysql']['error'] = 'Database name or password not configured'
    
    # Test PostgreSQL connection
    if postgres_config['database'] and postgres_config['password']:
        try:
            import time
            start_time = time.time()
            postgres_conn = db_manager.create_postgres_connection(postgres_config)
            connection_time = time.time() - start_time
            
            # Get table count (PostgreSQL)
            cursor = postgres_conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables_count = cursor.fetchone()[0]
            cursor.close()
            postgres_conn.close()
            
            status['postgres'] = {
                'connected': True,
                'error': None,
                'tables_count': tables_count,
                'connection_time': round(connection_time * 1000, 2)  # Convert to milliseconds
            }
        except Exception as e:
            status['postgres']['error'] = str(e)
    else:
        status['postgres']['error'] = 'Database name or password not configured'
    
    return jsonify(status)

def get_database_config_from_env():
    """Get database configuration from environment variables"""
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
    
    return mysql_config, postgres_config

@app.route('/api/start_migration', methods=['POST'])
def start_migration():
    global migration_status
    
    if migration_status['is_running']:
        return jsonify({'error': 'Migration is already running'}), 400
    
    try:
        # Get database configuration from environment variables
        mysql_config, postgres_config = get_database_config_from_env()
        
        # Validate required fields with detailed error messages
        if not mysql_config['database']:
            return jsonify({'error': 'MySQL database name is not configured. Please set MYSQL_DATABASE in your .env file.'}), 400
        
        if not postgres_config['database']:
            return jsonify({'error': 'PostgreSQL database name is not configured. Please set POSTGRES_DATABASE in your .env file.'}), 400
        
        if not mysql_config['password']:
            return jsonify({'error': 'MySQL password is not configured. Please set MYSQL_PASSWORD in your .env file.'}), 400
        
        if not postgres_config['password']:
            return jsonify({'error': 'PostgreSQL password is not configured. Please set POSTGRES_PASSWORD in your .env file.'}), 400
        
        # Test database connections before starting migration
        emit_progress_safe('Testing database connections before starting migration...')
        
        try:
            # Test MySQL connection
            mysql_conn = db_manager.create_mysql_connection(mysql_config)
            mysql_conn.close()
            emit_progress_safe('✓ MySQL connection test successful')
        except Exception as e:
            error_msg = f'MySQL connection failed: {str(e)}. Please check your MySQL configuration in .env file.'
            emit_progress_safe(f'✗ {error_msg}')
            return jsonify({'error': error_msg}), 400
        
        try:
            # Test PostgreSQL connection
            postgres_conn = db_manager.create_postgres_connection(postgres_config)
            postgres_conn.close()
            emit_progress_safe('✓ PostgreSQL connection test successful')
        except Exception as e:
            error_msg = f'PostgreSQL connection failed: {str(e)}. Please check your PostgreSQL configuration in .env file.'
            emit_progress_safe(f'✗ {error_msg}')
            return jsonify({'error': error_msg}), 400
        
        # Reset status
        migration_status.update({
            'is_running': True,
            'current_table': '',
            'total_tables': 0,
            'completed_tables': 0,
            'current_progress': 0,
            'total_records': 0,
            'processed_records': 0,
            'error_message': '',
            'success_message': '',
            'active_tables': [],
            'parallel_workers': 0
        })
        
        # Start migration in a separate thread
        migration_thread = threading.Thread(
            target=run_migration,
            args=(mysql_config, postgres_config)
        )
        migration_thread.daemon = True
        migration_thread.start()
        
        emit_progress_safe('🚀 Migration thread started successfully!')
        return jsonify({'message': 'Migration started successfully'})
        
    except Exception as e:
        error_msg = f'Failed to start migration: {str(e)}'
        emit_progress_safe(f'✗ {error_msg}')
        return jsonify({'error': error_msg}), 500

def run_migration(mysql_config, postgres_config):
    """Main migration function with parallel processing"""
    global migration_status
    
    mysql_conn = None
    postgres_conn = None
    
    try:
        # Connect to databases with timeout handling
        emit_progress_safe('🔌 Connecting to MySQL database...')
        try:
            print(f"DEBUG: About to connect to MySQL with config: {mysql_config}")
            mysql_conn = db_manager.connect_mysql(mysql_config)
            print(f"DEBUG: MySQL connection established: {mysql_conn}")
            emit_progress_safe('✓ MySQL connection established')
        except Exception as e:
            print(f"DEBUG: MySQL connection failed: {e}")
            raise Exception(f'Failed to connect to MySQL: {str(e)}')
        
        emit_progress_safe('🔌 Connecting to PostgreSQL database...')
        try:
            print(f"DEBUG: About to connect to PostgreSQL with config: {postgres_config}")
            postgres_conn = db_manager.connect_postgres(postgres_config)
            print(f"DEBUG: PostgreSQL connection established: {postgres_conn}")
            emit_progress_safe('✓ PostgreSQL connection established')
        except Exception as e:
            print(f"DEBUG: PostgreSQL connection failed: {e}")
            raise Exception(f'Failed to connect to PostgreSQL: {str(e)}')
        
        # Get all tables from MySQL
        emit_progress_safe('📋 Fetching table list from MySQL...')
        try:
            print(f"DEBUG: About to call get_mysql_tables with connection: {mysql_conn}")
            tables = db_manager.get_mysql_tables(mysql_conn)
            print(f"DEBUG: Got tables: {tables}")
            if not tables:
                raise Exception('No tables found in MySQL database')
            update_migration_status({'total_tables': len(tables)})
            emit_progress_safe(f'✓ Found {len(tables)} tables to migrate: {", ".join(tables[:5])}{"..." if len(tables) > 5 else ""}')
        except Exception as e:
            print(f"DEBUG: Error fetching tables: {e}")
            raise Exception(f'Failed to fetch tables from MySQL: {str(e)}')
        
        # Create thread pool executor for parallel table processing
        max_workers = min(system_monitor.cpu_cores, len(tables))
        update_migration_status({'parallel_workers': max_workers})
        
        # Emit progress update to show the updated status
        emit_progress_safe(f'⚡ Starting parallel migration with {max_workers} workers')
        
        # Use ThreadPoolExecutor for parallel table migration
        emit_progress_safe(f'🔄 Creating thread pool with {max_workers} workers for {len(tables)} tables')
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all table migration tasks
            emit_progress_safe('📤 Submitting table migration tasks...')
            future_to_table = {
                executor.submit(
                    migrate_table_parallel, 
                    mysql_config, 
                    postgres_config, 
                    table_name, 
                    i, 
                    len(tables)
                ): table_name 
                for i, table_name in enumerate(tables)
            }
            
            emit_progress_safe(f'✅ Submitted {len(future_to_table)} table migration tasks')
            
            # Process completed tasks
            completed_tables = 0
            for future in as_completed(future_to_table):
                table_name = future_to_table[future]
                try:
                    emit_progress_safe(f'🔄 Processing result for table: {table_name}')
                    result = future.result()
                    completed_tables += 1
                    update_migration_status({'completed_tables': completed_tables})
                    emit_progress_safe(f'✅ Completed table: {table_name} ({completed_tables}/{len(tables)})')
                except Exception as e:
                    error_msg = f'❌ Error migrating table {table_name}: {str(e)}'
                    emit_progress_safe(error_msg)
                    print(f"ERROR in table {table_name}: {e}")
                    raise Exception(error_msg)
        
        update_migration_status({
            'completed_tables': len(tables),
            'current_progress': 100,
            'success_message': f'🎉 Successfully migrated {len(tables)} tables using {max_workers} parallel workers!',
            'is_running': False
        })
        
        emit_progress_safe('🎉 Migration completed successfully!')
        
    except Exception as e:
        error_msg = f'❌ Migration failed: {str(e)}'
        update_migration_status({
            'error_message': error_msg,
            'is_running': False
        })
        emit_progress_safe(error_msg)
        print(f"Migration error: {e}")  # Also log to console for debugging
    
    finally:
        # Close connections safely
        try:
            if mysql_conn:
                mysql_conn.close()
                emit_progress_safe('🔌 MySQL connection closed')
        except Exception as e:
            emit_progress_safe(f'⚠️ Warning: Error closing MySQL connection: {str(e)}')
        
        try:
            if postgres_conn:
                postgres_conn.close()
                emit_progress_safe('🔌 PostgreSQL connection closed')
        except Exception as e:
            emit_progress_safe(f'⚠️ Warning: Error closing PostgreSQL connection: {str(e)}')

def migrate_table_parallel(mysql_config, postgres_config, table_name, table_index, total_tables):
    """Migrate a single table with parallel batch processing"""
    mysql_conn = None
    postgres_conn = None
    
    try:
        print(f"DEBUG: Starting migration for table {table_name} (index {table_index}/{total_tables})")
        
        # Create dedicated connections for this thread
        emit_progress_safe(f'🔗 Creating connections for table: {table_name}', table_name)
        try:
            print(f"DEBUG: Creating MySQL connection for table {table_name}")
            mysql_conn = db_manager.create_mysql_connection(mysql_config)
            print(f"DEBUG: MySQL connection created for table {table_name}")
            
            print(f"DEBUG: Creating PostgreSQL connection for table {table_name}")
            postgres_conn = db_manager.create_postgres_connection(postgres_config)
            print(f"DEBUG: PostgreSQL connection created for table {table_name}")
        except Exception as e:
            print(f"DEBUG: Connection error for table {table_name}: {e}")
            raise Exception(f'Failed to create database connections for table {table_name}: {str(e)}')
        
        emit_progress_safe(f'📊 Starting migration of table: {table_name}', table_name)
        
        # Get table structure
        try:
            print(f"DEBUG: Getting table structure for {table_name}")
            table_structure = db_manager.get_mysql_table_structure(mysql_conn, table_name)
            print(f"DEBUG: Got table structure for {table_name}: {len(table_structure) if table_structure else 0} columns")
            if not table_structure:
                raise Exception(f'No structure found for table {table_name}')
            emit_progress_safe(f'✓ Retrieved structure for table {table_name} ({len(table_structure)} columns)')
        except Exception as e:
            print(f"DEBUG: Error getting table structure for {table_name}: {e}")
            raise Exception(f'Failed to get structure for table {table_name}: {str(e)}')
        
        # Get total record count
        try:
            print(f"DEBUG: Getting record count for {table_name}")
            total_records = db_manager.get_mysql_table_count(mysql_conn, table_name)
            print(f"DEBUG: Got record count for {table_name}: {total_records}")
            # Update total records by adding current table's records
            with status_lock:
                migration_status['total_records'] += total_records
            emit_progress_safe(f'📈 Table {table_name} has {total_records} records')
        except Exception as e:
            print(f"DEBUG: Error getting record count for {table_name}: {e}")
            raise Exception(f'Failed to get record count for table {table_name}: {str(e)}')
        
        # Create table in PostgreSQL
        try:
            print(f"DEBUG: Creating PostgreSQL table {table_name}")
            db_manager.create_postgres_table(postgres_conn, table_name, table_structure)
            print(f"DEBUG: PostgreSQL table {table_name} created successfully")
            emit_progress_safe(f'✓ Created PostgreSQL table: {table_name}')
        except Exception as e:
            print(f"DEBUG: Error creating PostgreSQL table {table_name}: {e}")
            raise Exception(f'Failed to create PostgreSQL table {table_name}: {str(e)}')
        
        if total_records == 0:
            emit_progress_safe(f'⚠️ Table {table_name} is empty, skipping data migration')
            return
        
        # Process data in parallel batches
        print(f"DEBUG: Starting batch processing for {table_name}")
        batch_size = memory_controller.get_optimal_batch_size()
        max_workers = min(system_monitor.cpu_cores, 4)  # Limit batch workers to avoid too many connections
        
        print(f"DEBUG: Batch size: {batch_size}, Max workers: {max_workers}")
        
        # Calculate batch ranges
        batch_ranges = []
        for offset in range(0, total_records, batch_size):
            limit = min(batch_size, total_records - offset)
            batch_ranges.append((offset, limit))
        
        print(f"DEBUG: Created {len(batch_ranges)} batch ranges for {table_name}")
        emit_progress_safe(f'⚡ Processing {len(batch_ranges)} batches for table {table_name} with {max_workers} workers (batch size: {batch_size})')
        
        # Use ThreadPoolExecutor for parallel batch processing
        print(f"DEBUG: Creating batch executor for {table_name}")
        with ThreadPoolExecutor(max_workers=max_workers) as batch_executor:
            # Submit all batch processing tasks
            print(f"DEBUG: Submitting {len(batch_ranges)} batch tasks for {table_name}")
            batch_futures = [
                batch_executor.submit(
                    process_batch_parallel,
                    mysql_config,
                    postgres_config,
                    table_name,
                    table_structure,
                    offset,
                    limit,
                    batch_index,
                    len(batch_ranges)
                )
                for batch_index, (offset, limit) in enumerate(batch_ranges)
            ]
            
            print(f"DEBUG: Submitted {len(batch_futures)} batch tasks for {table_name}")
            
            # Wait for all batches to complete
            processed_records = 0
            for future in as_completed(batch_futures):
                try:
                    print(f"DEBUG: Processing batch result for {table_name}")
                    batch_processed = future.result()
                    processed_records += batch_processed
                    print(f"DEBUG: Batch processed {batch_processed} records for {table_name}")
                    # Update progress with current table's progress
                    update_progress(batch_processed, total_records, table_index, total_tables)
                except Exception as e:
                    error_msg = f'❌ Error processing batch for table {table_name}: {str(e)}'
                    print(f"DEBUG: Batch error for {table_name}: {e}")
                    emit_progress_safe(error_msg)
                    raise Exception(error_msg)
        
        emit_progress_safe(f'✅ Completed table {table_name}: {processed_records} records migrated')
        
    except Exception as e:
        error_msg = f'❌ Error migrating table {table_name}: {str(e)}'
        emit_progress_safe(error_msg)
        print(f"Table migration error for {table_name}: {e}")  # Also log to console
        raise e
    
    finally:
        # Close thread-specific connections
        try:
            if mysql_conn:
                mysql_conn.close()
        except Exception as e:
            emit_progress_safe(f'⚠️ Warning: Error closing MySQL connection for table {table_name}: {str(e)}')
        
        try:
            if postgres_conn:
                postgres_conn.close()
        except Exception as e:
            emit_progress_safe(f'⚠️ Warning: Error closing PostgreSQL connection for table {table_name}: {str(e)}')

def process_batch_parallel(mysql_config, postgres_config, table_name, table_structure, offset, limit, batch_index, total_batches):
    """Process a single batch of records in parallel"""
    mysql_conn = None
    postgres_conn = None
    
    try:
        print(f"DEBUG: Processing batch {batch_index}/{total_batches} for {table_name} (offset: {offset}, limit: {limit})")
        
        # Create dedicated connections for this batch
        try:
            print(f"DEBUG: Creating batch connections for {table_name} batch {batch_index}")
            mysql_conn = db_manager.create_mysql_connection(mysql_config)
            postgres_conn = db_manager.create_postgres_connection(postgres_config)
            print(f"DEBUG: Batch connections created for {table_name} batch {batch_index}")
        except Exception as e:
            print(f"DEBUG: Batch connection error for {table_name} batch {batch_index}: {e}")
            raise Exception(f'Failed to create batch connections: {str(e)}')
        
        # Get batch data
        try:
            print(f"DEBUG: Fetching batch data for {table_name} batch {batch_index}")
            batch_data = db_manager.get_mysql_table_data_batch(mysql_conn, table_name, offset, limit)
            print(f"DEBUG: Fetched {len(batch_data) if batch_data else 0} records for {table_name} batch {batch_index}")
        except Exception as e:
            print(f"DEBUG: Batch data fetch error for {table_name} batch {batch_index}: {e}")
            raise Exception(f'Failed to fetch batch data (offset {offset}, limit {limit}): {str(e)}')
        
        if not batch_data:
            print(f"DEBUG: No data in batch {batch_index} for {table_name}")
            return 0
        
        # Check for memory pressure
        if memory_controller.should_pause_processing():
            print(f"DEBUG: Memory pressure detected, pausing for {table_name} batch {batch_index}")
            memory_controller.pause_for_memory_recovery()
        
        # Insert batch data
        try:
            print(f"DEBUG: Inserting batch data for {table_name} batch {batch_index}")
            processed_count = db_manager.insert_postgres_data_batch(
                postgres_conn, 
                table_name, 
                batch_data, 
                table_structure
            )
            print(f"DEBUG: Inserted {processed_count} records for {table_name} batch {batch_index}")
            return processed_count
        except Exception as e:
            print(f"DEBUG: Batch insert error for {table_name} batch {batch_index}: {e}")
            raise Exception(f'Failed to insert batch data: {str(e)}')
        
    except Exception as e:
        error_msg = f'❌ Error processing batch {batch_index + 1}/{total_batches} for table {table_name}: {str(e)}'
        emit_progress_safe(error_msg)
        print(f"Batch processing error: {e}")  # Also log to console
        raise e
    
    finally:
        # Close batch-specific connections
        try:
            if mysql_conn:
                mysql_conn.close()
        except Exception as e:
            print(f"Warning: Error closing MySQL batch connection: {e}")
        
        try:
            if postgres_conn:
                postgres_conn.close()
        except Exception as e:
            print(f"Warning: Error closing PostgreSQL batch connection: {e}")

def emit_progress(message):
    # Update system info before emitting
    migration_status['system_info'] = system_monitor.get_system_info()
    socketio.emit('progress_update', {
        'message': message,
        'status': migration_status
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
