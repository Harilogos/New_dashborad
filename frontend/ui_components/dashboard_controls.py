"""
Dashboard Controls Module
Provides UI components for client selection, date filtering, and page setup
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

def setup_page():
    """Configure Streamlit page settings"""
    st.set_page_config(
        page_title="Energy Generation Dashboard",
        page_icon="🌞",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/your-repo/energy-dashboard',
            'Report a bug': 'https://github.com/your-repo/energy-dashboard/issues',
            'About': """
            # Solar & Wind Energy Generation Dashboard
            
            **Version:** 1.0  
            **Framework:** Streamlit  
            **Purpose:** Monitor and analyze solar and wind energy generation, consumption patterns, and settlement data.
            
            Built with ❤️ for sustainable energy monitoring.
            """
        }
    )

def apply_custom_css():
    """Apply custom CSS styling to the dashboard"""
    st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #1E88E5;
        --secondary-color: #424242;
        --background-color: #f0f2f6;
        --success-color: #4CAF50;
        --warning-color: #FFA000;
        --info-color: #e8f0fe;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--background-color);
    }
    
    /* Custom info boxes */
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--primary-color);
        background-color: var(--info-color);
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--success-color);
        background-color: #e8f5e8;
    }
    
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 4px solid var(--warning-color);
        background-color: #fff8e1;
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        border-radius: 0.5rem;
        border: none;
        background: linear-gradient(90deg, var(--primary-color), #42A5F5);
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.3);
    }
    
    /* Section headers */
    .section-header {
        font-weight: bold;
        color: var(--secondary-color);
        font-size: 1.1rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Loading spinner customization */
    .stSpinner > div {
        border-top-color: var(--primary-color) !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

def create_client_plant_filters(client_data: Dict) -> Tuple[Optional[str], Optional[str], str]:
    """
    Create client selection filter and determine plant configuration
    
    Args:
        client_data: Dictionary containing client and plant information
        
    Returns:
        Tuple of (selected_client, selected_plant, plant_type)
    """
    
    # Initialize session state
    if 'selected_client' not in st.session_state:
        st.session_state.selected_client = None
    
    # Client Selection Section
    st.sidebar.markdown('<p class="section-header">🏢 Client Selection</p>', unsafe_allow_html=True)
    
    if not client_data:
        st.sidebar.error("❌ No client data available")
        return None, None, "None"
    
    client_options = ["Select a Client"] + sorted(list(client_data.keys()))
    
    selected_client = st.sidebar.selectbox(
        "Choose a client to view their energy data",
        options=client_options,
        key="client_selector",
        help="Select a client to load their plant data"
    )
    
    if selected_client == "Select a Client":
        return None, None, "None"
    
    # Update session state
    st.session_state.selected_client = selected_client
    
    # Get plant data for selected client
    plants = client_data.get(selected_client, {})
    solar_plants = plants.get('solar', [])
    wind_plants = plants.get('wind', [])
    
    # Check if client has plants
    total_plants = len(solar_plants) + len(wind_plants)
    has_both_types = len(solar_plants) > 0 and len(wind_plants) > 0
    
    if total_plants == 0:
        st.sidebar.error("❌ No plants available for this client")
        return selected_client, None, "None"
    
    # Auto-select if only one plant
    if total_plants == 1:
        if solar_plants:
            selected_plant = solar_plants[0]
            plant_type = "Solar"
        else:
            selected_plant = wind_plants[0]
            plant_type = "Wind"
        
        st.sidebar.success(f"✅ Auto-selected: {selected_plant}")
        return selected_client, selected_plant, plant_type
    
    # If client has only one type of plant (but multiple plants of that type), don't show selection
    if not has_both_types:
        if solar_plants:
            # Multiple solar plants only - auto-select combined view
            selected_plant = None
            plant_type = "Solar"
            st.sidebar.info(f"📊 Viewing all {len(solar_plants)} solar plants combined")
        else:
            # Multiple wind plants only - auto-select combined view
            selected_plant = None
            plant_type = "Wind" 
            st.sidebar.info(f"📊 Viewing all {len(wind_plants)} wind plants combined")
        
        return selected_client, selected_plant, plant_type
    
    # For clients with both types, default to combined view
    selected_plant = None
    plant_type = "Combined"
    
    return selected_client, selected_plant, plant_type

def create_date_filters():
    """Create and return date range filters"""
    
    # Add a date selection header with better styling
    st.sidebar.markdown('<div style="font-weight: bold; margin-bottom: 10px; color: #424242;">Date Selection</div>', unsafe_allow_html=True)

    # Set default dates to today
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Calculate min and max values (1 year before and after today)
    min_date = today - timedelta(days=365)
    max_date = today + timedelta(days=365)

    # Initialize session state for date range if it doesn't exist
    if 'date_range' not in st.session_state:
        st.session_state.date_range = (today, today)

    # Use a single date_input with 'start' and 'end' values
    date_range = st.sidebar.date_input(
        "Select Custom Date Range",
        value=st.session_state.date_range,
        min_value=min_date,
        max_value=max_date,
        help="Select a custom date range for your data"
    )

    # Extract start and end dates from the tuple
    if len(date_range) == 2:
        start_date, end_date = date_range
    else:
        # Fallback if only one date is selected
        start_date = end_date = date_range[0]

    return start_date, end_date

def create_plant_type_indicator(plant_type: str) -> str:
    """Create a visual indicator for plant type"""
    
    indicators = {
        "Solar": "☀️",
        "Wind": "💨",
        "Combined": "🔄",
        "None": "❌"
    }
    
    return indicators.get(plant_type, "❓")

def show_loading_message(message: str):
    """Show a loading message with spinner"""
    return st.spinner(f"⏳ {message}")

def show_error_message(message: str, details: str = None):
    """Show an error message with optional details"""
    st.error(f"❌ {message}")
    
    if details:
        with st.expander("🔍 Error Details"):
            st.code(details)

def show_success_message(message: str):
    """Show a success message"""
    st.success(f"✅ {message}")

def show_info_message(message: str):
    """Show an info message"""
    st.info(f"ℹ️ {message}")

def show_warning_message(message: str):
    """Show a warning message"""
    st.warning(f"⚠️ {message}")