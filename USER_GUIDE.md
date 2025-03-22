# Lead Generation Tool - User Guide

## Overview

The Lead Generation Tool is an AI-enhanced web scraping solution designed to help businesses quickly identify and collect potential customer information from company websites. This guide provides detailed instructions on how to use all features of the tool effectively.

## Getting Started

### Installation

1. Ensure you have Python 3.8 or later installed
2. Clone the repository:
   ```
   git clone https://github.com/mathamphetamine/caprae_leadgen_tool.git
   ```
3. Navigate to the project directory:
   ```
   cd caprae_leadgen_tool
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Launch the application:
   ```
   streamlit run src/app.py
   ```

The application will open in your default web browser at `http://localhost:8501`.

## Interface Overview

The interface consists of two main sections:
- **Sidebar**: Contains all configuration options and settings
- **Main Panel**: Displays results, analysis, and lead data

### Sidebar Controls

#### Configuration Management
- **Save Configuration**: Save your current settings for future use
- **Load Configuration**: Load previously saved settings
- **Configuration Name**: Enter a name for your configuration

#### Target URL
Enter the full URL of the website you want to scrape (include http:// or https://).

#### Crawling Options
- **Crawl Depth**: Set how many pages deep the tool should follow internal links (1-5)
- **Respect robots.txt**: Toggle whether to check and obey robots.txt rules
- **Maximum Pages**: Limit the total number of pages to scrape

#### Filtering Options
- **Keywords to Include**: Enter words that should appear in lead data (comma-separated)
- **Keywords to Exclude**: Enter words that should not appear in lead data (comma-separated)
- **Minimum Data Points**: Set the minimum number of data points required for a valid lead
- **Advanced Filtering**: Configure field-specific filters:
  - **Field**: Select which field to filter (Company Name, Email, Phone, etc.)
  - **Condition**: Choose "contains" or "does not contain"
  - **Value**: Enter the text to match

## Using the Tool

### Step 1: Configure Your Search
1. Enter the target website URL
2. Set your crawling preferences
3. Configure your filtering criteria
4. (Optional) Save your configuration for future use

### Step 2: Generate Leads
1. Click the "Generate Leads" button
2. The tool will display a progress bar while scraping
3. If errors occur, they will be displayed with details

### Step 3: Analyze Results
The results section provides:
- **Lead Count**: Total number of leads found
- **Industry Breakdown**: Chart showing distribution by industry
- **Domain Analysis**: List of most common domains
- **Data Completeness**: Metrics on contact information quality

### Step 4: Work with Lead Data
- **Search**: Use the search box to filter leads by any criteria
- **Sort**: Click column headers to sort leads
- **Filter**: Use the dropdown filters to narrow results
- **Export**: Download all leads as a CSV file

## Advanced Features

### Multi-page Crawling
The tool can follow internal links to discover additional leads:
- Set "Crawl Depth" to control how many links deep to go
- Use "Maximum Pages" to limit the total pages processed
- Links are prioritized based on relevance to lead generation

### Configuration Management
Save time by managing your search configurations:
1. Create and save multiple configurations for different types of searches
2. Load saved configurations with a single click
3. Configurations are stored in the `config` directory

### Advanced Filtering
Create complex filters to target specific lead types:
1. Click "Add Filter" to create a new filter rule
2. Select the field to filter on (e.g., Company Name, Email)
3. Choose the condition (contains/does not contain)
4. Enter the filter value
5. Add multiple filters to create AND conditions

### Lead Analysis
Get insights about your leads:
- **Industry Distribution**: See which industries appear most frequently
- **Contact Completeness**: Evaluate the quality of contact information
- **Domain Analysis**: Identify the most common email domains
- **Job Titles**: View statistics on job titles when available

## Best Practices

### Ethical Scraping
- Always respect website terms of service
- Use reasonable rate limits (the tool has built-in delays)
- Don't attempt to circumvent access restrictions
- Only use the data in accordance with privacy regulations

### Optimizing Results
- Start with broader filters and then narrow them
- For company websites, target the "About" and "Contact" pages first
- Use industry-specific keywords to improve filtering
- Test with different crawl depths to find the optimal setting

### Troubleshooting
- If no results are found, try reducing filter restrictions
- If the tool runs slowly, reduce the crawl depth and maximum pages
- For rate limiting errors, wait a few minutes before trying again
- Check that the URL is correctly formatted (including http:// or https://)

## Technical Details

### Data Storage
- Leads are stored in memory during the session
- Exported CSV files are saved to the `data` directory
- Configurations are saved to the `config` directory as JSON files

### Privacy Considerations
- The tool does not store scraped data permanently unless exported
- No data is sent to external servers
- Consider your local privacy laws before storing contact information

## Future Enhancements

Planned improvements for future versions:
- Direct CRM integration (Salesforce, HubSpot)
- Email deliverability validation
- AI-powered lead scoring
- Company information enrichment from public databases
- Scheduled scraping and monitoring 