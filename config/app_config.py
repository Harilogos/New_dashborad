"""
Application Configuration
Contains settings and constants for the dashboard
"""

# Application Settings
APP_TITLE = "Solar & Wind Energy Generation Dashboard"
APP_ICON = "🌞"
APP_VERSION = "1.0"

# Page Configuration
PAGE_CONFIG = {
    "page_title": APP_TITLE,
    "page_icon": APP_ICON,
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# Theme Colors
COLORS = {
    "primary": "#1E88E5",
    "secondary": "#424242", 
    "background": "#f0f2f6",
    "success": "#4CAF50",
    "warning": "#FFA000",
    "info": "#e8f0fe",
    "error": "#f44336"
}

# Plant Type Colors
PLANT_COLORS = {
    "solar": "#FFA000",
    "wind": "#1E88E5", 
    "combined": "#4CAF50"
}

# Plant Type Icons
PLANT_ICONS = {
    "solar": "☀️",
    "wind": "💨",
    "combined": "🔄",
    "none": "❌"
}

# Tab Configuration
TABS = {
    "summary": {
        "title": "📊 Summary",
        "icon": "📊"
    },
    "tod": {
        "title": "⏰ ToD Analysis", 
        "icon": "⏰"
    },
    "cost": {
        "title": "💰 Power Cost Analysis",
        "icon": "💰"
    }
}

# Date Configuration
DATE_CONFIG = {
    "max_days_back": 365,
    "max_days_forward": 365,
    "default_range_days": 1
}

# Database Configuration
DB_CONFIG = {
    "connection_timeout": 30,
    "query_timeout": 60,
    "max_retries": 3
}

# UI Messages
MESSAGES = {
    "loading": {
        "client_data": "Loading client data...",
        "generation_consumption": "Loading generation vs consumption data...",
        "generation_only": "Loading generation data...",
        "consumption_only": "Loading consumption data...",
        "tod_banking": "Loading monthly ToD data...",
        "banking_settlement": "Loading banking settlement data...",
        "tod_comparison": "Loading ToD comparison data...",
        "tod_generation": "Loading ToD generation data...",
        "tod_consumption": "Loading ToD consumption data..."
    },
    "errors": {
        "no_client_data": "No client data available",
        "no_plants": "No plants available for this client",
        "db_connection": "Database connection failed",
        "data_fetch": "Failed to fetch data",
        "invalid_selection": "Invalid client or plant selection"
    },
    "info": {
        "select_client": "Please select a client and plant from the sidebar to begin analysis.",
        "combined_view": "Combined view shows data for all plants",
        "single_day": "Single day analysis",
        "multi_day": "Multi-day analysis",
        "auto_selected": "Auto-selected",
        "cost_analysis_unavailable": "Power Cost Analysis is not available for combined view. Please select a specific plant.",
        "cost_analysis_coming_soon": "Power Cost Analysis features coming soon!"
    },
    "tips": {
        "plant_selection": "Select a specific plant for detailed analysis or leave both at default for combined view. Selecting one plant will reset the other."
    }
}

# Feature Flags
FEATURES = {
    "power_cost_analysis": False,  # Set to True when implemented
    "real_time_updates": False,
    "data_export": False,
    "user_preferences": False
}

# Logging Configuration
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "dashboard.log"
}