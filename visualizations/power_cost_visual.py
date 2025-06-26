import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

def format_rupees_lakhs(x, _):
    return f"₹{x / 1e5:.1f}L" if x >= 1e5 else f"₹{x:.0f}"

def plot_costs_without_banking(df: pd.DataFrame, plant_name: str) -> plt.Figure:
    """
    Plot Grid Cost vs Actual Cost (without banking logic), formatted in Lakhs.
    """
    df = df.copy()
    df['month'] = pd.to_datetime(df['Date'] + '-01')
    df = df.sort_values('month')
    df['month_str'] = df['month'].dt.strftime('%b %Y')
    x = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, df['Grid Cost (₹)'], label='Grid Cost', marker='o', linewidth=2.5, color='#1E88E5')
    ax.plot(x, df['Actual Cost (₹)'], label='Actual Cost', marker='s', linestyle='--', linewidth=2.5, color='#E53935')

    for i, val in enumerate(df['Savings (₹)']):
        ax.text(
            x[i],
            max(df['Grid Cost (₹)'].iloc[i], df['Actual Cost (₹)'].iloc[i]) * 1.02,
            f"₹{val / 1e5:.2f}L",  # Format in Lakhs
            ha='center',
            fontsize=9,
            color='gray'
        )

    ax.set_title(f"Monthly Cost without Banking\n{plant_name}", fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Cost (₹ in Lakhs)")
    ax.set_xticks(x)
    ax.set_xticklabels(df['month_str'], rotation=45, ha='right')
    ax.yaxis.set_major_formatter(FuncFormatter(format_rupees_lakhs))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', frameon=False)

    plt.tight_layout()
    return fig





def plot_costs_with_banking(df: pd.DataFrame, plant_name: str) -> plt.Figure:
    """
    Plot Grid Cost vs Actual Cost (with banking logic), formatted in Lakhs.
    """
    df = df.copy()
    df['month'] = pd.to_datetime(df['Date'] + '-01')
    df = df.sort_values('month')
    df['month_str'] = df['month'].dt.strftime('%b %Y')
    x = np.arange(len(df))

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(x, df['Grid Cost (₹)'], label='Grid Cost', marker='o', linewidth=2.5, color='#1E88E5')
    ax.plot(x, df['Actual Cost (₹)'], label='Actual Cost', marker='s', linestyle='--', linewidth=2.5, color='#43A047')

    for i, val in enumerate(df['Savings (₹)']):
        ax.text(
            x[i],
            max(df['Grid Cost (₹)'].iloc[i], df['Actual Cost (₹)'].iloc[i]) * 1.02,
            f"₹{val / 1e5:.2f}L",   # Display in Lakhs
            ha='center',
            fontsize=9,
            color='gray'
        )

    ax.set_title(f"Monthly Cost with Banking\n{plant_name}", fontsize=14)
    ax.set_xlabel("Month")
    ax.set_ylabel("Cost (₹ in Lakhs)")
    ax.set_xticks(x)
    ax.set_xticklabels(df['month_str'], rotation=45, ha='right')
    ax.yaxis.set_major_formatter(FuncFormatter(format_rupees_lakhs))
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend(loc='upper right', frameon=False)

    plt.tight_layout()
    return fig
