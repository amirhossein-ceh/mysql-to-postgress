# MySQL to PostgreSQL Migration Tool

A Flask-based web application that migrates data from MySQL to PostgreSQL with real-time progress tracking and a beautiful user interface.

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

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone and navigate to the project directory:**
   ```bash
   cd /Users/amir/Desktop/projects/modaam
   ```

2. **Start the application with sample data:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Open your browser and go to `http://localhost:5000`
   - The application will start with sample MySQL and PostgreSQL databases

### Manual Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up your databases:**
   - MySQL database with your source data
   - PostgreSQL database for the target data

3. **Run the application:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - Open your browser and go to `http://localhost:5000`

## Usage

1. **Configure System Resources:**
   - Set the number of CPU cores to use (default: 3)
   - Set memory limit in MB (default: 1024 MB)
   - Click "Update Configuration" to apply changes

2. **Monitor System Resources:**
   - View real-time memory usage and CPU utilization
   - Monitor process memory consumption
   - Check for memory warnings
   - Force garbage collection if needed

3. **Configure Database Connections:**
   - Fill in your MySQL source database details
   - Fill in your PostgreSQL target database details

4. **Start Migration:**
   - Click the "Start Migration" button
   - Watch the real-time progress updates

5. **Monitor Progress:**
   - View current table being migrated
   - Track tables and records progress
   - Read detailed logs in real-time
   - Monitor system resources during migration

## Database Configuration

### MySQL Source Database
- **Host**: Your MySQL server host (default: localhost)
- **Port**: MySQL port (default: 3306)
- **Username**: MySQL username
- **Password**: MySQL password
- **Database**: Source database name

### PostgreSQL Target Database
- **Host**: Your PostgreSQL server host (default: localhost)
- **Port**: PostgreSQL port (default: 5432)
- **Username**: PostgreSQL username
- **Password**: PostgreSQL password
- **Database**: Target database name

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
├── sample_data/
│   └── init.sql          # Sample MySQL data
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose setup
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

## System Monitoring Features

### Memory Management
- **Real-time Monitoring**: Continuous monitoring of system and process memory usage
- **Automatic Control**: Dynamic batch size adjustment based on memory pressure
- **Memory Limits**: Configurable memory limits with automatic warnings
- **Garbage Collection**: Manual and automatic memory cleanup

### CPU Management
- **Configurable Cores**: Set the number of CPU cores to use (default: 3)
- **Load Balancing**: Efficient distribution of processing across available cores
- **Performance Monitoring**: Real-time CPU usage tracking

### System Information
- **Memory Usage**: Total, available, and process-specific memory information
- **CPU Utilization**: Current CPU usage percentage and core allocation
- **System Warnings**: Automatic alerts for high memory usage
- **History Tracking**: Memory and CPU usage history for analysis

### API Endpoints
- `GET /api/system_info` - Get current system information
- `GET /api/system_config` - Get current system configuration
- `POST /api/system_config` - Update system configuration
- `GET /api/memory_history` - Get memory usage history
- `POST /api/force_gc` - Manually trigger garbage collection

## Security Notes

- Change default passwords in production
- Use environment variables for sensitive data
- Consider using SSL/TLS for database connections
- Implement proper authentication for production use

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure databases are running and accessible
2. **Permission Denied**: Check database user permissions
3. **Port Conflicts**: Modify ports in docker-compose.yml if needed
4. **Memory Issues**: Increase Docker memory limits for large datasets

### Logs
Check the application logs for detailed error information:
```bash
docker-compose logs app
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
