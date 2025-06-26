import pandas as pd
from db.safe_db_utils import safe_read_sql


def fetch_all_plants(conn) -> pd.DataFrame:
    """
    Fetch all rows from the tbl_plants table.

    Args:
        conn: MySQL connection object.

    Returns:
        pd.DataFrame: All plant records.
    """
    query = "SELECT * FROM tbl_plants"
    return safe_read_sql(query, conn)




def fetch_plant_by_id(conn, plant_id: str) -> pd.DataFrame:
    """
    Fetch plant details based on plant_id.

    Args:
        conn: MySQL connection object.
        plant_id (str): The plant ID to filter on.

    Returns:
        pd.DataFrame: Matching plant record(s).
    """
    query = "SELECT * FROM tbl_plants WHERE plant_id = %s"
    return safe_read_sql(query, conn, (plant_id,))




def fetch_plants_by_client(conn, client_name: str) -> pd.DataFrame:
    """
    Fetch plant details for a given client_name.

    Args:
        conn: MySQL connection object.
        client_name (str): The client name to filter on.

    Returns:
        pd.DataFrame: All plant records for that client.
    """
    query = "SELECT * FROM tbl_plants WHERE client_name = %s"
    return safe_read_sql(query, conn, (client_name,))

