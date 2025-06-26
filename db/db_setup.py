import mysql.connector
from mysql.connector import pooling
import threading

# Global connection pool
_connection_pool = None
_pool_lock = threading.Lock()

def setup_db_connection_pool(host: str, user: str, password: str, database: str):
    """Setup a MySQL connection pool."""
    global _connection_pool
    try:
        config = {
            'user': user,
            'password': password,
            'host': host,
            'database': database,
            'pool_name': 'mypool',
            'pool_size': 10,
            'pool_reset_session': True,
            'autocommit': True,
            'consume_results': True
        }
        _connection_pool = mysql.connector.pooling.MySQLConnectionPool(**config)
        print("✅ Database connection pool established")
        return _connection_pool
    except mysql.connector.Error as err:
        print(f"❌ Database connection pool failed: {err}")
        return None

def get_db_connection():
    """Get a connection from the pool."""
    global _connection_pool
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                setup_db_connection_pool(
                    host="localhost",
                    user="root",
                    password="test123",
                    database="energy_db"
                )
    
    try:
        if _connection_pool:
            conn = _connection_pool.get_connection()
            conn.autocommit = True
            return conn
    except mysql.connector.Error as err:
        print(f"❌ Error getting connection from pool: {err}")
    
    return None

def setup_db_connection(host: str, user: str, password: str, database: str):
    """Establish and return a MySQL connection."""
    try:
        conn = mysql.connector.connect(
            host=host, 
            user=user, 
            password=password, 
            database=database,
            autocommit=True,
            consume_results=True
        )
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        return None





# Setup DB - Initialize the connection pool
setup_db_connection_pool(
    host="localhost",
    user="root",
    password="test123",
    database="energy_db"
)

# Legacy single connection for backward compatibility
CONN = setup_db_connection(
    host="localhost",
    user="root",
    password="test123",
    database="energy_db"
)