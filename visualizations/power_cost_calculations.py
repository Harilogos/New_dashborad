import pandas as pd
from db.safe_db_utils import safe_read_sql

def fetch_combined_monthly_data(
    conn,
    client_name: str = None
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
    if client_name:
        consumption_query = consumption_query.format(plant_filter="AND client_name = %s")
        settlement_query = settlement_query.format(plant_filter="AND client_name = %s")
        params = (client_name,)
    else:
        consumption_query = consumption_query.format(plant_filter="")
        settlement_query = settlement_query.format(plant_filter="")

    # Read consumption data and group by month
    df_consumption = safe_read_sql(consumption_query, conn, params)
    df_consumption['date'] = pd.to_datetime(df_consumption['date'])
    df_consumption['month'] = df_consumption['date'].dt.to_period('M').astype(str)
    df_consumption_monthly = (
        df_consumption.groupby('month', as_index=False)['consumption']
        .sum()
        .rename(columns={'consumption': 'total_consumption_sum'})
    )

    # Read banking settlement data (already monthly)
    df_settlement = safe_read_sql(settlement_query, conn, params)
    df_settlement['month'] = pd.to_datetime(df_settlement['month']).dt.to_period('M').astype(str)

    # Merge both on 'month'
    df_combined = pd.merge(
        df_consumption_monthly,
        df_settlement,
        on='month',
        how='outer'
    ).sort_values('month').reset_index(drop=True)

    return df_combined





def calculate_monthly_power_costs(df: pd.DataFrame, grid_rate_per_kwh: float = 4.0) -> pd.DataFrame:
    """
    Calculate cost metrics and return in clean format with renamed columns.
    Args:
        df (pd.DataFrame): Combined DataFrame with columns:
            ['month', 'total_consumption_sum', 'total_matched_settled_sum', 
             'total_intra_settlement', 'total_inter_settlement']
        grid_rate_per_kwh (float): Grid rate in ₹ per kWh
    Returns:
        pd.DataFrame: Formatted with required columns
    """
    df = df.copy()
    # Fill NaNs to ensure safe arithmetic
    for col in ['total_consumption_sum', 'total_matched_settled_sum', 
                'total_intra_settlement', 'total_inter_settlement']:
        df[col] = df[col].fillna(0)
    # Calculate generation = all settled energy
    df['banked_settled_units'] = (
        df['total_matched_settled_sum'] +
        df['total_intra_settlement'] +
        df['total_inter_settlement']
    )
    # Net consumption = what still had to be bought from the grid
    df['grid_consumption'] = (df['total_consumption_sum'] - df['banked_settled_units']).clip(lower=0)
    # Costs
    df['grid_cost'] = df['total_consumption_sum'] * grid_rate_per_kwh
    df['actual_cost'] = df['grid_consumption'] * grid_rate_per_kwh
    df['savings'] = df['grid_cost'] - df['actual_cost']
    df['savings_percentage'] = round(df["savings"] / df["grid_cost"] * 100,2)
    
    
    # Final formatting
    df_final = df[[
        'month',
        'grid_cost',
        'actual_cost',
        'savings',
        'banked_settled_units',
        'savings_percentage'
    ]].rename(columns={
        'month': 'Date',
        'grid_cost': 'Grid Cost (₹)',
        'actual_cost': 'Actual Cost (₹)',
        'savings': 'Savings (₹)',
        'banked_settled_units' : 'Energy Offset',
        'savings_percentage' : 'Saving (%)'
    })
    return df_final


def summarize_costs_table(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize cost metrics from a monthly-level DataFrame and return a single-row summary table.
    Args:
        df (pd.DataFrame): DataFrame with monthly columns like:
            'Consumption (kWh)', 'Generation (kWh)', 'Net Consumption (kWh)',
            'Grid Cost (₹)', 'Actual Cost (₹)', 'Savings (₹)'
    Returns:
        pd.DataFrame: Single-row DataFrame with total and average metrics.
    """
   
    total_grid_cost = df['Grid Cost (₹)'].sum()
    total_actual_cost = df['Actual Cost (₹)'].sum()
    total_savings = df['Savings (₹)'].sum()
    total_energy_offset = df["Energy Offset"].sum()
    average_savings_percent = (
        (total_savings / total_grid_cost) * 100 if total_grid_cost != 0 else 0.0
    )
    summary_table = pd.DataFrame([{
       
        "Total Grid Cost (₹)": total_grid_cost,
        "Total Actual Cost (₹)": total_actual_cost,
        "Total Savings (₹)": total_savings,
        "Energy Offset"  : total_energy_offset,
        "Savings (%)": round(average_savings_percent, 2)
    }])
    return summary_table




def calculate_monthly_costs_without_banking(
    df: pd.DataFrame,
    grid_rate_per_kwh: float = 4.0
) -> pd.DataFrame:
    """
    Calculate monthly costs using raw consumption and allocated generation 
    (without banking/settlement adjustment).

    Args:
        df (pd.DataFrame): DataFrame with ['month', 'total_consumption_sum', 'allocated_generation']
        grid_rate_per_kwh (float): Rate in ₹ per kWh

    Returns:
        pd.DataFrame: Cost breakdown per month
    """
    df = df.copy()

    # Basic cost calculations
    df['grid_cost'] = df['total_consumption_sum'] * grid_rate_per_kwh
    df['net_consumption_kwh'] = (df['total_consumption_sum'] - df['total_matched_settled_sum']).clip(lower=0)
    df['actual_cost'] = df['net_consumption_kwh'] * grid_rate_per_kwh
    df['savings'] = df['grid_cost'] - df['actual_cost']
    df['savings_percentage'] = round(df["savings"] / df["grid_cost"] * 100,2)

    # Format the result
    df_final = df[[
        'month',
   
        'grid_cost',
        'actual_cost',
        'savings',
        'total_matched_settled_sum',
        'savings_percentage'
    ]].rename(columns={
        'month': 'Date',
       
        'grid_cost': 'Grid Cost (₹)',
        'actual_cost': 'Actual Cost (₹)',
        'savings': 'Savings (₹)',
        'total_matched_settled_sum' : 'Energy Offset',
        'savings_percentage' : 'Saving (%)'
    })

    return df_final




def summarize_costs_table_without_banking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Summarize total and average cost metrics for non-banking logic.

    Args:
        df (pd.DataFrame): DataFrame with:
            - Consumption (kWh)
            - Generation (kWh)
            - Net Consumption (kWh)
            - Grid Cost (₹)
            - Actual Cost (₹)
            - Savings (₹)

    Returns:
        pd.DataFrame: Single-row summary
    """
 
    total_grid_cost = df['Grid Cost (₹)'].sum()
    total_actual_cost = df['Actual Cost (₹)'].sum()
    total_savings = df['Savings (₹)'].sum()
    total_energy_offset = df["Energy Offset"].sum()

    average_savings_percent = (
        (total_savings / total_grid_cost) * 100 if total_grid_cost else 0
    )

    summary = pd.DataFrame([{
        
        "Total Grid Cost (₹)": total_grid_cost,
        "Total Actual Cost (₹)": total_actual_cost,
        "Total Savings (₹)": total_savings,
        "Energy Offset"  : total_energy_offset,
        "Average Savings (%)": round(average_savings_percent, 2)
    }])

    return summary
