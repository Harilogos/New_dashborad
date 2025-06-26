"""
Solar & Wind Energy Generation Dashboard
Main Streamlit Application
"""

import streamlit as st
from datetime import datetime, timedelta
import logging

# Import configuration
from config.app_config import PAGE_CONFIG, MESSAGES, FEATURES

# Import dashboard components
from frontend.ui_components.dashboard_controls import (
    create_client_plant_filters,
    create_date_filters,
    setup_page,
    apply_custom_css
)

# Import display functions
from frontend.display_plots.summary_display import (
    display_generation_vs_consumption,
    display_generation_only,
    display_consumption_only
)
from frontend.display_plots.tod_display import (
    display_monthly_tod_before_banking,
    display_monthly_banking_settlement,
    display_tod_generation_vs_consumptiont,
    display_tod_generation,
    display_tod_consumption
)

from frontend.display_plots.power_cost_display import (
    display_power_cost_analysis
)

# Import data management
from backend.data.db_data_manager import load_client_data
from db.db_setup import CONN

def main():
    """Main application function"""
    
    # Setup page configuration
    setup_page()
    
    # Apply custom CSS
    apply_custom_css()
    
    # Initialize error logging
    logging.basicConfig(level=logging.INFO)
    
    try:
        # Load client data
        with st.spinner("Loading client data..."):
            client_data = load_client_data()
        
        # Create sidebar controls
        st.sidebar.markdown("""
        <div style='background: linear-gradient(90deg, #1E88E5, #42A5F5); 
                    padding: 1rem; margin: -1rem -1rem 1rem -1rem; 
                    border-radius: 0.5rem;'>
            <h2 style='color: white; margin: 0; text-align: center;'>
                🎛️ Dashboard Controls
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("---")
        
        # Client and Plant Selection
        selected_client, selected_plant, plant_type = create_client_plant_filters(client_data)
        
        st.sidebar.markdown("---")
        
        # Date Selection
        start_date, end_date = create_date_filters()

      
        
        # Main content area
        if selected_client:
            
            # Create tabs
            tab1, tab2, tab3 = st.tabs(["Summary", "ToD Analysis", "Power Cost Analysis"])
            
            with tab1:
                # Determine what to pass to display functions
                display_name = selected_plant if selected_plant else selected_client
                
                # Show database connection status
                if CONN is None:
                    st.error("❌ Database connection failed. Please check your database configuration.")
                    st.stop()
                
                # Automatically display all plots
                st.subheader("Generation vs Consumption")
                with st.spinner("Loading generation vs consumption data..."):
                    display_generation_vs_consumption(display_name, start_date, end_date)
                
                st.markdown("---")
                
                st.subheader("Generation Analysis")
                with st.spinner("Loading generation data..."):
                    display_generation_only(display_name, start_date, end_date)
                
                st.markdown("---")
                
                st.subheader("Consumption Analysis")
                with st.spinner("Loading consumption data..."):
                    display_consumption_only(display_name, start_date, end_date)
            
            with tab2:
                
                
                # Show database connection status
                if CONN is None:
                    st.error("❌ Database connection failed. Please check your database configuration.")
                    st.stop()
                
                # Automatically display all ToD plots
                st.subheader("Monthly ToD Before Banking")
                with st.spinner("Loading monthly ToD data..."):
                    display_monthly_tod_before_banking(display_name)
                
                st.markdown("---")
                
                st.subheader("Monthly Banking Settlement")
                with st.spinner("Loading banking settlement data..."):
                    display_monthly_banking_settlement(display_name)
                
                st.markdown("---")
                
                st.subheader("ToD Generation vs Consumption")
                with st.spinner("Loading ToD comparison data..."):
                    display_tod_generation_vs_consumptiont(display_name, start_date, end_date)
                
                st.markdown("---")
                
                st.subheader("ToD Generation Analysis")
                with st.spinner("Loading ToD generation data..."):
                    display_tod_generation(display_name, start_date, end_date)
                
                st.markdown("---")
                
                st.subheader("ToD Consumption Analysis")
                with st.spinner("Loading ToD consumption data..."):
                    display_tod_consumption(display_name, start_date, end_date)
            
            with tab3:
                st.header("💰 Power Cost Analysis")
                display_power_cost_analysis(display_name)
                
                
        
        else:
            # No content when no selection is made
            pass
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        logging.error(f"Application error: {str(e)}")
        
        # Show error details in expander for debugging
        with st.expander("🔍 Error Details"):
            st.code(str(e))

if __name__ == "__main__":
    main()