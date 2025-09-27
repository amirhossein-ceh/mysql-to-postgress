#!/usr/bin/env python3
"""
Simple one-liner MySQL connection test
"""

import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

config = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'port': int(os.getenv('MYSQL_PORT', 3306)),
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', ''),
    'database': os.getenv('MYSQL_DATABASE', '')
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()
    cursor.execute('SELECT VERSION()')
    version = cursor.fetchone()
    cursor.execute('SHOW TABLES')
    tables = cursor.fetchall()
    cursor.close()
    conn.close()
    print(f'✅ MySQL Connected! Version: {version[0]}, Tables: {len(tables)}')
except Exception as e:
    print(f'❌ MySQL Connection Failed: {e}')
