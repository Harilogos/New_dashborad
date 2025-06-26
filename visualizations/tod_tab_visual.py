
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter
import matplotlib.dates as mdates
from .tod_config import get_slot_order, get_slot_color_map, normalize_slot_name, add_slot_labels_with_time

def format_thousands(x, pos):
    return f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'


##Monthly ToD Before Banking

def create_monthly_before_banking_plot(df: pd.DataFrame, plant_name: str):
    """
    Create monthly ToD-wise generation vs. consumption stacked bar chart.
    """
    fig, ax = plt.subplots(figsize=(14, 8))

    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center', fontsize=14, color='red')
        ax.set_title(f"{plant_name} - Monthly Before Banking", fontsize=16)
        return fig

    # Step 1: Extract month
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.to_period('M').astype(str)

    # Step 2: Normalize slots
    df['slot'] = df['slot'].apply(normalize_slot_name)

    # Step 3: Pivot tables
    gen_pivot = df.pivot_table(index='month', columns='slot', values='generation_kwh', aggfunc='sum', fill_value=0)
    cons_pivot = df.pivot_table(index='month', columns='slot', values='consumption_kwh', aggfunc='sum', fill_value=0)

    # Step 4: Order and align columns
    slot_order = list(reversed(get_slot_order()))  # Top-down visual stacking
    slot_colors = get_slot_color_map()

    for slot in slot_order:
        if slot not in gen_pivot.columns:
            gen_pivot[slot] = 0.0
        if slot not in cons_pivot.columns:
            cons_pivot[slot] = 0.0
    gen_pivot = gen_pivot[slot_order].astype(float)
    cons_pivot = cons_pivot[slot_order].astype(float)

    # Step 5: Plot
    x = np.arange(len(gen_pivot.index))
    bar_width = 0.4
    months = gen_pivot.index.tolist()

    gen_bottom = np.zeros(len(x))
    cons_bottom = np.zeros(len(x))

    legend_items = []

    for slot in slot_order:
        gen_bar = ax.bar(
            x - bar_width / 2,
            gen_pivot[slot].values,
            bar_width,
            bottom=gen_bottom,
            color=slot_colors.get(slot, '#aaa'),
            edgecolor='white',
            label=f'Gen {slot}'
        )
        gen_bottom += gen_pivot[slot].values
        legend_items.append((f'Gen {slot}', gen_bar[0]))

        cons_bar = ax.bar(
            x + bar_width / 2,
            cons_pivot[slot].values,
            bar_width,
            bottom=cons_bottom,
            color=slot_colors.get(slot, '#aaa'),
            edgecolor='black',
            hatch='///',
            label=f'Cons {slot}'
        )
        cons_bottom += cons_pivot[slot].values
        legend_items.append((f'Cons {slot}', cons_bar[0]))

    # Add total labels
    for i in range(len(x)):
        g_total = gen_bottom[i]
        c_total = cons_bottom[i]
        if g_total > 0:
            ax.text(x[i] - bar_width/2, g_total + g_total * 0.02, f"{g_total:.0f}", ha='center', va='bottom', fontsize=9, color='green')
        if c_total > 0:
            ax.text(x[i] + bar_width/2, c_total + c_total * 0.02, f"{c_total:.0f}", ha='center', va='bottom', fontsize=9, color='darkred')

    # Final touches
    ax.set_xticks(x)
    ax.set_xticklabels(months, rotation=45, ha='right')
    ax.set_ylabel("Energy (kWh)", fontsize=12)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_title(f"{plant_name} - Monthly Before Banking Settlement (ToD-wise)", fontsize=14)
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    ax.grid(True, axis='y', linestyle='--', alpha=0.5)

    # Custom legend ordering: all Gen first, then Cons, both in stack order
    gen_legend = [item for item in legend_items if item[0].startswith("Gen")][::-1]
    cons_legend = [item for item in legend_items if item[0].startswith("Cons")][::-1]

    # Remove duplicates (if any), preserve order
    def deduplicate(items):
        seen = set()
        return [(l, h) for l, h in items if not (l in seen or seen.add(l))]

    ordered_legend_items = deduplicate(gen_legend) + deduplicate(cons_legend)

    ax.legend(
        [h for _, h in ordered_legend_items],
        [l for l, _ in ordered_legend_items],
        loc='upper left',
        bbox_to_anchor=(1.01, 1),
        frameon=False
    )

    plt.tight_layout()
    return fig




##Monthly Banking Settlement
def create_monthly_banking_settlement_chart(df: pd.DataFrame, plant_name: str) -> tuple[plt.Figure, pd.DataFrame]:
    """
    Create a chart showing monthly banking settlement breakdown (line + pie), integrating consumption + unsettled logic.
    """
    # Rename columns for clarity
    df = df.rename(columns={
        'total_matched_settled_sum': 'settlement_without_banking',
        'total_intra_settlement': 'intra_settlement',
        'total_inter_settlement': 'inter_settlement',
        'total_consumption_sum': 'consumption'
    })

    # Ensure datetime format and sorting
    df['month'] = pd.to_datetime(df['month'] + '-01')
    df = df.sort_values('month')

    # Derived metrics
    df['settlement_with_banking'] = df['intra_settlement'] + df['inter_settlement']
    df['total_settlement'] = df['settlement_with_banking'] + df['settlement_without_banking']
    df['replacement_percentage'] = np.where(
        df['consumption'] > 0,
        (df['total_settlement'] / df['consumption']) * 100,
        0
    )
    df['month_str'] = df['month'].dt.strftime('%b %Y')
    x = np.arange(len(df))

    # 🎨 Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # --- Line Chart ---
    ax1.plot(x, df['total_settlement'], label='Total Settlement', marker='o', linewidth=2.5, color="#2E7D32")
    ax1.plot(x, df['settlement_with_banking'], label='With Banking', marker='s', linestyle='--', linewidth=2, color="orange")
    ax1.plot(x, df['settlement_without_banking'], label='Without Banking', marker='^', linestyle=':', linewidth=2, color="green")

    # # Annotate Replacement %
    # for i, pct in enumerate(df['replacement_percentage']):
    #     ax1.text(
    #         x[i],
    #         df['total_settlement'].iloc[i] * 1.03,
    #         f"{pct:.1f}%",
    #         ha='center',
    #         va='bottom',
    #         fontsize=9,
    #         color='gray'
    #     )

    ax1.set_title(f"Monthly Banking Settlement\n{plant_name}", fontsize=14)
    ax1.set_xlabel("Month", fontsize=12)
    ax1.set_ylabel("Energy (kWh)", fontsize=12)
    ax1.set_xticks(x)
    ax1.set_xticklabels(df['month_str'], rotation=45, ha='right')
    ax1.yaxis.set_major_formatter(FuncFormatter(format_thousands))
    ax1.grid(True, axis='y', linestyle='--', alpha=0.6)
    ax1.legend(loc='upper left', frameon=False)

    # --- Pie Chart ---
    total_with_banking = df['settlement_with_banking'].sum()
    total_without_banking = df['settlement_without_banking'].sum()
    total_consumption = df['consumption'].sum()

    unsettled = total_consumption - (total_with_banking + total_without_banking)

    pie_values = [total_with_banking, total_without_banking, unsettled]
    pie_labels = ['With Banking', 'Without Banking', 'Unsettled']
    pie_colors = ['orange', 'green', 'gray']

    ax2.pie(
        pie_values,
        labels=pie_labels,
        colors=pie_colors,
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontsize': 11}
    )
    ax2.set_title("Total Banking Breakdown", fontsize=14)

    plt.tight_layout()
    return fig, df





###ToD Generation vs Consumption
def create_tod_binned_plot(
    df: pd.DataFrame,
    plant_name: str,
    start_date: str,
    end_date: str = None
):
    """
    Create a ToD-binned bar plot comparing generation vs. consumption.
    """

    if df.empty:
        raise ValueError("No data to plot")

    # ✅ Normalize slot names
    df['slot'] = df['slot'].apply(normalize_slot_name)

    # ✅ Melt the DataFrame for seaborn
    df_melted = df.melt(
        id_vars='slot',
        value_vars=['generation_kwh', 'consumption_kwh'],
        var_name='Type',
        value_name='kWh'
    )

    # ✅ Prepare order and labels
    slot_order = get_slot_order()
    slot_labels = add_slot_labels_with_time()

    # ✅ Setup seaborn style
    sns.set(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    # ✅ Create barplot
    sns.barplot(
        data=df_melted,
        x='slot',
        y='kWh',
        hue='Type',
        ax=ax,
        order=slot_order,
        palette={
            'generation_kwh': '#4CAF50',    # Green
            'consumption_kwh': '#FFC107'   # Amber
        },
        edgecolor='black',
        linewidth=0.5
    )

    # ✅ Add labels to each bar
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', label_type='edge', fontsize=8, padding=2)

    # ✅ Title and axis labels
    title_date = f"{start_date} to {end_date}" if end_date and end_date != start_date else start_date
    ax.set_title(f"ToD Binned Generation vs Consumption\n{plant_name} ({title_date})", fontsize=14)
    ax.set_xlabel("ToD Slot")
    ax.set_ylabel("Energy (kWh)")
    ax.legend(title="Type")

    # ✅ Set fixed x-ticks to avoid warning
    ax.set_xticks(range(len(slot_order)))
    ax.set_xticklabels([slot_labels.get(slot, slot) for slot in slot_order], rotation=45)

    plt.tight_layout()
    return fig





# from matplotlib import pyplot as plt
# import seaborn as sns
# import numpy as np
# from matplotlib.ticker import FuncFormatter


# def format_thousands(x, pos):
#     return f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'

# def create_tod_comparison_plot(df, plant_name, start_date, end_date=None):
#     if df.empty:
#         print("❌ No data to plot.")
#         return

#     sns.set(style="whitegrid")

#     # Normalize slot names
#     df['slot'] = df['slot'].apply(normalize_slot_name)

#     # Enforce slot order
#     slot_order = get_slot_order()
#     slot_colors = get_slot_color_map()
#     slot_labels = add_slot_labels_with_time()

#     # Aggregate by slot
#     df_grouped = df.groupby('slot', as_index=False)[['generation_kwh', 'consumption_kwh']].sum()
#     df_grouped['slot'] = pd.Categorical(df_grouped['slot'], categories=slot_order, ordered=True)
#     df_grouped = df_grouped.sort_values('slot')

#     fig, ax = plt.subplots(figsize=(10, 6))
#     bar_width = 0.35
#     x = np.arange(len(df_grouped))

#     for i, row in df_grouped.iterrows():
#         slot = row['slot']
#         color = slot_colors.get(slot, '#999999')

#         # Generation - solid
#         ax.bar(
#             x[i] - bar_width / 2,
#             row['generation_kwh'],
#             width=bar_width,
#             color=color,
#             edgecolor='black',
#             label='Generation' if i == 0 else None
#         )

#         # Consumption - hatched
#         ax.bar(
#             x[i] + bar_width / 2,
#             row['consumption_kwh'],
#             width=bar_width,
#             color=color,
#             edgecolor='black',
#             hatch='//',
#             label='Consumption' if i == 0 else None
#         )

#         # Value labels
#         ax.text(x[i] - bar_width / 2, row['generation_kwh'] + 200,
#                 f"{row['generation_kwh']:.0f}", ha='center', va='bottom', fontsize=8)
#         ax.text(x[i] + bar_width / 2, row['consumption_kwh'] + 200,
#                 f"{row['consumption_kwh']:.0f}", ha='center', va='bottom', fontsize=8)

#     label = f"{start_date} to {end_date}" if end_date and start_date != end_date else start_date
#     ax.set_title(f"ToD-Binned Generation vs Consumption\n{plant_name} ({label})", fontsize=14)
#     ax.set_ylabel("Energy (kWh)")
#     ax.set_xlabel("ToD Slot")
#     ax.set_xticks(x)
#     ax.set_xticklabels([slot_labels.get(slot, slot) for slot in df_grouped['slot']], rotation=45, ha='right')
#     ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

#     # Legend (remove duplicates)
#     handles, labels = ax.get_legend_handles_labels()
#     by_label = dict(zip(labels, handles))
#     ax.legend(by_label.values(), by_label.keys(), title="Type")

#     ax.grid(True, axis='y', linestyle='--', alpha=0.6)
#     plt.tight_layout()
#     return fig




##ToD Generation
def format_thousands(x, pos):
    return f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'




def create_tod_generation_plot(df: pd.DataFrame, plant_name: str, start_date: str, end_date: str = None):
    """
    Create a smart Seaborn-styled stacked bar chart of ToD slot-wise generation,
    with dynamic bar width, date tick intervals, total annotations, and ordered legend.
    """
    if df.empty:
        return

    sns.set(style="whitegrid")

    # Normalize input
    df['slot'] = df['slot'].apply(normalize_slot_name)
    df['date'] = pd.to_datetime(df['date'])
    df['generation_kwh'] = df['generation_kwh'].astype(float)

    # Load slot config
    slot_order = get_slot_order()
    slot_colors = get_slot_color_map()

    # Pivot to date × slot
    pivot_df = df.pivot_table(
        index='date',
        columns='slot',
        values='generation_kwh',
        aggfunc='sum',
        fill_value=0
    )
    for slot in slot_order:
        if slot not in pivot_df.columns:
            pivot_df[slot] = 0.0
    pivot_df = pivot_df[slot_order]

    # Plot config
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(pivot_df), dtype=float)
    dates = pivot_df.index

    total_days = (dates[-1] - dates[0]).days + 1
    bar_width = min(0.8, max(0.3, 20 / total_days))  # Dynamically scale width

    bar_handles = []

    # Plot stacked bars (bottom to top)
    for slot in reversed(slot_order):
        values = pivot_df[slot].values
        bar = ax.bar(
            dates,
            values,
            bottom=bottom,
            label=slot,
            color=slot_colors.get(slot, '#4CAF50'),
            edgecolor='white',
            width=bar_width
        )
        bar_handles.append((slot, bar[0]))
        bottom += values

    # Annotate inside bars
    for i, total in enumerate(bottom):
        ax.text(
            dates[i],
            total * 0.5,
            f"{total:.0f}",
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            color='black',
            rotation=90
        )

    # Axis labels and title
    ax.set_ylabel("Generation (kWh)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    label = f"{start_date} to {end_date}" if end_date and start_date != end_date else start_date
    ax.set_title(f"Daily ToD-wise Generation\n{plant_name} ({label})", fontsize=14)

    # Smart date formatting
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Format Y axis
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    # Ordered legend (bottom to top of stack = top to bottom of legend)
    legend_handles = [handle for name in slot_order for s, handle in reversed(bar_handles) if s == name]
    legend_labels = [name for name in slot_order]
    ax.legend(legend_handles, legend_labels, title="ToD Slot", loc='upper left', bbox_to_anchor=(1.01, 1), frameon=False)

    plt.tight_layout()
    return fig






##ToD Consumption

def create_tod_consumption_plot(df: pd.DataFrame, plant_name: str, start_date: str, end_date: str = None):
    """
    Create a smart stacked bar chart with Morning Peak on top and Night Off-Peak at the bottom,
    for ToD slot-wise consumption per day with dynamic bar width, x-axis handling, and legend ordering.
    """
    if df.empty:
        return

    sns.set(style="whitegrid")

    # Clean and normalize input
    df['slot'] = df['slot'].apply(normalize_slot_name)
    df['date'] = pd.to_datetime(df['date'])
    df['consumption_kwh'] = df['consumption_kwh'].astype(float)

    # Slot configuration
    slot_order = get_slot_order()
    slot_colors = get_slot_color_map()

    # Pivot table
    pivot_df = df.pivot_table(
        index='date',
        columns='slot',
        values='consumption_kwh',
        aggfunc='sum',
        fill_value=0
    )
    for slot in slot_order:
        if slot not in pivot_df.columns:
            pivot_df[slot] = 0.0
    pivot_df = pivot_df[slot_order]

    # Prepare for plotting
    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(pivot_df), dtype=float)
    dates = pivot_df.index

    total_days = (dates[-1] - dates[0]).days + 1
    bar_width = min(0.8, max(0.3, 20 / total_days))  # Adjust bar width dynamically

    bar_handles = []

    # Reverse slot order for stacking: bottom up
    for slot in reversed(slot_order):
        values = pivot_df[slot].values
        bars = ax.bar(
            dates,
            values,
            bottom=bottom,
            label=slot,
            color=slot_colors.get(slot, '#4CAF50'),
            edgecolor='white',
            width=bar_width
        )
        bar_handles.append((slot, bars[0]))  # Capture for legend
        bottom += values

    # Add value labels inside bars
    for i, total in enumerate(bottom):
        ax.text(
            dates[i],
            total * 0.5,
            f"{total:.0f}",
            ha='center',
            va='center',
            fontsize=9,
            fontweight='bold',
            color='black',
            rotation=90
        )

    # Styling
    ax.set_ylabel("Consumption (kWh)", fontsize=12)
    ax.set_xlabel("Date", fontsize=12)
    label = f"{start_date} to {end_date}" if end_date and start_date != end_date else start_date
    ax.set_title(f"Daily ToD-wise Consumption\n{plant_name} ({label})", fontsize=14)

    # Smart x-axis ticks
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

    # Format Y-axis
    ax.yaxis.set_major_formatter(FuncFormatter(format_thousands))

    # Ordered legend (from bottom to top stack)
    legend_handles = [handle for name in slot_order for s, handle in reversed(bar_handles) if s == name]
    legend_labels = [name for name in slot_order]
    ax.legend(legend_handles, legend_labels, title="ToD Slot", loc='upper left', bbox_to_anchor=(1.01, 1), frameon=False)

    plt.tight_layout()
    return fig








