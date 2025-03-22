# Lead Generation Tool

A web scraping tool designed for lead generation, helping businesses identify and collect potential customer information from various online sources.

## Features

- **Targeted Website Scraping**: Extract potential lead data from specified websites with support for multi-page crawling
- **Intelligent Filtering**: Filter and prioritize leads based on keywords, criteria, and advanced field-specific filters
- **Data Validation & Cleaning**: Ensure data quality with validation, deduplication, and text normalization
- **Lead Analysis**: View statistics and insights about your leads, including industry and domain breakdowns
- **User-friendly Interface**: Intuitive Streamlit web interface with configuration management
- **Ethical Scraping**: Built-in respect for robots.txt rules and rate limiting

## Setup Instructions

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   cd lead_gen_tool
   streamlit run src/app.py
   ```

## Usage

1. Enter the target website URL
2. Configure crawling options (depth, robots.txt settings)
3. Specify filtering criteria (keywords, industry, etc.)
4. Click "Generate Leads"
5. Search, filter, and analyze your leads
6. Download the results as a CSV file

## Advanced Features

### Website Crawling
The tool can automatically follow internal links on a website to discover more potential leads. Configure the maximum number of pages to crawl in the settings.

### Configuration Management
Save your favorite search configurations and load them later to quickly run the same searches again.

### Advanced Filtering
Apply field-specific filters using contains/not contains conditions to precisely target the leads you want.

### Real-time Search
Search within your results to quickly find specific leads matching your criteria.

## Design Choices

- **Quality Over Quantity**: Focused on creating a small set of well-implemented features
- **User Experience**: Prioritized an intuitive interface for non-technical users
- **Data Quality**: Implemented validation and filtering to ensure high-quality leads
- **Ethical Scraping**: Respects website terms of service and includes rate limiting
- **Resilient Design**: Robust error handling and recovery mechanisms

## Dependencies

- Python 3.8+
- See requirements.txt for full list of packages

## Testing

Run the unit tests with:
```
python -m unittest tests/test_scraper.py
```
