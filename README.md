# 🚀 MySQL to PostgreSQL Migration Tool

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A high-performance, multi-threaded Flask-based web application that migrates data from MySQL to PostgreSQL with real-time progress tracking, connection testing, and a beautiful user interface. Features parallel processing, memory management, and comprehensive system monitoring.

## 📋 Table of Contents

- [✨ Key Highlights](#-key-highlights)
- [🚀 Quick Start](#-quick-start)
- [📖 Usage Guide](#-usage-guide)
- [⚙️ Database Configuration](#️-database-configuration)
- [🔍 Connection Testing](#-connection-testing)
- [🚀 Multi-threading and Performance Features](#-multi-threading-and-performance-features)
- [📊 System Monitoring Features](#-system-monitoring-features)
- [🔧 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## ✨ Key Highlights

- **🔥 Multi-threaded Processing**: 2-4x faster migrations with parallel table and batch processing
- **🔍 Connection Testing**: Real-time database connectivity monitoring and validation
- **📊 Live Monitoring**: Real-time progress tracking with WebSocket support
- **🧠 Smart Memory Management**: Automatic memory control and garbage collection
- **⚡ Performance Optimized**: CPU core utilization and memory-aware batch sizing
- **🐳 Docker Ready**: Fully containerized with Docker Compose
- **🎨 Modern UI**: Beautiful, responsive web interface with real-time updates

## Features

- 🔄 **Real-time Migration**: Live progress updates with WebSocket support
- 📊 **Progress Tracking**: Detailed progress bars and status information
- 🎨 **Modern UI**: Beautiful, responsive web interface
- 🐳 **Docker Support**: Fully containerized with Docker Compose
- 🔧 **Auto-reload**: Development mode with automatic code reloading
- 📝 **Detailed Logging**: Real-time log output during migration
- 🛡️ **Error Handling**: Comprehensive error handling and reporting
- 🧠 **Memory Management**: Real-time memory monitoring and automatic memory control
- ⚙️ **CPU Management**: Configurable CPU core usage (default: 3 cores)
- 📈 **System Monitoring**: Live system resource monitoring with history
- 🗑️ **Garbage Collection**: Manual and automatic memory cleanup
- 🔍 **Connection Testing**: Real-time database connection status monitoring
- 🚀 **Multi-threading**: Parallel table and batch processing for faster migrations
- ⚡ **Performance Optimization**: CPU core utilization and memory-aware batch sizing

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended)
- **Python 3.9+** (for manual setup)
- **MySQL Database** (source)
- **PostgreSQL Database** (target)

### 🐳 Using Docker Compose (Recommended)

1. **Clone and navigate to the project:**
   ```bash
   git clone <repository-url>
   cd db_migration
   ```

2. **Create environment configuration:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Start the application:**
   ```bash
   docker-compose up --build
   ```

4. **Access the application:**
   - Open your browser: `http://localhost:5001`
   - Test database connections
   - Start migration

### 🛠️ Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - Open your browser: `http://localhost:5000`

## 📖 Usage Guide

### 1. 🔧 System Configuration
- **CPU Cores**: Set the number of CPU cores to use (default: 3)
- **Memory Limit**: Set memory limit in MB (default: 1024 MB)
- **Apply Changes**: Click "Update Configuration" to apply settings

### 2. 📊 System Monitoring
- **Real-time Metrics**: View live memory usage and CPU utilization
- **Process Monitoring**: Monitor application memory consumption
- **Memory Warnings**: Automatic alerts for high memory usage
- **Garbage Collection**: Manual memory cleanup when needed

### 3. 🔍 Connection Testing
- **Automatic Testing**: Connections tested on page load
- **Manual Testing**: Click "Test Connections" to verify connectivity
- **Status Display**: View connection status, table counts, and response times
- **Pre-migration Validation**: Ensure both databases are accessible

### 4. 🚀 Migration Process
- **Start Migration**: Click "Start Migration" (enabled when connections verified)
- **Parallel Processing**: Watch real-time updates with multi-threading info
- **Progress Tracking**: Monitor current table, records, and overall progress
- **Worker Monitoring**: Track parallel workers and processing efficiency

### 5. 📈 Progress Monitoring
- **Live Updates**: Real-time progress bars and status information
- **Detailed Logs**: Comprehensive logging with timestamps
- **System Resources**: Monitor memory and CPU during migration
- **Error Handling**: Automatic error detection and reporting

## ⚙️ Database Configuration

### 📝 Environment Variables (.env file)
Create a `.env` file in the project root with your database configuration:

```env
# MySQL Source Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=your_source_database

# PostgreSQL Target Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_postgres_username
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DATABASE=your_target_database

# Application Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
```

### 🔐 Security Best Practices
- Use strong passwords for database connections
- Store sensitive data in environment variables
- Consider using SSL/TLS for production databases
- Regularly rotate database credentials

### 📊 Database Requirements

#### MySQL Source Database
- **Host**: Your MySQL server host (default: localhost)
- **Port**: MySQL port (default: 3306)
- **Username**: MySQL username with appropriate permissions
- **Password**: MySQL password
- **Database**: Source database name
- **Permissions**: SELECT, SHOW TABLES, DESCRIBE

#### PostgreSQL Target Database
- **Host**: Your PostgreSQL server host (default: localhost)
- **Port**: PostgreSQL port (default: 5432)
- **Username**: PostgreSQL username with appropriate permissions
- **Password**: PostgreSQL password
- **Database**: Target database name
- **Permissions**: CREATE, INSERT, SELECT, DROP

## 🔍 Connection Testing

### 🌐 Web Interface Testing
The application includes comprehensive built-in connection testing:

- **🔄 Automatic Testing**: Connections tested automatically on page load
- **🔘 Manual Testing**: Click "Test Connections" button for on-demand verification
- **📊 Real-time Status**: Live connection status, table counts, and response times
- **✅ Pre-migration Validation**: Migration blocked until both databases are connected
- **📈 Performance Metrics**: Connection response times and database statistics

### 💻 Command Line Testing
Use the provided test scripts in the `test_connection/` folder:

#### 🔬 Comprehensive Test
```bash
# Run locally
python test_connection/test_mysql_connection.py

# Run inside Docker container
docker-compose exec app python test_connection/test_mysql_connection.py
```

**Features:**
- ✅ Configuration validation
- ✅ Connection testing with detailed output
- ✅ Database information (version, size, table count)
- ✅ Table listing (first 10 tables)
- ✅ Error handling and detailed reporting

#### ⚡ Simple Test
```bash
# Run locally
python test_connection/test_mysql_simple.py

# Run inside Docker container
docker-compose exec app python test_connection/test_mysql_simple.py
```

**Features:**
- ✅ Quick connection verification
- ✅ Basic database information
- ✅ Minimal output for automation

#### 🚀 One-liner Test
```bash
# Test MySQL connection inside container
docker-compose exec app python -c "
import os, mysql.connector; 
from dotenv import load_dotenv; 
load_dotenv(); 
conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'), 
    port=int(os.getenv('MYSQL_PORT', 3306)), 
    user=os.getenv('MYSQL_USER'), 
    password=os.getenv('MYSQL_PASSWORD'), 
    database=os.getenv('MYSQL_DATABASE')
); 
print('✅ MySQL Connected!'); 
conn.close()
"
```

## Sample Data

The Docker setup includes sample data with the following tables:
- `users` - User information
- `products` - Product catalog
- `orders` - Order records
- `order_items` - Order line items

## Docker Services

- **app**: Flask application (port 5000)
- **mysql**: MySQL 8.0 database (port 3306)
- **postgres**: PostgreSQL 13 database (port 5432)

## Development

### Auto-reload Feature
The application automatically reloads when you make changes to the code, making development efficient.

### File Structure
```
project/
├── app.py                 # Main Flask application
├── database_manager.py    # Database connection and migration logic
├── system_monitor.py      # System monitoring and resource management
├── templates/
│   └── index.html        # Web interface
├── test_connection/       # Database connection testing scripts
│   ├── test_mysql_connection.py  # Comprehensive MySQL connection test
│   └── test_mysql_simple.py      # Simple MySQL connection test
├── sample_data/
│   └── init.sql          # Sample MySQL data
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
├── .env                 # Environment variables (create this file)
└── README.md           # This file
```

## Data Type Mapping

The application automatically maps MySQL data types to PostgreSQL equivalents:

| MySQL Type | PostgreSQL Type |
|------------|-----------------|
| INT, INTEGER | INTEGER |
| BIGINT | BIGINT |
| VARCHAR | VARCHAR |
| TEXT | TEXT |
| DECIMAL | DECIMAL |
| FLOAT, DOUBLE | DOUBLE PRECISION |
| DATETIME, TIMESTAMP | TIMESTAMP |
| DATE | DATE |
| TIME | TIME |
| BLOB | BYTEA |
| JSON | JSON |

## Error Handling

The application includes comprehensive error handling for:
- Database connection failures
- Table creation errors
- Data insertion issues
- Network connectivity problems

## 🚀 Multi-threading and Performance Features

### ⚡ Parallel Processing Architecture
- **🔄 Table-level Parallelism**: Multiple tables migrate simultaneously using ThreadPoolExecutor
- **📦 Batch-level Parallelism**: Within each table, record batches process in parallel
- **💻 CPU Core Utilization**: Configurable number of workers (default: 3 cores)
- **🧠 Memory-aware Batching**: Dynamic batch size adjustment based on system memory
- **🔒 Thread-safe Operations**: All database operations protected with proper locking

### 📈 Performance Benefits
- **⚡ 2-4x Faster Migration**: Significant speed improvement with parallel processing
- **🎯 Efficient Resource Usage**: Optimal utilization of available CPU cores
- **📊 Scalable Processing**: Automatically adapts to system capabilities
- **📱 Real-time Monitoring**: Live updates of parallel worker status and performance
- **🔄 Adaptive Batching**: Memory-aware batch sizing for optimal performance

### 🔗 Connection Management
- **🔌 Dedicated Connections**: Each thread gets its own database connections
- **🏊 Connection Pooling**: Efficient connection management and cleanup
- **🛡️ Error Isolation**: Thread failures don't affect other parallel operations
- **🧹 Resource Cleanup**: Automatic connection cleanup on completion or failure
- **⚖️ Load Balancing**: Intelligent distribution of work across available threads

### 📊 Performance Metrics
| Configuration | Performance Improvement |
|---------------|------------------------|
| 1 Worker | Baseline (1x) |
| 2 Workers | ~2x faster |
| 3 Workers | ~2.7x faster |
| 4 Workers | ~4x faster |

*Performance improvements may vary based on system resources and database size.*

## 📊 System Monitoring Features

### 🧠 Memory Management
- **📈 Real-time Monitoring**: Continuous monitoring of system and process memory usage
- **⚡ Automatic Control**: Dynamic batch size adjustment based on memory pressure
- **⚠️ Memory Limits**: Configurable memory limits with automatic warnings
- **🗑️ Garbage Collection**: Manual and automatic memory cleanup
- **📊 Memory History**: Track memory usage patterns over time

### 💻 CPU Management
- **⚙️ Configurable Cores**: Set the number of CPU cores to use (default: 3)
- **⚖️ Load Balancing**: Efficient distribution of processing across available cores
- **📊 Performance Monitoring**: Real-time CPU usage tracking
- **🔄 Adaptive Processing**: Automatic adjustment based on system load

### 📈 System Information
- **💾 Memory Usage**: Total, available, and process-specific memory information
- **🖥️ CPU Utilization**: Current CPU usage percentage and core allocation
- **⚠️ System Warnings**: Automatic alerts for high memory usage
- **📊 History Tracking**: Memory and CPU usage history for analysis
- **🎯 Performance Metrics**: Real-time performance indicators

### 🔌 API Endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/system_info` | GET | Get current system information |
| `/api/system_config` | GET | Get current system configuration |
| `/api/system_config` | POST | Update system configuration |
| `/api/memory_history` | GET | Get memory usage history |
| `/api/force_gc` | POST | Manually trigger garbage collection |
| `/api/database_status` | GET | Test database connections and get status |
| `/api/database_config` | GET | Get database configuration (without passwords) |
| `/api/start_migration` | POST | Start database migration process |
| `/api/status` | GET | Get current migration status |

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Consider using SSL/TLS for database connections
- Implement proper authentication for production use

## 🔧 Troubleshooting

### 🚨 Common Issues

#### 1. **Connection Refused**
- ✅ Ensure databases are running and accessible
- ✅ Test connections using the built-in connection tester
- ✅ Verify host, port, and network connectivity
- ✅ Check firewall settings
- ✅ Confirm database services are started

#### 2. **Permission Denied**
- ✅ Check database user permissions
- ✅ Ensure user has CREATE, INSERT, SELECT privileges
- ✅ Verify database names are correct
- ✅ Check user authentication credentials

#### 3. **Port Conflicts**
- ✅ Modify ports in docker-compose.yml if needed
- ✅ Check if ports are already in use
- ✅ Use `netstat -tulpn | grep :PORT` to check port usage

#### 4. **Memory Issues**
- ✅ Increase Docker memory limits for large datasets
- ✅ Monitor memory usage during migration
- ✅ Use garbage collection if memory usage is high
- ✅ Adjust batch sizes in system configuration

#### 5. **Migration Fails to Start**
- ✅ Ensure both database connections are successful
- ✅ Test connections using the web interface or command line tools
- ✅ Check .env file configuration
- ✅ Verify all required environment variables are set

### 🔍 Connection Testing
Use the provided tools to diagnose connection issues:

```bash
# Comprehensive connection test
python test_connection/test_mysql_connection.py

# Test inside Docker container
docker-compose exec app python test_connection/test_mysql_connection.py

# Quick connection test
docker-compose exec app python test_connection/test_mysql_simple.py

# Test both databases via API
curl http://localhost:5001/api/database_status
```

### 📋 Logs and Debugging
Check the application logs for detailed error information:

```bash
# Application logs
docker-compose logs app

# All services logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f app

# Check specific service logs
docker-compose logs mysql
docker-compose logs postgres
```

### 🆘 Getting Help
If you encounter issues not covered here:
1. Check the application logs for detailed error messages
2. Verify your .env configuration
3. Test database connections using the provided tools
4. Ensure all prerequisites are met
5. Check system resources (memory, CPU, disk space)

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### 🚀 Getting Started
1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper documentation
4. **Test thoroughly** using the provided test scripts
5. **Submit a pull request** with a clear description

### 📝 Development Guidelines
- Follow Python PEP 8 style guidelines
- Add tests for new features
- Update documentation for any changes
- Ensure all tests pass before submitting
- Use meaningful commit messages

### 🐛 Reporting Issues
- Use the issue tracker to report bugs
- Include detailed reproduction steps
- Provide system information and logs
- Check existing issues before creating new ones

### 💡 Feature Requests
- Describe the feature clearly
- Explain the use case and benefits
- Consider implementation complexity
- Discuss with maintainers before major changes

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

<div align="center">

**⭐ Star this repository if you find it helpful!**

Made with ❤️ for the developer community

</div>
