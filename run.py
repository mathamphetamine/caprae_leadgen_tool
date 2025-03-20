#!/usr/bin/env python
"""
Caprae LeadGen Tool - Run Script
--------------------------------
This script starts the Caprae LeadGen Tool web application.
"""

from main import app

def main():
    """Entry point for the application."""
    app.run(debug=False, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 