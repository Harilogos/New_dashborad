"""
Safe database utility functions to handle MySQL connection issues
"""
import pandas as pd
import mysql.connector
from contextlib import contextmanager
from db.db_setup import get_db_connection, CONN

@contextmanager
def safe_db_connection():
    """Context manager for safe database connections"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            conn = CONN  # Fallback to global connection
        yield conn
    except Exception as e:
        print(f"Database connection error: {e}")
        yield None
    finally:
        if conn and hasattr(conn, 'close'):
            try:
                # Ensure all results are consumed before closing
                if hasattr(conn, '_cnx') and conn._cnx:
                    conn._cnx.consume_results()
                conn.close()
            except:
                pass

def safe_read_sql(query, conn, params=None):
    """Safely execute SQL query and return DataFrame"""
    try:
        # Create a new connection for this specific query to avoid conflicts
        with safe_db_connection() as safe_conn:
            if safe_conn is None:
                return pd.DataFrame()
            
            # Use pandas read_sql with the safe connection
            if params:
                df = pd.read_sql(query, safe_conn, params=params)
            else:
                df = pd.read_sql(query, safe_conn)
            
            return df
            
    except Exception as e:
        print(f"Error in safe_read_sql: {e}")
        return pd.DataFrame()

def safe_execute_query(query, params=None):
    """Safely execute query with cursor and return results"""
    with safe_db_connection() as conn:
        if conn is None:
            return []
            
        cursor = None
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            
            # Consume all remaining results
            while cursor.nextset():
                pass
                
            return results
            
        except Exception as e:
            print(f"Error in safe_execute_query: {e}")
            return []
        finally:
            if cursor:
                cursor.close()