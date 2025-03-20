# Caprae LeadGen Tool

A comprehensive lead generation tool that helps businesses scrape and enrich contact information for prospective clients. This tool is designed to streamline the process of finding, validating, and enriching business leads.

![LeadGen Tool Interface](https://via.placeholder.com/800x450?text=LeadGen+Tool+Interface)

## Features

- **Web Search**: Find relevant companies based on specific search criteria
- **Website Scraping**: Extract contact information (emails, phones, social links) from company websites
- **Email Validation**: Verify the deliverability of email addresses
- **Data Enrichment**: Enhance lead data with additional company insights
- **Batch Processing**: Process multiple leads at once via CSV/Excel uploads
- **Modern UI**: Clean, intuitive interface that makes lead generation simple

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Google API Key and Custom Search Engine ID (for search functionality)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/mathamphetamine/caprae_leadgen_tool.git
cd caprae_leadgen_tool
```

2. Create a virtual environment:
```bash
# On macOS/Linux
python -m venv venv
source venv/bin/activate

# On Windows
python -m venv venv
venv\Scripts\activate
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy the `.env.example` file to `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file with your API keys:
   ```
   GOOGLE_API_KEY=your_google_api_key
   GOOGLE_CSE_ID=your_custom_search_engine_id
   ```

   To obtain these keys:
   - Visit [Google Programmable Search Engine](https://programmablesearchengine.google.com/)
   - Create a new search engine
   - Get your API key from [Google Cloud Console](https://console.cloud.google.com/)

## Usage

1. Start the web application:
```bash
python main.py
```

2. Open your browser and navigate to `http://localhost:5000`

3. Use the interface to:
   - **Search**: Find companies based on keywords
   - **Scrape**: Extract contact information from specific websites
   - **Validate**: Verify email addresses for deliverability
   - **Enrich**: Add additional context to your leads
   - **Batch Process**: Upload CSV/Excel files for bulk processing

## Screenshots

### Search Interface
![Search Tab](https://via.placeholder.com/600x300?text=Search+Tab)

### Scraping Results
![Scrape Results](https://via.placeholder.com/600x300?text=Scrape+Results)

### Email Validation
![Email Validation](https://via.placeholder.com/600x300?text=Email+Validation)

## API Documentation

The tool provides a RESTful API for integration with other applications:

### Search Companies

**Endpoint**: `/api/search`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "query": "software development companies in berlin",
  "num_results": 10,
  "filter_domains": [".com", ".de"]
}
```

**Response**:
```json
[
  {
    "title": "Example Company",
    "link": "https://example.com",
    "snippet": "Example company description...",
    "domain": "example.com"
  },
  ...
]
```

### Scrape Website

**Endpoint**: `/api/scrape`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "url": "https://example.com",
  "max_pages": 5,
  "follow_links": true
}
```

**Response**:
```json
{
  "emails": ["contact@example.com", "info@example.com"],
  "phones": ["+1 (123) 456-7890"],
  "social_links": ["https://linkedin.com/company/example"],
  "contact_page_url": "https://example.com/contact",
  "company_name": "Example Inc.",
  "domain": "example.com",
  "website_url": "https://example.com"
}
```

### Validate Emails

**Endpoint**: `/api/validate-emails`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "emails": ["contact@example.com", "invalid@nonexistent123.com"]
}
```

**Response**:
```json
[
  {
    "email": "contact@example.com",
    "valid": true,
    "reason": "Valid",
    "normalized_email": "contact@example.com"
  },
  {
    "email": "invalid@nonexistent123.com",
    "valid": false,
    "reason": "Domain does not exist"
  }
]
```

### Enrich Company Data

**Endpoint**: `/api/enrich`  
**Method**: POST  
**Content-Type**: application/json  

**Request Body**:
```json
{
  "website_url": "https://example.com",
  "domain": "example.com"
}
```

**Response**:
```json
{
  "emails": ["contact@example.com", "info@example.com"],
  "phones": ["+1 (123) 456-7890"],
  "social_links": ["https://linkedin.com/company/example"],
  "company_name": "Example Inc.",
  "domain": "example.com",
  "potential_emails": ["sales@example.com", "support@example.com"]
}
```

## For Developers

### Importing the Module

```python
# Import individual functions
from leadgen_tool import scrape_website, validate_email_list, enrich_company_data

# Or use the classes directly
from leadgen_tool.scraper import WebScraper
from leadgen_tool.enricher import EmailValidator, DataEnricher
```

### Examples

```python
# Search for companies
from leadgen_tool import search_companies

companies = search_companies("software development companies in berlin")
for company in companies:
    print(f"Company: {company['title']}, URL: {company['link']}")

# Scrape a specific website
from leadgen_tool import scrape_website

contact_data = scrape_website("https://example.com")
print(f"Emails: {contact_data['emails']}")
print(f"Phones: {contact_data['phones']}")

# Validate an email
from leadgen_tool import validate_email_single

result = validate_email_single("contact@example.com")
if result['valid']:
    print(f"Email is valid: {result['normalized_email']}")
else:
    print(f"Email is invalid: {result['reason']}")

# Enrich company data
from leadgen_tool import enrich_company_data

company_data = {
    'website_url': 'https://example.com'
}
enriched_data = enrich_company_data(company_data)
```

## Configuration

You can configure the tool by modifying variables in the `.env` file:

```
# API settings
GOOGLE_API_KEY=your_key
GOOGLE_CSE_ID=your_id

# Scraping settings
MAX_REQUESTS_PER_MINUTE=10
REQUEST_TIMEOUT=15
```

## Limitations

- The LinkedIn scraper is provided for educational purposes only and should be used with caution, as automated scraping may violate LinkedIn's Terms of Service.
- Google search functionality requires valid API keys and is limited by Google's API quotas.
- Email validation performs basic checks but cannot guarantee 100% accuracy for all mail servers.

## License

MIT

## Disclaimer

This tool is for educational purposes only. Always ensure you comply with websites' terms of service and robots.txt files when scraping. Be respectful of rate limits and privacy concerns. Always follow relevant data protection regulations when collecting and storing contact information.
