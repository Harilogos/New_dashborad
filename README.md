# Solar & Wind Energy Generation Dashboard

A comprehensive Streamlit-based dashboard for monitoring and analyzing solar and wind energy generation, consumption patterns, and settlement data.

## Features

### 🎛️ Dashboard Controls
- **Client Selection**: Dynamic client dropdown with database integration
- **Plant Selection**: Smart solar/wind plant selection with mutual exclusion logic
- **Date Filtering**: Flexible date range selection with single-day and multi-day analysis
- **Current Selection Display**: Visual confirmation of active selections with reset functionality

### 📊 Analysis Tabs
- **Summary Tab**: Generation vs consumption analysis, plant-specific views
- **ToD (Time of Day) Tab**: Time-based analysis and banking settlement data
- **Power Cost Analysis Tab**: Financial analysis (coming soon)

### 🎨 User Interface
- Modern, responsive design with custom CSS styling
- Color-coded plant type indicators (Solar: Amber, Wind: Blue, Combined: Green)
- Loading states and error handling
- Interactive buttons and controls

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL database with energy data
- Required Python packages (see requirements.txt)

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd "d:/Harikrishnan/New Dashboard"
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure database connection**
   - Update database credentials in `db/db_setup.py`
   - Ensure your MySQL database is running and accessible

4. **Run the dashboard**
   ```bash
   streamlit run app.py
   ```

5. **Access the dashboard**
   - Open your web browser
   - Navigate to `http://localhost:8501`

## Project Structure

```
d:/Harikrishnan/New Dashboard/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
│
├── frontend/                      # Frontend components
│   ├── ui_components/            # UI components
│   │   ├── __init__.py
│   │   └── dashboard_controls.py # Dashboard controls implementation
│   └── display_plots/            # Display functions
│       ├── summary_display.py    # Summary tab displays
│       └── tod_display.py        # ToD tab displays
│
├── backend/                      # Backend data management
│   └── data/
│       ├── __init__.py
│       └── db_data_manager.py    # Database data management
│
├── config/                       # Configuration files
│   ├── __init__.py
│   └── app_config.py            # Application configuration
│
├── db/                          # Database modules
│   ├── db_setup.py              # Database connection setup
│   ├── fetch_summary_data.py    # Summary data fetching
│   └── fetch_tod_tab_data.py    # ToD data fetching
│
├── visualizations/              # Visualization modules
│   ├── summary_tab_visual.py    # Summary visualizations
│   ├── tod_tab_visual.py        # ToD visualizations
│   └── tod_config.py            # ToD configuration
│
└── helper/                      # Helper utilities
    └── utils.py                 # Utility functions
```

## Usage Guide

### 1. Client Selection
- Select a client from the dropdown in the sidebar
- The system will load available plants for the selected client

### 2. Plant Selection
- **Combined View**: Leave both plant dropdowns at default to view combined data
- **Specific Plant**: Select either a solar or wind plant for detailed analysis
- **Smart Selection**: Selecting one plant type automatically resets the other

### 3. Date Selection
- Choose a date range for analysis
- **Single Day**: Select the same date for start and end
- **Multi-Day**: Select different start and end dates
- Date range is limited to ±365 days from current date

### 4. Analysis Tabs

#### Summary Tab
- **Generation vs Consumption**: Compare generation and consumption patterns
- **Generation Only**: Focus on generation data analysis
- **Consumption Analysis**: Detailed consumption pattern analysis

#### ToD (Time of Day) Tab
- **Monthly ToD Before Banking**: Monthly time-of-day analysis before banking
- **Monthly Banking Settlement**: Banking settlement data visualization
- **ToD Generation vs Consumption**: Time-based generation vs consumption comparison
- **ToD Generation Analysis**: Detailed time-of-day generation patterns
- **ToD Consumption Analysis**: Time-of-day consumption analysis

#### Power Cost Analysis Tab
- Financial analysis features (coming soon)
- Requires specific plant selection (not available for combined view)

## Configuration

### Database Configuration
Update `db/db_setup.py` with your database credentials:
```python
CONN = setup_db_connection(
    host="your_host",
    user="your_username", 
    password="your_password",
    database="your_database"
)
```

### Application Configuration
Modify `config/app_config.py` to customize:
- Colors and themes
- Feature flags
- UI messages
- Date range limits

## Database Schema Requirements

The dashboard expects the following database structure:

### settlement_data table
```sql
CREATE TABLE settlement_data (
    id INT PRIMARY KEY AUTO_INCREMENT,
    client_name VARCHAR(255),
    date DATE,
    datetime DATETIME,
    allocated_generation DECIMAL(10,2),
    consumption DECIMAL(10,2),
    deficit DECIMAL(10,2),
    surplus_demand DECIMAL(10,2),
    surplus_generation DECIMAL(10,2),
    settled DECIMAL(10,2)
);
```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check database credentials in `db/db_setup.py`
   - Ensure MySQL server is running
   - Verify database exists and is accessible

2. **No Client Data Available**
   - Check if `settlement_data` table has data
   - Verify `client_name` column is not null
   - Check database connection

3. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python path and module imports

4. **Streamlit Not Starting**
   - Verify Streamlit is installed: `pip install streamlit`
   - Check if port 8501 is available
   - Try running with different port: `streamlit run app.py --server.port 8502`

### Debug Mode
Enable debug logging by setting the logging level in `config/app_config.py`:
```python
LOGGING_CONFIG = {
    "level": "DEBUG",
    # ... other settings
}
```

## Development

### Adding New Features

1. **New Visualization**
   - Add visualization function to appropriate module in `visualizations/`
   - Create display function in `frontend/display_plots/`
   - Add UI controls in `frontend/ui_components/dashboard_controls.py`
   - Update main app in `app.py`

2. **New Data Source**
   - Add fetch function to appropriate module in `db/`
   - Update data manager in `backend/data/db_data_manager.py`
   - Add configuration in `config/app_config.py`

3. **UI Improvements**
   - Update CSS in `frontend/ui_components/dashboard_controls.py`
   - Modify colors and themes in `config/app_config.py`
   - Add new UI components as needed

### Code Style
- Follow PEP 8 Python style guidelines
- Use type hints where appropriate
- Add docstrings to functions and classes
- Include error handling and logging

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For technical support or feature requests:
- Create an issue in the project repository
- Contact the development team
- Check the troubleshooting guide above

## Version History

- **v1.0** (2025-01-27): Initial release with core dashboard functionality
  - Client and plant selection
  - Date filtering
  - Summary and ToD analysis tabs
  - Database integration
  - Custom UI styling

## Future Enhancements

- Power Cost Analysis implementation
- Real-time data updates
- Data export functionality
- User preferences and saved views
- Advanced filtering options
- Mobile responsive design improvements