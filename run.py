#!/usr/bin/env python
"""
Caprae LeadGen Tool - Run Script
--------------------------------
This script starts the Caprae LeadGen Tool web application.
"""

from main import app

if __name__ == "__main__":
    # Set debug mode to False for production
    app.run(debug=False, host='0.0.0.0', port=5000) 