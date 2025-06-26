import streamlit as st
from db.fetch_tod_tab_data import fetch_combined_monthly_data
from db.db_setup import CONN
from visualizations.power_cost_calculations import calculate_monthly_power_costs, summarize_costs_table, calculate_monthly_costs_without_banking, summarize_costs_table_without_banking
from visualizations.power_cost_visual import plot_costs_with_banking, plot_costs_without_banking
def display_power_cost_analysis(selected_plant):
    
    # Power cost input section with right-aligned input
    col_left, col_right = st.columns([3, 1])

    with col_left:
        # Add radio button for banking option selection
        banking_option = st.radio(
            "Select Analysis Type:",
            options=["Without Banking", "With Banking"],
            index=0,  # Default to "Without Banking"
            horizontal=True,
            help="Choose whether to include banking in the power cost analysis"
        )

    with col_right:
        # Compact grid power cost input in right corner
        grid_rate = st.number_input(
            "Grid Cost (₹/kWh)",
            min_value=0.01,  # Changed from 0.0 to prevent division issues
            max_value=50.0,
            value=4.0,
            step=0.1,
            help="Enter grid electricity cost per kWh"
        )

    # Add error handling and validation
    try:
        # Validate grid_rate
        if grid_rate is None or grid_rate <= 0:
            st.error("Please enter a valid grid cost value greater than 0")
            return
            
        # Fetch data with error handling
        main_df = fetch_combined_monthly_data(CONN, selected_plant)
        
        if main_df is None or main_df.empty:
            st.warning("No data available for the selected plant")
            return
            
    except Exception as e:
        st.error(f"An error occurred while processing the data: {str(e)}")
        print(f"Error in power cost analysis: {e}")
        return
    
    # Display content based on selected banking option
    if banking_option == "With Banking":
        try:
            # Calculate costs with banking
            df_calculated = calculate_monthly_power_costs(main_df, grid_rate)
            
            if df_calculated is None or df_calculated.empty:
                st.warning("Unable to calculate power costs with the current data")
                return

            # Get summary data
            summary = summarize_costs_table(df_calculated)
            
            st.subheader("With Banking")
            # Display as metrics in table format
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Grid Cost",
                    f"₹{summary.iloc[0]['Total Grid Cost (₹)']:.0f}",
                    help="Total cost if all energy was purchased from grid"
                )

            with col2:
                st.metric(
                    "Actual Cost",
                    f"₹{summary.iloc[0]['Total Actual Cost (₹)']:.0f}",
                    help="Actual cost after solar/wind generation offset"
                )

            with col3:
                st.metric(
                    "Total Savings",
                    f"₹{summary.iloc[0]['Total Savings (₹)']:.0f}",
                    delta=f"{summary.iloc[0]['Savings (%)']:.1f}%",
                    help="Total money saved due to renewable generation"
                )

            with col4:
                st.metric(
                    "Energy Offset",
                    f"{summary.iloc[0]['Energy Offset']:.0f} kWh",
                    help="Total energy offset by renewable generation"
                )

            # Plot chart
            fig = plot_costs_with_banking(df_calculated, selected_plant)
            if fig:
                st.pyplot(fig)
            else:
                st.warning("⚠️ No chart generated for the selected data.")
            
            # Display the detailed table
            st.subheader("Monthly Power Cost Analysis (With Banking)")
            st.dataframe(df_calculated, use_container_width=True)
            
        except Exception as e:
            st.error(f"An error occurred while processing the with banking data: {str(e)}")
            print(f"Error in with banking analysis: {e}")
    
    else:  # Without Banking
        try:
            # Calculate costs without banking
            df_calculated_without_banking = calculate_monthly_costs_without_banking(main_df, grid_rate)
            
            if df_calculated_without_banking is None or df_calculated_without_banking.empty:
                st.warning("Unable to calculate power costs without banking with the current data")
                return
            
            # Get summary data without banking
            summary_without_banking = summarize_costs_table_without_banking(df_calculated_without_banking)
            
            st.subheader("Without Banking")
            # Display as metrics in table format for Without Banking
            col1_nb, col2_nb, col3_nb, col4_nb = st.columns(4)
            
            with col1_nb:
                st.metric(
                    "Total Grid Cost",
                    f"₹{summary_without_banking.iloc[0]['Total Grid Cost (₹)']:.0f}",
                    help="Total cost if all energy was purchased from grid"
                )

            with col2_nb:
                st.metric(
                    "Actual Cost",
                    f"₹{summary_without_banking.iloc[0]['Total Actual Cost (₹)']:.0f}",
                    help="Actual cost after solar/wind generation offset"
                )

            with col3_nb:
                st.metric(
                    "Total Savings",
                    f"₹{summary_without_banking.iloc[0]['Total Savings (₹)']:.0f}",
                    delta=f"{summary_without_banking.iloc[0]['Average Savings (%)']:.1f}%",
                    help="Total money saved due to renewable generation"
                )

            with col4_nb:
                st.metric(
                    "Energy Offset",
                    f"{summary_without_banking.iloc[0]['Energy Offset']:.0f} kWh",
                    help="Total energy offset by renewable generation"
                )

            # Plot chart
            fig = plot_costs_without_banking(df_calculated_without_banking, selected_plant)
            if fig:
                st.pyplot(fig)
            else:
                st.warning("⚠️ No chart generated for the selected data.")
            
            # Display the detailed table without banking
            st.subheader("Monthly Power Cost Analysis (Without Banking)")
            st.dataframe(df_calculated_without_banking, use_container_width=True)
            
        except Exception as e:
            st.error(f"An error occurred while processing the without banking data: {str(e)}")
            print(f"Error in without banking analysis: {e}")


