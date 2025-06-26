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
            # Calculate additional metrics for banking settlement
            summary_df = df.copy()
            
            
            # Calculate derived metrics
            summary_df['settlement_with_banking'] = summary_df['total_intra_settlement'] + summary_df['total_inter_settlement']
            summary_df['total_settlement'] = summary_df['settlement_with_banking'] + summary_df['total_matched_settled_sum']
            
            # Calculate surplus demand after banking
            summary_df['surplus_demand_after_banking'] = (
                summary_df['surplus_demand_sum'].fillna(0)
                - summary_df['total_matched_settled_sum'].fillna(0)
                - summary_df['total_intra_settlement'].fillna(0)
                - summary_df['total_inter_settlement'].fillna(0)
            ).clip(lower=0)
            
            # Calculate totals for metric boxes
            total_generation_mwh = summary_df['total_generation_sum'].sum() / 1000 if 'total_generation_sum' in summary_df.columns else 0
            loss_percentage = 2.8  
            total_generation_after_loss_mwh = total_generation_mwh * (1 - loss_percentage/100)
            total_consumption_mwh = summary_df['total_consumption_sum'].sum() / 1000 if 'total_consumption_sum' in summary_df.columns else 0
            total_settlement_mwh = summary_df['total_settlement'].sum() / 1000
            total_surplus_demand_after_banking_mwh = summary_df['surplus_demand_after_banking'].sum() / 1000
            
            # Calculate replacement percentage with banking
            replacement_percentage_with_banking = (
                (total_settlement_mwh / total_consumption_mwh) * 100 
                if total_consumption_mwh > 0 else 0
            )
            
            # Add CSS to style metric containers
            st.markdown("""
            <style>
            [data-testid="metric-container"] [data-testid="metric-container-label"] {
                font-size: 0.9em;
                font-weight: bold;
            }
            [data-testid="metric-container"] [data-testid="metric-container-value"] {
                font-size: 0.7em;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Create 5 horizontal boxes with main metrics using Streamlit columns
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric(
                    label="Total Generation",
                    value=f"{total_generation_mwh:.0f} MWh"
                )
            with col2:
                st.metric(
                    label="Generation (after loss)",
                    value=f"{total_generation_after_loss_mwh:.0f} MWh",
                    help=f"Generation after {loss_percentage}% transmission/distribution loss"
                )
            with col3:
                st.metric(
                    label="Total Consumption",
                    value=f"{total_consumption_mwh:.0f} MWh"
                )
            with col4:
                st.metric(
                    label="Replacement (with Banking) %",
                    value=f"{replacement_percentage_with_banking:.0f}%",
                    help="Percentage of consumption met by generation including banking settlement"
                )
            with col5:
                st.metric(
                    label="Surplus Demand (after Banking)",
                    value=f"{total_surplus_demand_after_banking_mwh:.0f} MWh",
                    help="Remaining demand after considering all banking settlements"
                )
            
            # Customize the summary dataframe for display
            display_df = summary_df.copy()
            
            # Select and rename columns for display
            columns_to_display = {
                'month': 'Month',
                'total_matched_settled_sum': 'Settlement (Without Banking)',
                'settlement_with_banking': 'Settlement (With Banking)',
                'total_settlement': 'Total Settlement',
                # 'total_consumption_sum': 'Consumption'
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






