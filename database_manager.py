import mysql.connector
import psycopg2
from psycopg2.extras import RealDictCursor
import json
import threading
from typing import List, Dict, Any

class DatabaseManager:
    def __init__(self):
        self.mysql_connection = None
        self.postgres_connection = None
        self._lock = threading.Lock()
    
    def create_mysql_connection(self, config: Dict[str, Any]):
        """Create a new MySQL connection (thread-safe)"""
        try:
            connection = mysql.connector.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                user=config.get('user', 'root'),
                password=config.get('password', ''),
                database=config.get('database', ''),
                charset='utf8mb4',
                connection_timeout=30,  # 30 second connection timeout
                autocommit=True
            )
            return connection
        except mysql.connector.Error as e:
            raise Exception(f"MySQL connection error: {e}")
    
    def create_postgres_connection(self, config: Dict[str, Any]):
        """Create a new PostgreSQL connection (thread-safe)"""
        try:
            connection = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                user=config.get('user', 'postgres'),
                password=config.get('password', ''),
                database=config.get('database', 'postgres'),
                connect_timeout=30,  # 30 second connection timeout
                application_name='db_migration_tool'
            )
            connection.autocommit = True
            return connection
        except psycopg2.Error as e:
            raise Exception(f"PostgreSQL connection error: {e}")
    
    def connect_mysql(self, config: Dict[str, Any]):
        """Connect to MySQL database"""
        try:
            self.mysql_connection = mysql.connector.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 3306),
                user=config.get('user', 'root'),
                password=config.get('password', ''),
                database=config.get('database', ''),
                charset='utf8mb4',
                connection_timeout=30,  # 30 second connection timeout
                autocommit=True
            )
            return self.mysql_connection
        except mysql.connector.Error as e:
            raise Exception(f"MySQL connection error: {e}")
    
    def connect_postgres(self, config: Dict[str, Any]):
        """Connect to PostgreSQL database"""
        try:
            self.postgres_connection = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                user=config.get('user', 'postgres'),
                password=config.get('password', ''),
                database=config.get('database', 'postgres'),
                connect_timeout=30,  # 30 second connection timeout
                application_name='db_migration_tool'
            )
            self.postgres_connection.autocommit = True
            return self.postgres_connection
        except psycopg2.Error as e:
            raise Exception(f"PostgreSQL connection error: {e}")
    
    def get_mysql_tables(self, connection) -> List[str]:
        """Get list of all tables from MySQL database"""
        cursor = connection.cursor()
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        cursor.close()
        return tables
    
    def get_mysql_table_structure(self, connection, table_name: str) -> List[Dict[str, Any]]:
        """Get table structure from MySQL"""
        cursor = connection.cursor()
        cursor.execute(f"DESCRIBE `{table_name}`")
        columns = cursor.fetchall()
        cursor.close()
        
        structure = []
        for column in columns:
            structure.append({
                'name': column[0],
                'type': column[1],
                'null': column[2] == 'YES',
                'key': column[3],
                'default': column[4],
                'extra': column[5]
            })
        return structure
    
    def get_mysql_table_data(self, connection, table_name: str) -> List[Dict[str, Any]]:
        """Get all data from MySQL table"""
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}`")
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def get_mysql_table_data_batch(self, connection, table_name: str, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Get a batch of data from MySQL table (for parallel processing)"""
        cursor = connection.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit} OFFSET {offset}")
        data = cursor.fetchall()
        cursor.close()
        return data
    
    def get_mysql_table_count(self, connection, table_name: str) -> int:
        """Get total record count for a table"""
        cursor = connection.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def mysql_to_postgres_type(self, mysql_type: str) -> str:
        """Convert MySQL data type to PostgreSQL data type"""
        mysql_type = mysql_type.lower()
        
        if 'int' in mysql_type:
            if 'bigint' in mysql_type:
                return 'BIGINT'
            elif 'smallint' in mysql_type:
                return 'SMALLINT'
            elif 'tinyint' in mysql_type:
                return 'SMALLINT'
            else:
                return 'INTEGER'
        elif 'varchar' in mysql_type or 'char' in mysql_type:
            if 'varchar' in mysql_type:
                return 'VARCHAR'
            else:
                return 'CHAR'
        elif 'text' in mysql_type:
            return 'TEXT'
        elif 'decimal' in mysql_type or 'numeric' in mysql_type:
            return 'DECIMAL'
        elif 'float' in mysql_type or 'double' in mysql_type:
            return 'DOUBLE PRECISION'
        elif 'date' in mysql_type:
            return 'DATE'
        elif 'time' in mysql_type:
            return 'TIME'
        elif 'datetime' in mysql_type or 'timestamp' in mysql_type:
            return 'TIMESTAMP'
        elif 'blob' in mysql_type:
            return 'BYTEA'
        elif 'json' in mysql_type:
            return 'JSON'
        else:
            return 'TEXT'  # Default fallback
    
    def create_postgres_table(self, connection, table_name: str, structure: List[Dict[str, Any]]):
        """Create table in PostgreSQL based on MySQL structure"""
        cursor = connection.cursor()
        
        # Drop table if exists
        cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
        
        # Create table
        columns = []
        for column in structure:
            col_name = column['name']
            col_type = self.mysql_to_postgres_type(column['type'])
            nullable = 'NULL' if column['null'] else 'NOT NULL'
            
            # Handle primary key
            if column['key'] == 'PRI':
                col_type += ' PRIMARY KEY'
            
            columns.append(f'"{col_name}" {col_type} {nullable}')
        
        create_sql = f'CREATE TABLE "{table_name}" ({", ".join(columns)})'
        cursor.execute(create_sql)
        connection.commit()
        cursor.close()
    
    def insert_postgres_data(self, connection, table_name: str, data: List[Dict[str, Any]], structure: List[Dict[str, Any]]):
        """Insert data into PostgreSQL table"""
        if not data:
            return
        
        cursor = connection.cursor()
        
        # Get column names
        columns = [col['name'] for col in structure]
        column_names = ', '.join([f'"{col}"' for col in columns])
        
        # Prepare insert statement
        placeholders = ', '.join(['%s'] * len(columns))
        insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'
        
        # Prepare data for insertion
        values_list = []
        for row in data:
            values = []
            for col in columns:
                value = row.get(col)
                # Handle None values and data type conversions
                if value is None:
                    values.append(None)
                elif isinstance(value, (dict, list)):
                    values.append(json.dumps(value))
                else:
                    values.append(value)
            values_list.append(tuple(values))
        
        # Execute batch insert
        cursor.executemany(insert_sql, values_list)
        connection.commit()
        cursor.close()
    
    def insert_postgres_data_batch(self, connection, table_name: str, data: List[Dict[str, Any]], structure: List[Dict[str, Any]]):
        """Insert a batch of data into PostgreSQL table (thread-safe)"""
        if not data:
            return 0
        
        with self._lock:
            cursor = connection.cursor()
            
            try:
                # Get column names
                columns = [col['name'] for col in structure]
                column_names = ', '.join([f'"{col}"' for col in columns])
                
                # Prepare insert statement
                placeholders = ', '.join(['%s'] * len(columns))
                insert_sql = f'INSERT INTO "{table_name}" ({column_names}) VALUES ({placeholders})'
                
                # Prepare data for insertion
                values_list = []
                for row in data:
                    values = []
                    for col in columns:
                        value = row.get(col)
                        # Handle None values and data type conversions
                        if value is None:
                            values.append(None)
                        elif isinstance(value, (dict, list)):
                            values.append(json.dumps(value))
                        else:
                            values.append(value)
                    values_list.append(tuple(values))
                
                # Execute batch insert
                cursor.executemany(insert_sql, values_list)
                connection.commit()
                return len(values_list)
                
            except Exception as e:
                connection.rollback()
                raise e
            finally:
                cursor.close()
    
    def close_connections(self):
        """Close all database connections"""
        if self.mysql_connection:
            self.mysql_connection.close()
        if self.postgres_connection:
            self.postgres_connection.close()
