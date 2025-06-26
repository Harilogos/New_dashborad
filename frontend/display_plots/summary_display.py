
import streamlit as st
from db.db_setup import CONN
from db.fetch_summary_data import fetch_generation_consumption_data
from visualizations.summary_tab_visual import plot_generation_vs_consumption, create_generation_only_plot, create_consumption_plot


def display_generation_vs_consumption(selected_plant, start_date, end_date=None):
    # Convert dates to string format if they're date objects
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime('%Y-%m-%d')
       
    else:
        start_date_str = str(start_date)
    
    if end_date is None:
        end_date_str = start_date_str
    elif hasattr(end_date, 'strftime'):
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        end_date_str = str(end_date)
   

    try:
        df = fetch_generation_consumption_data(CONN, selected_plant, start_date_str, end_date_str)
        
        
        if df is not None and not df.empty:

            fig = plot_generation_vs_consumption(
                df=df,
                plant_display_name=selected_plant,
                start_date=start_date_str,
                end_date=end_date_str
            )
            if fig:
                st.pyplot(fig)
            else:
                st.warning("⚠️ No chart generated for the selected data.")

                
            # Calculate metrics
            total_generation_kwh = df['generation'].sum()
            total_consumption_kwh = df['consumption'].sum()
            total_settled_kwh = df['settled'].sum()
            total_surplus_demand_kwh = df['surplus_demand'].sum()
            
            # Convert to MWh
            total_generation_mwh = total_generation_kwh / 1000
            total_consumption_mwh = total_consumption_kwh / 1000
            total_settled_mwh = total_settled_kwh / 1000
            surplus_demand_mwh = total_surplus_demand_kwh / 1000
            
            # Calculate generation after loss (2.8% loss)
            loss_percentage = 2.8
            total_generation_after_loss_mwh = total_generation_mwh * (1 - loss_percentage / 100)
            
            # Calculate replacement percentage (without Banking)
            replacement_percentage = (total_settled_mwh / total_consumption_mwh * 100) if total_consumption_mwh > 0 else 0
            
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
                    label="Replacement (without Banking) %",
                    value=f"{replacement_percentage:.0f}%",
                    help="Percentage of consumption (without Banking) met by generation"
                )
            with col5:
                st.metric(
                    label="Surplus Demand",
                    value=f"{surplus_demand_mwh:.0f} MWh",
                    help="Demand that couldn't be met by generation (from settlement data)"
                )
            
            
        else:
            st.warning("⚠️ No data available for the selected plant and date range.")
    except Exception as e:
        st.error(f"❌ Error loading generation vs consumption data: {str(e)}")
        st.exception(e)



    
def display_generation_only(selected_plant, start_date, end_date=None):
    # Convert dates to string format if they're date objects
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime('%Y-%m-%d')
    else:
        start_date_str = str(start_date)
    
    if end_date is None:
        end_date_str = start_date_str
    elif hasattr(end_date, 'strftime'):
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        end_date_str = str(end_date)

    try:
        df = fetch_generation_consumption_data(CONN, selected_plant, start_date_str, end_date_str)
        
        if df is not None and not df.empty:
            fig = create_generation_only_plot(
                df=df,
                plant_name=selected_plant,
                start_date=start_date_str,
                end_date=end_date_str
            )
            if fig:
                st.pyplot(fig)
            else:
                st.warning("⚠️ No generation chart generated for the selected data.")
        else:
            st.warning("⚠️ No generation data available for the selected plant and date range.")
    except Exception as e:
        st.error(f"❌ Error loading generation data: {str(e)}")
        st.exception(e)




def display_consumption_only(selected_plant, start_date, end_date=None):
    # Convert dates to string format if they're date objects
    if hasattr(start_date, 'strftime'):
        start_date_str = start_date.strftime('%Y-%m-%d')
    else:
        start_date_str = str(start_date)
    
    if end_date is None:
        end_date_str = start_date_str
    elif hasattr(end_date, 'strftime'):
        end_date_str = end_date.strftime('%Y-%m-%d')
    else:
        end_date_str = str(end_date)

    try:
        df = fetch_generation_consumption_data(CONN, selected_plant, start_date_str, end_date_str)
        
        if df is not None and not df.empty:
            fig = create_consumption_plot(
                df=df,
                plant_name=selected_plant,
                start_date=start_date_str,
                end_date=end_date_str
            )
            if fig:
                st.pyplot(fig)
            else:
                st.warning("⚠️ No consumption chart generated for the selected data.")
        else:
            st.warning("⚠️ No consumption data available for the selected plant and date range.")
    except Exception as e:
        st.error(f"❌ Error loading consumption data: {str(e)}")
        st.exception(e)