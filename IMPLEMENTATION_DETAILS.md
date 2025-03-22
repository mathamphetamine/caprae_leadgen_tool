# Lead Generation Tool - Implementation Details

This document provides detailed technical information about the implementation of the Lead Generation Tool. It is intended for developers who want to understand the codebase or extend the tool's functionality.

## Architecture Overview

The tool follows a modular architecture with two main components:

1. **Scraper Module** (`src/scraper.py`): Handles website crawling, data extraction, and lead filtering
2. **UI Module** (`src/app.py`): Provides the Streamlit-based user interface and session management

Here's a high-level overview of the data flow:

```
User Input → Streamlit UI → Scraper Module → Data Processing → Lead Display → CSV Export
```

## Core Classes

### LeadScraper

The `LeadScraper` class in `scraper.py` is the central component responsible for extracting lead information from websites.

#### Key Methods:

- **scrape_website**: Main entry point that orchestrates the scraping process
- **_check_robots_txt**: Verifies if scraping is allowed for the target URL
- **_find_internal_links**: Discovers and prioritizes internal links for crawling
- **_extract_company_info**: Extracts company details from HTML content
- **filter_leads**: Applies user-defined filters to the extracted leads
- **export_to_csv**: Saves the lead data to a CSV file
- **analyze_leads**: Generates insights and statistics about the collected leads

#### Error Handling:

The scraper implements comprehensive error handling with:
- Exponential backoff for request failures
- Graceful recovery from parsing errors
- Detailed error messages for debugging
- Rate limiting to respect server resources

### Streamlit UI

The UI is built with Streamlit in `app.py` and manages:
- User input collection and validation
- Session state management
- Configuration saving/loading
- Results visualization
- Progress tracking

## Data Extraction Techniques

### Company Information Extraction

The tool uses several techniques to extract company information:

1. **Meta Tag Analysis**: Extracts information from meta tags (description, keywords)
2. **Schema.org Markup**: Identifies structured data using JSON-LD or microdata
3. **HTML Pattern Matching**: Looks for common patterns in HTML structure
4. **Text Analysis**: Analyzes heading and paragraph text for relevant information

### Contact Information Extraction

Contact details are extracted using:

1. **Regular Expressions**: Pattern matching for emails, phone numbers
2. **HTML Structure Analysis**: Finding contact forms and contact pages
3. **Link Analysis**: Identifying social media links and contact links

## Technical Implementation Details

### State Management

The application uses Streamlit's session state to manage:
- Current lead data
- Filtered results
- Analysis metrics
- Scraper configuration
- UI state

```python
# Example of session state initialization
if 'leads' not in st.session_state:
    st.session_state.leads = []
if 'filtered_leads' not in st.session_state:
    st.session_state.filtered_leads = []
if 'lead_analysis' not in st.session_state:
    st.session_state.lead_analysis = {}
```

### Configuration Management

Configurations are saved as JSON files in the `config` directory:

```python
def save_configuration(config_name, config_data):
    """Save configuration to a JSON file."""
    os.makedirs('config', exist_ok=True)
    config_path = os.path.join('config', f"{config_name}.json")
    with open(config_path, 'w') as f:
        json.dump(config_data, f, indent=2)
    return config_path
```

### Rate Limiting Implementation

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

### Robots.txt Processing

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

## Testing

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

## Performance Considerations

- **Memory Usage**: The tool stores all leads in memory, which could be a limitation for very large websites
- **Request Rate**: Default rate limiting is set to avoid overloading target servers
- **CPU Usage**: HTML parsing is CPU-intensive but generally efficient

## Extending the Tool

### Adding New Field Extractors

To add extraction for a new field type:
1. Add a new method to the `LeadScraper` class
2. Integrate it with the `_extract_company_info` method
3. Update the UI in `app.py` to display and filter the new field

### Implementing New Filters

To add a new filtering mechanism:
1. Extend the `filter_leads` method in `LeadScraper`
2. Add corresponding UI elements in `app.py`
3. Update the filter handling in the session state

### Adding CRM Integration

To integrate with CRM systems:
1. Create a new module (e.g., `src/crm_integration.py`)
2. Implement the appropriate API calls for your CRM
3. Add a new section to the UI for CRM connection settings
4. Update the export functionality to push data to the CRM

## Code Style and Conventions

The codebase follows these conventions:
- PEP 8 for Python code style
- Private methods prefixed with underscore (e.g., `_extract_company_info`)
- Comprehensive docstrings for all classes and methods
- Error handling for all external interactions

## Known Limitations and Future Work

- **JavaScript Rendering**: The current implementation doesn't handle JavaScript-rendered content
- **Authentication**: No support for scraping sites requiring authentication
- **Distributed Scraping**: Single-threaded operation could be extended to distributed architecture
- **Natural Language Processing**: Future versions could use NLP for better data extraction

## Security Considerations

- **Data Storage**: Lead data is stored temporarily in memory and optionally exported to CSV
- **API Keys**: No external API keys are currently required
- **User Input**: All user input is validated before use in scraping operations 