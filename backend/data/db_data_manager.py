"""
Database Data Manager
Handles data loading and management for the dashboard
"""

import pandas as pd
import logging
from typing import Dict, List, Optional
from db.db_setup import CONN
from db.safe_db_utils import safe_read_sql

def get_plants() -> Dict[str, Dict[str, List[str]]]:
    """
    Fetch all plants from the database and organize by client and type
    
    Returns:
        Dictionary with structure:
        {
            'client_name': {
                'solar': ['plant1', 'plant2'],
                'wind': ['plant3', 'plant4']
            }
        }
    """
    if CONN is None:
        logging.error("Database connection not available")
        return {}
    
    try:
        # Query to get all unique client names from settlement_data
        query = """
        SELECT DISTINCT client_name 
        FROM settlement_data 
        WHERE client_name IS NOT NULL 
        ORDER BY client_name
        """
        
        df = safe_read_sql(query, CONN)
        
        if df.empty:
            logging.warning("No clients found in settlement_data table")
            return {}
        
        # For now, we'll create a mock structure since we don't have plant type info
        # In a real implementation, you would have a plants table with type information
        client_data = {}
        
        for client in df['client_name'].tolist():
            # Mock plant data - in reality, this would come from a plants table
            client_data[client] = {
                'solar': [f"{client}_Solar_Plant"],
                'wind': [f"{client}_Wind_Plant"] if client != "Combined_Client" else []
            }
        
        logging.info(f"Loaded {len(client_data)} clients")
        return client_data
        
    except Exception as e:
        logging.error(f"Error fetching plants: {str(e)}")
        return {}

def get_client_plants(client_name: str) -> Dict[str, List[str]]:
    """
    Get plants for a specific client
    
    Args:
        client_name: Name of the client
        
    Returns:
        Dictionary with solar and wind plant lists
    """
    all_plants = get_plants()
    return all_plants.get(client_name, {'solar': [], 'wind': []})

def load_client_data() -> Dict[str, Dict[str, List[str]]]:
    """
    Load client data with error handling and caching
    
    Returns:
        Client data dictionary
    """
    try:
        return get_plants()
    except Exception as e:
        logging.error(f"Failed to load client data: {str(e)}")
        return {}

def validate_client_plant_selection(client_name: str, plant_name: str) -> bool:
    """
    Validate if a plant belongs to a client
    
    Args:
        client_name: Name of the client
        plant_name: Name of the plant
        
    Returns:
        True if valid, False otherwise
    """
    client_plants = get_client_plants(client_name)
    all_plants = client_plants['solar'] + client_plants['wind']
    return plant_name in all_plants

def get_plant_type(client_name: str, plant_name: str) -> Optional[str]:
    """
    Get the type of a plant (solar or wind)
    
    Args:
        client_name: Name of the client
        plant_name: Name of the plant
        
    Returns:
        'solar', 'wind', or None if not found
    """
    client_plants = get_client_plants(client_name)
    
    if plant_name in client_plants['solar']:
        return 'solar'
    elif plant_name in client_plants['wind']:
        return 'wind'
    else:
        return None

def get_available_date_range(client_name: str, plant_name: str = None) -> Dict[str, str]:
    """
    Get the available date range for a client/plant
    
    Args:
        client_name: Name of the client
        plant_name: Name of the plant (optional)
        
    Returns:
        Dictionary with 'min_date' and 'max_date'
    """
    if CONN is None:
        return {'min_date': None, 'max_date': None}
    
    try:
        query = """
        SELECT MIN(date) as min_date, MAX(date) as max_date
        FROM settlement_data
        WHERE client_name = %s
        """
        params = [client_name]
        
        # If specific plant is provided, add it to the filter
        # Note: This assumes you have a plant_name column in settlement_data
        # Adjust based on your actual database schema
        
        df = safe_read_sql(query, CONN, params)
        
        if not df.empty and df.iloc[0]['min_date'] is not None:
            return {
                'min_date': df.iloc[0]['min_date'].strftime('%Y-%m-%d'),
                'max_date': df.iloc[0]['max_date'].strftime('%Y-%m-%d')
            }
        else:
            return {'min_date': None, 'max_date': None}
            
    except Exception as e:
        logging.error(f"Error getting date range: {str(e)}")
        return {'min_date': None, 'max_date': None}

def check_data_availability(client_name: str, plant_name: str, start_date: str, end_date: str) -> bool:
    """
    Check if data is available for the given parameters
    
    Args:
        client_name: Name of the client
        plant_name: Name of the plant
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        True if data is available, False otherwise
    """
    if CONN is None:
        return False
    
    try:
        query = """
        SELECT COUNT(*) as count
        FROM settlement_data
        WHERE client_name = %s 
        AND date BETWEEN %s AND %s
        """
        
        df = safe_read_sql(query, CONN, [client_name, start_date, end_date])
        
        return df.iloc[0]['count'] > 0 if not df.empty else False
        
    except Exception as e:
        logging.error(f"Error checking data availability: {str(e)}")
        return False

def get_data_summary(client_name: str) -> Dict:
    """
    Get summary statistics for a client
    
    Args:
        client_name: Name of the client
        
    Returns:
        Dictionary with summary statistics
    """
    if CONN is None:
        return {}
    
    try:
        query = """
        SELECT 
            COUNT(DISTINCT date) as total_days,
            MIN(date) as first_date,
            MAX(date) as last_date,
            SUM(allocated_generation) as total_generation,
            SUM(consumption) as total_consumption,
            AVG(allocated_generation) as avg_generation,
            AVG(consumption) as avg_consumption
        FROM settlement_data
        WHERE client_name = %s
        """
        
        df = safe_read_sql(query, CONN, [client_name])
        
        if not df.empty:
            return {
                'total_days': int(df.iloc[0]['total_days']) if df.iloc[0]['total_days'] else 0,
                'first_date': df.iloc[0]['first_date'].strftime('%Y-%m-%d') if df.iloc[0]['first_date'] else None,
                'last_date': df.iloc[0]['last_date'].strftime('%Y-%m-%d') if df.iloc[0]['last_date'] else None,
                'total_generation': float(df.iloc[0]['total_generation']) if df.iloc[0]['total_generation'] else 0,
                'total_consumption': float(df.iloc[0]['total_consumption']) if df.iloc[0]['total_consumption'] else 0,
                'avg_generation': float(df.iloc[0]['avg_generation']) if df.iloc[0]['avg_generation'] else 0,
                'avg_consumption': float(df.iloc[0]['avg_consumption']) if df.iloc[0]['avg_consumption'] else 0
            }
        else:
            return {}
            
    except Exception as e:
        logging.error(f"Error getting data summary: {str(e)}")
        return {}