# Lead Generation Tool

An AI-enhanced web scraping tool designed for lead generation, helping businesses identify and collect potential customer information from company websites efficiently.

![Lead Gen Tool](https://via.placeholder.com/800x400?text=Lead+Generation+Tool)

## Quick Start

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the application:
   ```
   streamlit run src/app.py
   ```

## Key Features

- **Targeted Website Scraping**: Extract lead data from websites with multi-page crawling
- **Intelligent Filtering**: Find relevant leads with customizable criteria
- **Data Validation**: Ensure quality with automated cleaning and validation
- **Lead Analysis**: Get insights into your leads with visual analytics
- **Ethical Scraping**: Built-in respect for robots.txt and rate limiting

## Documentation

For comprehensive documentation, please refer to:

- [Complete Documentation](DOCUMENTATION.md) - Detailed user guide and technical information
- [Video Script](VIDEO_SCRIPT.md) - Script for creating a demonstration video

## Project Structure

```
├── config/              # Configuration storage
├── data/                # Lead data exports
├── src/                 # Source code
│   ├── app.py           # Streamlit UI
│   ├── scraper.py       # Lead scraping engine
│   └── tests/           # Unit tests
├── DOCUMENTATION.md     # Complete user and developer guide
├── README.md            # This file
├── requirements.txt     # Python dependencies
└── VIDEO_SCRIPT.md      # Video demonstration script
```

## Development

### Dependencies

- Python 3.8+
- See requirements.txt for full list of packages

### Testing

Run the unit tests with:
```
python -m unittest src/tests/test_scraper.py
```

## License

MIT

## Disclaimer

This tool is for educational purposes only. Always ensure you comply with websites' terms of service and robots.txt files when scraping. Be respectful of rate limits and privacy concerns.
