import pandas as pd
from db.safe_db_utils import safe_read_sql



def fetch_generation_consumption_data(
    conn,
    client_name: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch enriched generation and consumption data from settlement_data.

    - Single day: return raw slot-wise rows without aggregation
    - Multi-day: return daily aggregated totals

    Returns:
        pd.DataFrame with:
        - datetime (for single day) or date (for multi-day)
        - generation, consumption, deficit, surplus_demand, surplus_generation, settled
    """
    if conn is None:
        return pd.DataFrame()

    is_single_day = start_date == end_date

    if is_single_day:
        # No aggregation, raw records per slot
        query = """
            SELECT datetime,
                   allocated_generation AS generation,
                   consumption,
                   deficit,
                   surplus_demand,
                   surplus_generation,
                   settled
            FROM settlement_data
            WHERE client_name = %s AND date = %s
            ORDER BY datetime;
        """
        df = safe_read_sql(query, conn, (client_name, start_date))
        df['datetime'] = pd.to_datetime(df['datetime'])

    else:
        # Aggregate for each date
        query = """
            SELECT date,
                   SUM(allocated_generation) AS generation,
                   SUM(consumption) AS consumption,
                   SUM(deficit) AS deficit,
                   SUM(surplus_demand) AS surplus_demand,
                   SUM(surplus_generation) AS surplus_generation,
                   SUM(settled) AS settled
            FROM settlement_data
            WHERE client_name = %s AND date BETWEEN %s AND %s
            GROUP BY date
            ORDER BY date;
        """
        df = safe_read_sql(query, conn, (client_name, start_date, end_date))
        df['date'] = pd.to_datetime(df['date'])

    return df



def fetch_unitwise_consumption_and_generation(
    conn,
    client_name: str,
    start_date: str,
    end_date: str
) -> pd.DataFrame:
    """
    Fetch aggregated consumption and allocated generation grouped by cons_unit
    for the specified client and date range.
    
    Returns:
        pd.DataFrame with columns:
        - cons_unit
        - consumption
        - allocated_generation
    """
    if conn is None:
        return pd.DataFrame()

    query = """
        SELECT cons_unit,
               SUM(consumption) AS consumption,
               SUM(allocated_generation) AS allocated_generation
        FROM settlement_data
        WHERE client_name = %s
          AND date BETWEEN %s AND %s
        GROUP BY cons_unit
        ORDER BY cons_unit;
    """
    
    df = safe_read_sql(query, conn, (client_name, start_date, end_date))

    # Safety: ensure numeric columns are of numeric type
    df['consumption'] = pd.to_numeric(df['consumption'], errors='coerce').fillna(0)
    df['allocated_generation'] = pd.to_numeric(df['allocated_generation'], errors='coerce').fillna(0)

    return df
