# Lead Generation Tool - Documentation

## Table of Contents
1. [Overview](#overview)
2. [User Guide](#user-guide)
   - [Installation](#installation)
   - [Interface Overview](#interface-overview)
   - [Using the Tool](#using-the-tool)
   - [Advanced Features](#advanced-features)
   - [Best Practices](#best-practices)
3. [Technical Implementation](#technical-implementation)
   - [Architecture Overview](#architecture-overview)
   - [Core Classes](#core-classes)
   - [Data Extraction Techniques](#data-extraction-techniques)
   - [Key Technical Features](#key-technical-features)
   - [Testing](#testing)
   - [Extending the Tool](#extending-the-tool)
4. [Design Approach & Rationale](#design-approach--rationale)
   - [Libraries & Tools Selection](#libraries--tools-selection)
   - [Technical Improvements](#technical-improvements)
   - [Performance Evaluation](#performance-evaluation)
   - [Business Value Alignment](#business-value-alignment)

## Overview

The Lead Generation Tool is an AI-enhanced web scraping solution designed to help businesses quickly identify and collect potential customer information from company websites. It features intelligent data extraction, filtering, and analysis capabilities within an intuitive user interface.

### Key Features

- **Targeted Website Scraping**: Extract potential lead data from specified websites with multi-page crawling
- **Intelligent Filtering**: Filter and prioritize leads based on keywords and advanced field-specific filters
- **Data Validation & Cleaning**: Ensure data quality with validation, deduplication, and text normalization
- **Lead Analysis**: View statistics and insights about your leads, including industry and domain breakdowns
- **User-friendly Interface**: Intuitive Streamlit web interface with configuration management
- **Ethical Scraping**: Built-in respect for robots.txt rules and rate limiting

## User Guide

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

### Interface Overview

The interface consists of two main sections:
- **Sidebar**: Contains all configuration options and settings
- **Main Panel**: Displays results, analysis, and lead data

#### Sidebar Controls

- **Configuration Management**: Save/load search configurations
- **Target URL**: Enter the website to scrape
- **Crawling Options**: Set depth, robots.txt settings, and maximum pages
- **Filtering Options**: Keywords to include/exclude, minimum data points, and advanced field-specific filters

### Using the Tool

#### Step 1: Configure Your Search
1. Enter the target website URL
2. Set your crawling preferences
3. Configure your filtering criteria
4. (Optional) Save your configuration for future use

#### Step 2: Generate Leads
1. Click the "Generate Leads" button
2. The tool will display a progress bar while scraping
3. If errors occur, they will be displayed with details

#### Step 3: Analyze Results
The results section provides:
- **Lead Count**: Total number of leads found
- **Industry Breakdown**: Chart showing distribution by industry
- **Domain Analysis**: List of most common domains
- **Data Completeness**: Metrics on contact information quality

#### Step 4: Work with Lead Data
- **Search**: Use the search box to filter leads by any criteria
- **Sort**: Click column headers to sort leads
- **Filter**: Use the dropdown filters to narrow results
- **Export**: Download all leads as a CSV file

### Advanced Features

#### Multi-page Crawling
The tool can follow internal links to discover additional leads:
- Set "Crawl Depth" to control how many links deep to go
- Use "Maximum Pages" to limit the total pages processed
- Links are prioritized based on relevance to lead generation

#### Configuration Management
Save time by managing your search configurations:
1. Create and save multiple configurations for different types of searches
2. Load saved configurations with a single click
3. Configurations are stored in the `config` directory

#### Advanced Filtering
Create complex filters to target specific lead types:
1. Click "Add Filter" to create a new filter rule
2. Select the field to filter on (e.g., Company Name, Email)
3. Choose the condition (contains/does not contain)
4. Enter the filter value
5. Add multiple filters to create AND conditions

#### Lead Analysis
Get insights about your leads:
- **Industry Distribution**: See which industries appear most frequently
- **Contact Completeness**: Evaluate the quality of contact information
- **Domain Analysis**: Identify the most common email domains
- **Job Titles**: View statistics on job titles when available

### Best Practices

#### Ethical Scraping
- Always respect website terms of service
- Use reasonable rate limits (the tool has built-in delays)
- Don't attempt to circumvent access restrictions
- Only use the data in accordance with privacy regulations

#### Optimizing Results
- Start with broader filters and then narrow them
- For company websites, target the "About" and "Contact" pages first
- Use industry-specific keywords to improve filtering
- Test with different crawl depths to find the optimal setting

#### Troubleshooting
- If no results are found, try reducing filter restrictions
- If the tool runs slowly, reduce the crawl depth and maximum pages
- For rate limiting errors, wait a few minutes before trying again
- Check that the URL is correctly formatted (including http:// or https://)

## Technical Implementation

### Architecture Overview

The tool follows a modular architecture with two main components:

1. **Scraper Module** (`src/scraper.py`): Handles website crawling, data extraction, and lead filtering
2. **UI Module** (`src/app.py`): Provides the Streamlit-based user interface and session management

Data flow:
```
User Input → Streamlit UI → Scraper Module → Data Processing → Lead Display → CSV Export
```

### Core Classes

#### LeadScraper

The `LeadScraper` class in `scraper.py` is responsible for extracting lead information from websites.

**Key Methods:**
- **scrape_website**: Main entry point that orchestrates the scraping process
- **_check_robots_txt**: Verifies if scraping is allowed for the target URL
- **_find_internal_links**: Discovers and prioritizes internal links for crawling
- **_extract_company_info**: Extracts company details from HTML content
- **filter_leads**: Applies user-defined filters to the extracted leads
- **export_to_csv**: Saves the lead data to a CSV file
- **analyze_leads**: Generates insights and statistics about the collected leads

**Error Handling:**
- Exponential backoff for request failures
- Graceful recovery from parsing errors
- Detailed error messages for debugging
- Rate limiting to respect server resources

#### Streamlit UI

The UI in `app.py` manages:
- User input collection and validation
- Session state management
- Configuration saving/loading
- Results visualization
- Progress tracking

### Data Extraction Techniques

#### Company Information Extraction

The tool uses several techniques to extract company information:

1. **Meta Tag Analysis**: Extracts information from meta tags (description, keywords)
2. **Schema.org Markup**: Identifies structured data using JSON-LD or microdata
3. **HTML Pattern Matching**: Looks for common patterns in HTML structure
4. **Text Analysis**: Analyzes heading and paragraph text for relevant information

#### Contact Information Extraction

Contact details are extracted using:

1. **Regular Expressions**: Pattern matching for emails, phone numbers
2. **HTML Structure Analysis**: Finding contact forms and contact pages
3. **Link Analysis**: Identifying social media links and contact links

### Key Technical Features

#### State Management

The application uses Streamlit's session state to manage data:

```python
# Example of session state initialization
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'filtered_leads' not in st.session_state:
    st.session_state.filtered_leads = []
if 'lead_analysis' not in st.session_state:
    st.session_state.lead_analysis = {}
```

#### Rate Limiting Implementation

The scraper uses exponential backoff for rate limiting:

```python
def _make_request(self, url, max_retries=3, base_delay=1):
    """Make HTTP request with exponential backoff."""
    for attempt in range(max_retries):
        try:
            response = requests.get(
                url, 
                headers={'User-Agent': self.user_agent},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            delay = base_delay * (2 ** attempt)
            time.sleep(delay)
    
    # If we get here, all retries failed
    raise Exception(f"Failed to retrieve {url} after {max_retries} attempts")
```

#### Robots.txt Processing

The tool respects robots.txt rules:

```python
def _check_robots_txt(self, url):
    """Check if scraping is allowed by robots.txt."""
    parsed_url = urlparse(url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
    
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    
    try:
        rp.read()
        return rp.can_fetch(self.user_agent, url)
    except:
        # If robots.txt doesn't exist or can't be parsed, we assume scraping is allowed
        return True
```

### Testing

Unit tests are provided in `src/tests/test_scraper.py` and cover:
- Robot.txt checking
- Data extraction
- Filtering logic
- CSV export functionality
- Error handling

Run the tests with:
```
python -m unittest src/tests/test_scraper.py
```

### Extending the Tool

#### Adding New Field Extractors
1. Add a new method to the `LeadScraper` class
2. Integrate it with the `_extract_company_info` method
3. Update the UI in `app.py` to display and filter the new field

#### Implementing New Filters
1. Extend the `filter_leads` method in `LeadScraper`
2. Add corresponding UI elements in `app.py`
3. Update the filter handling in the session state

#### Adding CRM Integration
1. Create a new module (e.g., `src/crm_integration.py`)
2. Implement the appropriate API calls for your CRM
3. Add a new section to the UI for CRM connection settings
4. Update the export functionality to push data to the CRM

## Design Approach & Rationale

For this project, I adopted a "Quality First" approach, focusing on developing a small set of core features with exceptional implementation rather than attempting to build many features superficially. I prioritized creating a tool that:

1. **Solves a real business problem**: Identifying potential leads from company websites quickly and efficiently
2. **Presents a clean, intuitive interface**: Making the tool accessible to non-technical users
3. **Delivers high-quality, actionable data**: Implementing filtering and validation to ensure leads are relevant
4. **Operates ethically**: Respecting website terms of service and robots.txt rules
5. **Handles errors gracefully**: Implementing robust error recovery and user feedback

### Libraries & Tools Selection

I selected Python with the following libraries for implementation:

- **BeautifulSoup4**: For HTML parsing and data extraction
- **Streamlit**: For creating a responsive, intuitive web interface without extensive frontend development
- **Pandas**: For data manipulation and CSV export
- **Requests**: For fetching web content with proper headers and error handling
- **Fake-UserAgent**: To rotate user agents and respect website policies
- **RobotFileParser**: To check and respect robots.txt rules

These choices allowed for rapid development while ensuring the tool has the necessary capabilities for effective lead generation.

### Technical Improvements

Key technical improvements include:

1. **Stateless Architecture**: Redesigned the scraper to be more stateless, improving reliability and maintainability
2. **Rate Limiting**: Implemented proper rate limiting and exponential backoff for retries
3. **Error Recovery**: Added comprehensive error handling with detailed feedback
4. **Progress Tracking**: Added visual feedback during the scraping process
5. **Filesystem Safety**: Added proper permission checking and error handling for file operations
6. **Expanded Test Coverage**: Created additional unit tests covering the new functionality

### Performance Evaluation

The tool demonstrates strengths in:

- **Intelligent Pattern Recognition**: Able to extract data from various website structures without site-specific configuration
- **Data Quality Control**: Multiple validation and filtering mechanisms ensure high-quality leads
- **User Experience**: Intuitive interface with immediate feedback and analysis
- **Export Capabilities**: Seamless CSV export for integration with existing workflows
- **Ethical Compliance**: Built-in respect for website policies and terms of service

Limitations include:

- **Advanced Page Structure**: Some highly dynamic websites using JavaScript rendering may require additional techniques
- **Basic Email Validation**: Uses pattern matching rather than deliverability checks
- **Limited CRM Integration**: Exports to CSV but does not directly integrate with CRM systems

### Business Value Alignment

This lead generation tool addresses real business needs for Caprae Capital's portfolio companies by:

1. **Accelerating Sales Workflows**: Dramatically reducing the time needed to identify and collect potential leads
2. **Improving Lead Quality**: Filtering and validation ensure sales teams focus on high-value prospects
3. **Enabling Data-Driven Decisions**: Analytics provide insights into lead sources and industry distribution
4. **Respecting Ethical Guidelines**: Built-in compliance with web scraping best practices
5. **Scalable Approach**: The tool's design allows for future enhancements like AI-driven lead scoring 