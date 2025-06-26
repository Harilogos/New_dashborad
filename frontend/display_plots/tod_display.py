import streamlit as st
from db.fetch_tod_tab_data import (
    fetch_tod_binned_data, 
    fetch_combined_monthly_data,
    fetch_all_daily_tod_data,
    fetch_daily_tod_data
)
from visualizations.tod_tab_visual import (
    create_monthly_before_banking_plot, 
    create_monthly_banking_settlement_chart, 
    create_tod_binned_plot,
    create_tod_generation_plot,
    create_tod_consumption_plot
)
from db.db_setup import CONN


def display_monthly_tod_before_banking(selected_plant):
    try:
        df = fetch_all_daily_tod_data(CONN, selected_plant)
        if df.empty:
            st.warning("No data available for the selected plant.")
            return

        fig = create_monthly_before_banking_plot(df, selected_plant)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Failed to generate plot.")
    except Exception as e:
        st.error("❌ Error displaying monthly ToD before banking.")
        print(f"[display_monthly_tod_before_banking] Error: {e}")


def display_monthly_banking_settlement(selected_plant):
    try:
        df = fetch_combined_monthly_data(CONN, selected_plant)
        if df.empty:
            st.warning("No monthly banking settlement data found.")
            return

        fig, summary_df = create_monthly_banking_settlement_chart(df, selected_plant)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Failed to generate banking settlement chart.")

        if not summary_df.empty:
            # Customize the summary dataframe for display
            display_df = summary_df.copy()
            
            # Select and rename columns for display
            columns_to_display = {
                'month_str': 'Month',
                'settlement_without_banking': 'Settlement (Without Banking)',
                'settlement_with_banking': 'Settlement (With Banking)',
                'total_settlement': 'Total Settlement',
                # 'consumption': 'Consumption'
            }
            
            # Filter and rename columns
            display_df = display_df[list(columns_to_display.keys())].rename(columns=columns_to_display)
            
            st.subheader("📊 Monthly Banking Settlement Summary")
            st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No summary data to display.")

    except Exception as e:
        st.error("❌ Error displaying banking settlement.")
        print(f"[display_monthly_banking_settlement] Error: {e}")


def display_tod_generation_vs_consumptiont(selected_plant, start_date, end_date=None):
    try:
        df = fetch_tod_binned_data(CONN, selected_plant, start_date, end_date)
        if df.empty:
            st.warning("No ToD generation vs consumption data found.")
            return

        fig = create_tod_binned_plot(df, selected_plant, start_date, end_date)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Plot could not be generated.")

    except Exception as e:
        st.error("❌ Error displaying ToD Generation vs Consumption plot.")
        print(f"[display_tod_generation_vs_consumptiont] Error: {e}")


def display_tod_generation(selected_plant, start_date, end_date=None):
    try:
        df = fetch_daily_tod_data(CONN, selected_plant, start_date, end_date)
        if df.empty:
            st.warning("No generation data found for the selected period.")
            return

        # # Create ToD table
        # is_multiple_days = start_date != end_date and end_date is not None
        
        # if is_multiple_days:
        #     # Group by date and slot for multiple days
        #     summary_df = df.groupby(['date', 'slot'])['generation_kwh'].sum().reset_index()
        #     summary_df['generation_mwh'] = summary_df['generation_kwh'] / 1000
            
        #     # Calculate percentage for each date
        #     date_totals = summary_df.groupby('date')['generation_mwh'].sum().reset_index()
        #     date_totals.rename(columns={'generation_mwh': 'date_total'}, inplace=True)
            
        #     summary_df = summary_df.merge(date_totals, on='date')
        #     summary_df['percentage'] = (summary_df['generation_mwh'] / summary_df['date_total'] * 100).round(1)
            
        #     # Prepare display dataframe
        #     display_df = summary_df[['date', 'slot', 'generation_mwh', 'percentage']].copy()
        #     display_df.columns = ['Date', 'ToD', 'Generation (MWh)', 'Percentage (%)']
            
        # else:
        #     # Single day - group by slot only
        #     summary_df = df.groupby('slot')['generation_kwh'].sum().reset_index()
        #     summary_df['generation_mwh'] = summary_df['generation_kwh'] / 1000
            
        #     # Calculate percentage
        #     total_generation = summary_df['generation_mwh'].sum()
        #     summary_df['percentage'] = (summary_df['generation_mwh'] / total_generation * 100).round(1) if total_generation > 0 else 0
            
        #     # Prepare display dataframe
        #     display_df = summary_df[['slot', 'generation_mwh', 'percentage']].copy()
        #     display_df.columns = ['ToD', 'Generation (MWh)', 'Percentage (%)']
        
        

        fig = create_tod_generation_plot(df, selected_plant, start_date, end_date)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Failed to generate generation plot.")

        # Display the summary table
        # st.dataframe(display_df, use_container_width=True)
        
    except Exception as e:
        st.error("❌ Error displaying ToD Generation.")
        print(f"[display_tod_generation] Error: {e}")


def display_tod_consumption(selected_plant, start_date, end_date=None):
    try:
        df = fetch_daily_tod_data(CONN, selected_plant, start_date, end_date)
        if df.empty:
            st.warning("No consumption data available.")
            return

        # # Create ToD table
        # is_multiple_days = start_date != end_date and end_date is not None
        
        # if is_multiple_days:
        #     # Group by date and slot for multiple days
        #     summary_df = df.groupby(['date', 'slot'])['consumption_kwh'].sum().reset_index()
        #     summary_df['consumption_mwh'] = summary_df['consumption_kwh'] / 1000
            
        #     # Calculate percentage for each date
        #     date_totals = summary_df.groupby('date')['consumption_mwh'].sum().reset_index()
        #     date_totals.rename(columns={'consumption_mwh': 'date_total'}, inplace=True)
            
        #     summary_df = summary_df.merge(date_totals, on='date')
        #     summary_df['percentage'] = (summary_df['consumption_mwh'] / summary_df['date_total'] * 100).round(1)
            
        #     # Prepare display dataframe
        #     display_df = summary_df[['date', 'slot', 'consumption_mwh', 'percentage']].copy()
        #     display_df.columns = ['Date', 'ToD', 'Consumption (MWh)', 'Percentage (%)']
            
        # else:
        #     # Single day - group by slot only
        #     summary_df = df.groupby('slot')['consumption_kwh'].sum().reset_index()
        #     summary_df['consumption_mwh'] = summary_df['consumption_kwh'] / 1000
            
        #     # Calculate percentage
        #     total_consumption = summary_df['consumption_mwh'].sum()
        #     summary_df['percentage'] = (summary_df['consumption_mwh'] / total_consumption * 100).round(1) if total_consumption > 0 else 0
            
        #     # Prepare display dataframe
        #     display_df = summary_df[['slot', 'consumption_mwh', 'percentage']].copy()
        #     display_df.columns = ['ToD', 'Consumption (MWh)', 'Percentage (%)']
        
        

        fig = create_tod_consumption_plot(df, selected_plant, start_date, end_date)
        if fig:
            st.pyplot(fig)
        else:
            st.warning("Failed to generate consumption plot.")

        # Display the summary table
        # st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        st.error("❌ Error displaying ToD Consumption.")
        print(f"[display_tod_consumption] Error: {e}")






