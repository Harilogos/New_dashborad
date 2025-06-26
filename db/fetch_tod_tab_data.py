import pandas as pd
from db.safe_db_utils import safe_read_sql


##ToD Generation vs Consumption
def fetch_tod_binned_data(conn, client_name: str, start_date: str, end_date: str = None) -> pd.DataFrame:
    """
    Fetch ToD-binned generation and consumption data from MySQL using mysql.connector.

    Args:
        conn: mysql.connector connection object.
        plant_id (str): Plant ID to filter on.
        start_date (str): Start date (YYYY-MM-DD).
        end_date (str, optional): End date (YYYY-MM-DD). If None, uses only start_date.

    Returns:
        pd.DataFrame: Data grouped by slot_name.
    """
    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        if not end_date:
            end_date = start_date

        query = """
            SELECT 
                slot_name AS slot,
                SUM(allocated_generation) AS generation_kwh,
                SUM(consumption) AS consumption_kwh
            FROM 
                settlement_data
            WHERE 
                client_name = %s
                AND date BETWEEN %s AND %s
            GROUP BY 
                slot_name
            ORDER BY 
                slot_name;
        """

        cursor.execute(query, (client_name, start_date, end_date))
        results = cursor.fetchall()
        
        # Consume all results to avoid "Unread result found" error
        while cursor.nextset():
            pass
            
        return pd.DataFrame(results)
        
    except Exception as e:
        print(f"Error in fetch_tod_binned_data: {e}")
        return pd.DataFrame()
    finally:
        if cursor:
            cursor.close()




##ToD Generation AND Consumption
def fetch_daily_tod_data(
    conn,
    client_name: str,
    start_date: str,
    end_date: str,
    plant_type: str = None
) -> pd.DataFrame:
    """
    Fetch daily ToD-binned generation and consumption data using slot_name and date directly.

    Returns:
        pd.DataFrame with columns: date, slot, generation_kwh, consumption_kwh
    """
    query = """
        SELECT
            date,
            slot_name AS slot,
            SUM(allocated_generation) AS generation_kwh,
            SUM(consumption) AS consumption_kwh
        FROM
            settlement_data
        WHERE
            client_name = %s
            AND date BETWEEN %s AND %s
    """

    params = [client_name, start_date, end_date]

    if plant_type:
        query += " AND type = %s"
        params.append(plant_type)

    query += """
        GROUP BY date, slot_name
        ORDER BY date, slot_name;
    """

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Consume all results to avoid "Unread result found" error
        while cursor.nextset():
            pass

        return pd.DataFrame(rows)

    except Exception as e:
        print(f"Error in fetch_daily_tod_data: {e}")
        return pd.DataFrame(columns=["date", "slot", "generation_kwh", "consumption_kwh"])
    finally:
        if cursor:
            cursor.close()




##Monthly ToD Before Banking


def fetch_all_daily_tod_data(
    conn,
    client_name: str,
    plant_type: str = None
) -> pd.DataFrame:
    """
    Fetch all available daily ToD-binned generation and consumption data
    grouped by date and slot_name, without any date filtering.

    Returns:
        pd.DataFrame with columns: date, slot, generation_kwh, consumption_kwh
    """
    query = """
        SELECT
            date,
            slot_name AS slot,
            SUM(allocated_generation) AS generation_kwh,
            SUM(consumption) AS consumption_kwh
        FROM
            settlement_data
        WHERE
            client_name = %s
    """

    params = [client_name]

    if plant_type:
        query += " AND type = %s"
        params.append(plant_type)

    query += """
        GROUP BY date, slot_name
        ORDER BY date, FIELD(slot_name, 'Morning Peak', 'Day (Normal)', 'Evening Peak', 'Off-Peak');
    """

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # Consume all results to avoid "Unread result found" error
        while cursor.nextset():
            pass

        return pd.DataFrame(rows)

    except Exception as e:
        print("⚠️ Error fetching data:", e)
        return pd.DataFrame(columns=["date", "slot", "generation_kwh", "consumption_kwh"])
    finally:
        if cursor:
            cursor.close()




##Monthly Banking Settlement
def fetch_combined_monthly_data(
    conn,
    plant_name: str = None
) -> pd.DataFrame:
    """
    Fetch monthly aggregated data for both consumption and banking settlement.

    Args:
        conn: MySQL connection object
        plant_name (str, optional): Filter by plant name

    Returns:
        pd.DataFrame: Merged DataFrame with month-wise consumption and settlement data
    """

    # --- Fetch Daily Consumption ---
    consumption_query = """
        SELECT
            date,
            consumption
        FROM
            settlement_data
        WHERE
            date IS NOT NULL
            {plant_filter}
        ORDER BY
            date;
    """

    # --- Fetch Monthly Banking Settlement ---
    settlement_query = """
        SELECT
            date AS month,
            SUM(matched_settled_sum) AS total_matched_settled_sum,
            SUM(intra_settlement) AS total_intra_settlement,
            SUM(inter_settlement) AS total_inter_settlement
        FROM
            banking_settlement
        WHERE
            date IS NOT NULL
            {plant_filter}
        GROUP BY
            date
        ORDER BY
            date;
    """

    # Prepare query and params
    params = ()
    if plant_name:
        consumption_query = consumption_query.format(plant_filter="AND client_name = %s")
        settlement_query = settlement_query.format(plant_filter="AND client_name = %s")
        params = (plant_name,)
    else:
        consumption_query = consumption_query.format(plant_filter="")
        settlement_query = settlement_query.format(plant_filter="")

    try:
        # Read consumption data and group by month using safe database utility
        df_consumption = safe_read_sql(consumption_query, conn, params)
        
        if df_consumption.empty:
            print("Warning: No consumption data found")
            return pd.DataFrame()
            
        df_consumption['date'] = pd.to_datetime(df_consumption['date'])
        df_consumption['month'] = df_consumption['date'].dt.to_period('M').astype(str)
        df_consumption_monthly = (
            df_consumption.groupby('month', as_index=False)['consumption']
            .sum()
            .rename(columns={'consumption': 'total_consumption_sum'})
        )

        # Read banking settlement data (already monthly) using safe database utility
        df_settlement = safe_read_sql(settlement_query, conn, params)
        
        if df_settlement.empty:
            print("Warning: No settlement data found")
            # Return consumption data only with zeros for settlement columns
            df_consumption_monthly['total_matched_settled_sum'] = 0
            df_consumption_monthly['total_intra_settlement'] = 0
            df_consumption_monthly['total_inter_settlement'] = 0
            return df_consumption_monthly
            
        df_settlement['month'] = pd.to_datetime(df_settlement['month']).dt.to_period('M').astype(str)

        # Merge both on 'month'
        df_combined = pd.merge(
            df_consumption_monthly,
            df_settlement,
            on='month',
            how='outer'
        ).sort_values('month').reset_index(drop=True)

        return df_combined
        
    except Exception as e:
        print(f"Error in fetch_combined_monthly_data: {e}")
        return pd.DataFrame()
