import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import pandas as pd
from matplotlib.patches import Patch





def format_thousands(x, _):
    return f'{int(x):,}'

#####Generation VS Consumption
# def plot_generation_vs_consumption(
#     df: pd.DataFrame,
#     plant_display_name: str,
#     start_date: str,
#     end_date: str
# ):
#     """Area plot for generation vs. consumption with surplus bar chart for multiple days."""
#     if df.empty:
#         print("⚠️ No data available to plot.")
#         return

#     is_single_day = start_date == end_date
    
#     # Calculate surplus generation and demand if not already present
#     if 'surplus_generation' not in df.columns:
#         df['surplus_generation'] = df.apply(lambda row: max(0, row['generation'] - row['consumption']), axis=1)
#     if 'surplus_demand' not in df.columns:
#         df['surplus_demand'] = df.apply(lambda row: max(0, row['consumption'] - row['generation']), axis=1)
    
#     # Create subplots - single plot for single day, two plots for multiple days
#     if is_single_day:
#         fig, ax = plt.subplots(figsize=(16, 8))
#         axes = [ax]
#     else:
#         fig, axes = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})
#         ax = axes[0]
    
#     # Main area plot
#     if is_single_day:
#         x = df['datetime']
#         ax.set_xlabel("Time of Day", fontsize=12)
#         ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
#     else:
#         x = df['date']
#         ax.set_xlabel("Date", fontsize=12)
#         ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
#         # Set appropriate date locators based on date range
#         if len(df) > 30:
#             ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
#         else:
#             ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))

#     # Add line plots for generation and consumption
#     ax.plot(x, df['generation'], color='green', linewidth=2.5, marker='o', markersize=6, label='Generation')
#     ax.plot(x, df['consumption'], color='red', linewidth=2.5, marker='s', markersize=6, linestyle='--', label='Consumption')
    
#     # Add fill between curves to show surplus/deficit areas
#     ax.fill_between(x, df['generation'], df['consumption'], 
#                     where=(df['generation'] >= df['consumption']), 
#                     color='green', alpha=0.3, interpolate=True, label='Surplus Generation')
#     ax.fill_between(x, df['generation'], df['consumption'], 
#                     where=(df['generation'] < df['consumption']), 
#                     color='red', alpha=0.3, interpolate=True, label='Surplus Demand')

#     # Format labels and title
#     label = start_date if is_single_day else f"{start_date} to {end_date}"
#     ax.set_title(f"Generation vs Consumption for {plant_display_name} ({label})", 
#                 fontsize=16, fontweight='bold', pad=20)

#     ax.set_ylabel("Energy (kWh)", fontsize=12)
    
#     # Format y-axis with thousands formatter if values are large
#     if df[['generation', 'consumption']].max().max() > 1000:
#         ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.1f}K' if x >= 1000 else f'{x:.0f}'))
    
#     ax.legend(loc='upper right', fontsize=11)
#     ax.grid(True, linestyle='--', alpha=0.4)
    
#     # Format x-axis labels
#     plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    

#     # Add surplus bar chart for multiple days
#     if not is_single_day and len(axes) > 1:
#         ax2 = axes[1]
    
#         # Calculate net surplus and color logic
#         df['net_surplus'] = df['surplus_generation'] - df['surplus_demand']
#         colors = df['net_surplus'].apply(lambda x: 'green' if x > 0 else ('red' if x < 0 else 'gray'))
    
#         # Plot single bar per day with color indicating type
#         ax2.bar(df['date'], df['net_surplus'].abs(), 
#                 color=colors, alpha=0.7, width=0.8, label='Net Surplus')
    
#         # Axis and formatting
#         ax2.set_xlabel("Date", fontsize=12)
#         ax2.set_ylabel("Surplus Energy (kWh)", fontsize=12)
#         ax2.set_title("Daily Net Surplus (Generation or Demand)", fontsize=14, fontweight='bold')
#         ax2.grid(True, linestyle='--', alpha=0.4)
    
#         # Legend (custom patch)
#         from matplotlib.patches import Patch
#         legend_elements = [
#             Patch(facecolor='green', label='Surplus Generation'),
#             Patch(facecolor='red', label='Surplus Demand')
#         ]
#         ax2.legend(handles=legend_elements, loc='upper right', fontsize=10)
    
#         ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
#         if len(df) > 30:
#             ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
#         else:
#             ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    
#         if df['net_surplus'].abs().max() > 1000:
#             ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.1f}K'))
    
#         # ✅ Only apply rotation if ax2 exists
#         plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')


    
#     # Adjust layout
#     plt.tight_layout()
#     if not is_single_day and len(axes) > 1:
#         plt.subplots_adjust(hspace=0.3)
    
#     return fig



def plot_generation_vs_consumption(
    df: pd.DataFrame,
    plant_display_name: str,
    start_date: str,
    end_date: str
):
    """Area plot for generation vs. consumption with settled percentage plot for multiple days."""
    if df.empty:
        print("⚠️ No data available to plot.")
        return

    is_single_day = start_date == end_date

    if 'surplus_generation' not in df.columns:
        df['surplus_generation'] = df.apply(lambda row: max(0, row['generation'] - row['consumption']), axis=1)
    if 'surplus_demand' not in df.columns:
        df['surplus_demand'] = df.apply(lambda row: max(0, row['consumption'] - row['generation']), axis=1)

    if is_single_day:
        fig, ax = plt.subplots(figsize=(16, 8))
        axes = [ax]
    else:
        fig, axes = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})
        ax = axes[0]

    # Main area plot
    x = df['datetime'] if is_single_day else df['date']
    ax.set_xlabel("Time of Day" if is_single_day else "Date", fontsize=12)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M') if is_single_day else mdates.DateFormatter('%b %d'))

    if not is_single_day:
        if len(df) > 30:
            ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))

    ax.plot(x, df['generation'], color='green', linewidth=2.5, marker='o', markersize=6, label='Generation')
    ax.plot(x, df['consumption'], color='red', linewidth=2.5, marker='s', markersize=6, linestyle='--', label='Consumption')

    ax.fill_between(x, df['generation'], df['consumption'], 
                    where=(df['generation'] >= df['consumption']), 
                    color='green', alpha=0.3, interpolate=True, label='Surplus Generation')
    ax.fill_between(x, df['generation'], df['consumption'], 
                    where=(df['generation'] < df['consumption']), 
                    color='red', alpha=0.3, interpolate=True, label='Surplus Demand')

    label = start_date if is_single_day else f"{start_date} to {end_date}"
    ax.set_title(f"Generation vs Consumption for {plant_display_name} ({label})", 
                 fontsize=16, fontweight='bold', pad=20)

    ax.set_ylabel("Energy (kWh)", fontsize=12)

    if df[['generation', 'consumption']].max().max() > 1000:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.1f}K' if x >= 1000 else f'{x:.0f}'))

    ax.legend(loc='upper right', fontsize=11)
    ax.grid(True, linestyle='--', alpha=0.4)
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Replace surplus bar chart with settled percentage plot
    if not is_single_day and len(axes) > 1:
        ax2 = axes[1]

        # Compute settled percentage safely
        df['settled_percentage'] = df.apply(
            lambda row: 100 * row['settled'] / row['consumption'] if row['consumption'] > 0 else 0,
            axis=1
        )

        ax2.plot(df['date'], df['settled_percentage'], color='blue', linewidth=2.5, marker='d', markersize=6, label='Settled %')

        ax2.set_xlabel("Date", fontsize=12)
        ax2.set_ylabel("Settled (%)", fontsize=12)
        ax2.set_title("Daily Settled Percentage", fontsize=14, fontweight='bold')
        ax2.grid(True, linestyle='--', alpha=0.4)

        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
        if len(df) > 30:
            ax2.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        else:
            ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))

        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.0f}%'))
        ax2.set_ylim(0, max(120, df['settled_percentage'].max() * 1.1))

        ax2.legend(loc='upper right', fontsize=10)
        plt.setp(ax2.get_xticklabels(), rotation=45, ha='right')

    plt.tight_layout()
    if not is_single_day and len(axes) > 1:
        plt.subplots_adjust(hspace=0.3)

    return fig



##Generation



def create_generation_only_plot(df, plant_name, start_date, end_date=None):
    if df.empty or 'generation' not in df.columns:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=12)
        return fig

    is_single_day = end_date is None or start_date == end_date
    fig, ax = plt.subplots(figsize=(12, 6))

    if is_single_day:
        x = df['datetime']
        ax.plot(x, df['generation'], color='green', marker='o', linewidth=2)
        ax.set_xlabel("Time of Day")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    else:
        x = df['date']
        bars = ax.bar(x, df['generation'], color='green', alpha=0.8)

        # Add values inside bars rotated 90 degrees
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height * 0.5,
                f"{int(height):,}",
                ha='center',
                va='center',
                fontsize=9,
                rotation=90,
                color='white'
            )

        ax.set_xlabel("Date")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    ax.set_ylabel("Generation (kWh)")
    title = f"Generation - {plant_name}\n{start_date}"
    if not is_single_day:
        title += f" to {end_date}"
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()

    return fig



# ##Consumption
def create_consumption_plot(df, plant_name, start_date, end_date=None):
    fig, ax = plt.subplots(figsize=(12, 6))

    if df.empty or 'consumption' not in df.columns:
        ax.text(0.5, 0.5, 'No consumption data available', ha='center', va='center', fontsize=12, color='red')
        ax.set_title(f"Consumption - {plant_name}", fontsize=14, fontweight='bold')
        return fig

    is_single_day = end_date is None or start_date == end_date

    if is_single_day:
        df['datetime'] = pd.to_datetime(df['datetime'])
        df = df.groupby('datetime', as_index=False)['consumption'].sum()
        ax.plot(df['datetime'], df['consumption'], color='red', marker='o', linewidth=2)
        ax.set_xlabel("Time of Day")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator(interval=2))
        title = f"Consumption - {plant_name}\n{start_date}"
    else:
        df = df.groupby('date', as_index=False)['consumption'].sum()
        bars = ax.bar(df['date'], df['consumption'], color='red', alpha=0.8)

        # Add values inside bars rotated 90 degrees
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height * 0.5,
                f"{int(height):,}",
                ha='center',
                va='center',
                fontsize=9,
                rotation=90,
                color='black'
            )

        ax.set_xlabel("Date")
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
        title = f"Daily Consumption - {plant_name}\n{start_date}"

    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.set_ylabel("Consumption (kWh)")
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    ax.grid(True, linestyle='--', alpha=0.6)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    plt.tight_layout()

    return fig





def plot_consumption_and_generation_pie(df: pd.DataFrame, plant_display_name: str):
    """
    Create two pie charts side by side:
    - Consumption distribution by cons_unit
    - Allocated generation distribution by cons_unit
    """

    if df.empty or 'cons_unit' not in df.columns:
        print("⚠️ No data or missing 'cons_unit' column for pie chart plotting.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Consumption pie
    consumption_data = df.groupby('cons_unit')['consumption'].sum()
    axes[0].pie(
        consumption_data, 
        labels=consumption_data.index,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops={'edgecolor': 'w'}
    )
    axes[0].set_title(f'Consumption Distribution by cons_unit\n{plant_display_name}', fontsize=14, fontweight='bold')

    # Allocated generation pie
    generation_data = df.groupby('cons_unit')['allocated_generation'].sum()
    axes[1].pie(
        generation_data, 
        labels=generation_data.index,
        autopct='%1.1f%%',
        startangle=140,
        wedgeprops={'edgecolor': 'w'}
    )
    axes[1].set_title(f'Allocated Generation Distribution by cons_unit\n{plant_display_name}', fontsize=14, fontweight='bold')

    plt.tight_layout()
    return fig
