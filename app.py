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

def update_progress(processed_records, total_records, completed_tables, total_tables):
    """Thread-safe function to update progress"""
    with progress_lock:
        migration_status['processed_records'] += processed_records
        migration_status['completed_tables'] = completed_tables
        if total_records > 0:
            table_progress = (processed_records / total_records) * 100
            overall_progress = ((completed_tables + (table_progress / 100)) / total_tables) * 100
            migration_status['current_progress'] = min(overall_progress, 100)

def emit_progress_safe(message, table_name=None):
    """Thread-safe function to emit progress updates"""
    with status_lock:
        if table_name:
            migration_status['current_table'] = table_name
        migration_status['system_info'] = system_monitor.get_system_info()
        socketio.emit('progress_update', {
            'message': message,
            'status': migration_status.copy()
        })

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
    
    # Get database configuration from environment variables
    mysql_config, postgres_config = get_database_config_from_env()
    
    # Validate required fields
    if not mysql_config['database'] or not postgres_config['database']:
        return jsonify({'error': 'Database names must be configured in .env file'}), 400
    
    if not mysql_config['password'] or not postgres_config['password']:
        return jsonify({'error': 'Database passwords must be configured in .env file'}), 400
    
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
    
    return jsonify({'message': 'Migration started'})

def run_migration(mysql_config, postgres_config):
    """Main migration function with parallel processing"""
    global migration_status
    
    try:
        # Connect to databases
        emit_progress_safe('Connecting to MySQL database...')
        mysql_conn = db_manager.connect_mysql(mysql_config)
        
        emit_progress_safe('Connecting to PostgreSQL database...')
        postgres_conn = db_manager.connect_postgres(postgres_config)
        
        # Get all tables from MySQL
        emit_progress_safe('Fetching table list from MySQL...')
        tables = db_manager.get_mysql_tables(mysql_conn)
        update_migration_status({'total_tables': len(tables)})
        
        emit_progress_safe(f'Found {len(tables)} tables to migrate')
        
        # Create thread pool executor for parallel table processing
        max_workers = min(system_monitor.cpu_cores, len(tables))
        update_migration_status({'parallel_workers': max_workers})
        
        emit_progress_safe(f'Starting parallel migration with {max_workers} workers')
        
        # Use ThreadPoolExecutor for parallel table migration
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all table migration tasks
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
            
            # Process completed tasks
            completed_tables = 0
            for future in as_completed(future_to_table):
                table_name = future_to_table[future]
                try:
                    result = future.result()
                    completed_tables += 1
                    update_migration_status({'completed_tables': completed_tables})
                    emit_progress_safe(f'Completed table: {table_name} ({completed_tables}/{len(tables)})')
                except Exception as e:
                    emit_progress_safe(f'Error migrating table {table_name}: {str(e)}')
                    raise e
        
        update_migration_status({
            'completed_tables': len(tables),
            'current_progress': 100,
            'success_message': f'Successfully migrated {len(tables)} tables using {max_workers} parallel workers!',
            'is_running': False
        })
        
        emit_progress_safe('Migration completed successfully!')
        
    except Exception as e:
        update_migration_status({
            'error_message': str(e),
            'is_running': False
        })
        emit_progress_safe(f'Migration failed: {str(e)}')
    
    finally:
        # Close connections
        try:
            if 'mysql_conn' in locals():
                mysql_conn.close()
            if 'postgres_conn' in locals():
                postgres_conn.close()
        except:
            pass

def migrate_table_parallel(mysql_config, postgres_config, table_name, table_index, total_tables):
    """Migrate a single table with parallel batch processing"""
    mysql_conn = None
    postgres_conn = None
    
    try:
        # Create dedicated connections for this thread
        mysql_conn = db_manager.create_mysql_connection(mysql_config)
        postgres_conn = db_manager.create_postgres_connection(postgres_config)
        
        emit_progress_safe(f'Starting migration of table: {table_name}', table_name)
        
        # Get table structure
        table_structure = db_manager.get_mysql_table_structure(mysql_conn, table_name)
        
        # Get total record count
        total_records = db_manager.get_mysql_table_count(mysql_conn, table_name)
        update_migration_status({'total_records': total_records})
        
        # Create table in PostgreSQL
        db_manager.create_postgres_table(postgres_conn, table_name, table_structure)
        
        if total_records == 0:
            emit_progress_safe(f'Table {table_name} is empty, skipping data migration')
            return
        
        # Process data in parallel batches
        batch_size = memory_controller.get_optimal_batch_size()
        max_workers = min(system_monitor.cpu_cores, 4)  # Limit batch workers to avoid too many connections
        
        # Calculate batch ranges
        batch_ranges = []
        for offset in range(0, total_records, batch_size):
            limit = min(batch_size, total_records - offset)
            batch_ranges.append((offset, limit))
        
        emit_progress_safe(f'Processing {len(batch_ranges)} batches for table {table_name} with {max_workers} workers')
        
        # Use ThreadPoolExecutor for parallel batch processing
        with ThreadPoolExecutor(max_workers=max_workers) as batch_executor:
            # Submit all batch processing tasks
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
            
            # Wait for all batches to complete
            processed_records = 0
            for future in as_completed(batch_futures):
                try:
                    batch_processed = future.result()
                    processed_records += batch_processed
                    update_progress(batch_processed, total_records, table_index, total_tables)
                except Exception as e:
                    emit_progress_safe(f'Error processing batch for table {table_name}: {str(e)}')
                    raise e
        
        emit_progress_safe(f'Completed table {table_name}: {processed_records} records migrated')
        
    except Exception as e:
        emit_progress_safe(f'Error migrating table {table_name}: {str(e)}')
        raise e
    
    finally:
        # Close thread-specific connections
        try:
            if mysql_conn:
                mysql_conn.close()
            if postgres_conn:
                postgres_conn.close()
        except:
            pass

def process_batch_parallel(mysql_config, postgres_config, table_name, table_structure, offset, limit, batch_index, total_batches):
    """Process a single batch of records in parallel"""
    mysql_conn = None
    postgres_conn = None
    
    try:
        # Create dedicated connections for this batch
        mysql_conn = db_manager.create_mysql_connection(mysql_config)
        postgres_conn = db_manager.create_postgres_connection(postgres_config)
        
        # Get batch data
        batch_data = db_manager.get_mysql_table_data_batch(mysql_conn, table_name, offset, limit)
        
        if not batch_data:
            return 0
        
        # Check for memory pressure
        if memory_controller.should_pause_processing():
            memory_controller.pause_for_memory_recovery()
        
        # Insert batch data
        processed_count = db_manager.insert_postgres_data_batch(
            postgres_conn, 
            table_name, 
            batch_data, 
            table_structure
        )
        
        return processed_count
        
    except Exception as e:
        emit_progress_safe(f'Error processing batch {batch_index + 1}/{total_batches} for table {table_name}: {str(e)}')
        raise e
    
    finally:
        # Close batch-specific connections
        try:
            if mysql_conn:
                mysql_conn.close()
            if postgres_conn:
                postgres_conn.close()
        except:
            pass

def emit_progress(message):
    # Update system info before emitting
    migration_status['system_info'] = system_monitor.get_system_info()
    socketio.emit('progress_update', {
        'message': message,
        'status': migration_status
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
