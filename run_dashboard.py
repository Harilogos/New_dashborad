#!/usr/bin/env python3
"""
Dashboard Launcher Script
Simple script to launch the Streamlit dashboard with proper configuration
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'mysql-connector-python',
        'plotly'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        print("\n   Or install all requirements:")
        print("   pip install -r requirements.txt")
        return False
    
    return True

def check_database_config():
    """Check if database configuration exists"""
    db_setup_path = Path("db/db_setup.py")
    
    if not db_setup_path.exists():
        print("❌ Database setup file not found: db/db_setup.py")
        return False
    
    try:
        with open(db_setup_path, 'r') as f:
            content = f.read()
            if 'localhost' in content and 'test123' in content:
                print("⚠️  Using default database configuration.")
                print("   Update db/db_setup.py with your database credentials.")
    except Exception as e:
        print(f"❌ Error reading database config: {e}")
        return False
    
    return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching Energy Generation Dashboard...")
    print("📊 Dashboard will open in your default web browser")
    print("🌐 URL: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main launcher function"""
    print("🌞 Solar & Wind Energy Generation Dashboard")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("❌ app.py not found. Please run this script from the project root directory.")
        return
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return
    
    # Check database configuration
    print("🔍 Checking database configuration...")
    if not check_database_config():
        return
    
    print("✅ All checks passed!")
    print()
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()