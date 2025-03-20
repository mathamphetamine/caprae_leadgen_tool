import os
import json
import logging
import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory, redirect, url_for, abort
from werkzeug.utils import secure_filename
from werkzeug.exceptions import HTTPException

from scraper.web_scraper import scrape_website
from scraper.google_search import search_companies
from scraper.linkedin_scraper import search_linkedin_companies, get_linkedin_company_details
from enricher.email_validator import validate_email_list, validate_email_single
from enricher.data_enricher import enrich_company_data, batch_enrich_companies, enrich_dataframe
from utils.helpers import export_to_csv, export_to_excel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("leadgen.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Determine base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize Flask app
app = Flask(__name__, 
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Configure upload folder
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Create exports directory if it doesn't exist
EXPORT_FOLDER = os.path.join(BASE_DIR, 'exports')
os.makedirs(EXPORT_FOLDER, exist_ok=True)

# Rate limiting settings
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload size
app.config['RATE_LIMIT'] = os.environ.get('MAX_REQUESTS_PER_MINUTE', 10)

def allowed_file(filename):
    """Check if file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """API endpoint to scrape a website."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'url' not in data:
            return jsonify({'error': 'URL is required'}), 400
        
        url = data.get('url')
        max_pages = data.get('max_pages', 5)
        follow_links = data.get('follow_links', True)
        
        # Validate URL
        if not url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format. URL must start with http:// or https://'}), 400
            
        # Validate max_pages
        try:
            max_pages = int(max_pages)
            if max_pages < 1 or max_pages > 20:
                return jsonify({'error': 'max_pages must be between 1 and 20'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'max_pages must be a valid integer'}), 400
        
        # Log the request
        logger.info(f"Scraping website: {url} (max_pages={max_pages}, follow_links={follow_links})")
        
        result = scrape_website(url, max_pages, follow_links)
        
        # Log success
        logger.info(f"Successfully scraped {url}, found {len(result.get('emails', []))} emails and {len(result.get('phones', []))} phone numbers")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint to search for companies."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data.get('query')
        num_results = data.get('num_results', 10)
        filter_domains = data.get('filter_domains')
        
        # Validate num_results
        try:
            num_results = int(num_results)
            if num_results < 1 or num_results > 50:
                return jsonify({'error': 'num_results must be between 1 and 50'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'num_results must be a valid integer'}), 400
            
        # Validate filter_domains
        if filter_domains is not None and not isinstance(filter_domains, list):
            return jsonify({'error': 'filter_domains must be a list of domain extensions'}), 400
        
        # Log the request
        logger.info(f"Searching for companies: '{query}' (num_results={num_results}, filter_domains={filter_domains})")
        
        results = search_companies(query, num_results, filter_domains)
        
        # Log success
        logger.info(f"Search for '{query}' returned {len(results)} results")
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error searching companies: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-email', methods=['POST'])
def api_validate_email():
    """API endpoint to validate a single email."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        
        email = data.get('email')
        
        # Basic email format validation
        if not '@' in email or not '.' in email:
            return jsonify({'valid': False, 'reason': 'Invalid email format'}), 200
        
        # Log the request
        logger.info(f"Validating email: {email}")
        
        result = validate_email_single(email)
        
        # Log result
        valid_status = "valid" if result.get('valid', False) else "invalid"
        logger.info(f"Email {email} is {valid_status}: {result.get('reason', '')}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error validating email: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-emails', methods=['POST'])
def api_validate_emails():
    """API endpoint to validate multiple emails."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'emails' not in data:
            return jsonify({'error': 'Emails list is required'}), 400
        
        emails = data.get('emails')
        
        # Validate emails input
        if not isinstance(emails, list):
            return jsonify({'error': 'Emails must be a list'}), 400
            
        if len(emails) > 100:
            return jsonify({'error': 'Maximum of 100 emails can be validated at once'}), 400
        
        # Filter out empty values
        emails = [email for email in emails if email and isinstance(email, str)]
        
        if not emails:
            return jsonify([]), 200
        
        # Log the request
        logger.info(f"Validating {len(emails)} emails")
        
        results = validate_email_list(emails)
        
        # Log success
        valid_count = sum(1 for r in results if r.get('valid', False))
        logger.info(f"Validated {len(emails)} emails, {valid_count} are valid")
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error validating emails: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/enrich', methods=['POST'])
def api_enrich():
    """API endpoint to enrich company data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'website_url' not in data and 'domain' not in data:
            return jsonify({'error': 'Website URL or domain is required'}), 400
        
        # Validate URL if provided
        website_url = data.get('website_url')
        if website_url and not website_url.startswith(('http://', 'https://')):
            return jsonify({'error': 'Invalid URL format. URL must start with http:// or https://'}), 400
        
        # Log the request
        if 'website_url' in data:
            logger.info(f"Enriching data for website: {data['website_url']}")
        else:
            logger.info(f"Enriching data for domain: {data['domain']}")
        
        result = enrich_company_data(data)
        
        # Log success
        logger.info("Data enrichment completed successfully")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error enriching company data: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/batch-enrich', methods=['POST'])
def api_batch_enrich():
    """API endpoint to enrich multiple companies' data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'companies' not in data:
            return jsonify({'error': 'Companies list is required'}), 400
        
        companies = data.get('companies')
        
        # Validate companies input
        if not isinstance(companies, list):
            return jsonify({'error': 'Companies must be a list'}), 400
            
        if len(companies) > 50:
            return jsonify({'error': 'Maximum of 50 companies can be enriched at once'}), 400
            
        if not all(isinstance(company, dict) for company in companies):
            return jsonify({'error': 'Each company must be a dictionary'}), 400
        
        # Log the request
        logger.info(f"Batch enriching {len(companies)} companies")
        
        results = batch_enrich_companies(companies)
        
        # Log success
        logger.info(f"Successfully enriched {len(results)} companies")
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error batch enriching companies: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/linkedin-search', methods=['POST'])
def api_linkedin_search():
    """API endpoint to search for companies on LinkedIn."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'query' not in data:
            return jsonify({'error': 'Query is required'}), 400
        
        query = data.get('query')
        max_results = data.get('max_results', 5)
        
        # Validate max_results
        try:
            max_results = int(max_results)
            if max_results < 1 or max_results > 20:
                return jsonify({'error': 'max_results must be between 1 and 20'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'max_results must be a valid integer'}), 400
        
        # Log the request
        logger.info(f"Searching LinkedIn for: {query} (max_results={max_results})")
        
        results = search_linkedin_companies(query, max_results)
        
        # Log success
        logger.info(f"LinkedIn search for '{query}' returned {len(results)} results")
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Error searching LinkedIn: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/linkedin-company', methods=['POST'])
def api_linkedin_company():
    """API endpoint to get company details from LinkedIn."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        if 'linkedin_url' not in data:
            return jsonify({'error': 'LinkedIn URL is required'}), 400
        
        linkedin_url = data.get('linkedin_url')
        
        # Validate LinkedIn URL
        if not linkedin_url.startswith('https://www.linkedin.com/company/'):
            return jsonify({'error': 'Invalid LinkedIn company URL. URL must start with https://www.linkedin.com/company/'}), 400
        
        # Log the request
        logger.info(f"Getting LinkedIn company details for: {linkedin_url}")
        
        result = get_linkedin_company_details(linkedin_url)
        
        # Log success
        logger.info(f"Successfully retrieved LinkedIn details for {linkedin_url}")
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting LinkedIn company details: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload for batch processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the uploaded file based on its type
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:  # Excel file
                    df = pd.read_excel(filepath)
                
                # Check if DataFrame is empty
                if df.empty:
                    return jsonify({'error': 'The uploaded file contains no data'}), 400
                
                # Extract parameters from form
                website_col = request.form.get('website_column', 'website')
                name_col = request.form.get('name_column')
                domain_col = request.form.get('domain_column')
                
                # Validate website_col exists in the DataFrame
                if website_col not in df.columns and not domain_col:
                    return jsonify({
                        'error': f"Column '{website_col}' not found in the uploaded file. "
                                 f"Available columns: {', '.join(df.columns)}"
                    }), 400
                
                # Validate name_col if provided
                if name_col and name_col not in df.columns:
                    return jsonify({
                        'error': f"Column '{name_col}' not found in the uploaded file. "
                                 f"Available columns: {', '.join(df.columns)}"
                    }), 400
                
                # Validate domain_col if provided
                if domain_col and domain_col not in df.columns:
                    return jsonify({
                        'error': f"Column '{domain_col}' not found in the uploaded file. "
                                 f"Available columns: {', '.join(df.columns)}"
                    }), 400
                
                # Log the request
                logger.info(f"Processing batch file {filename} with {len(df)} rows")
                
                # Enrich the data
                enriched_df = enrich_dataframe(df, website_col, name_col, domain_col)
                
                # Export the enriched data
                export_format = request.form.get('export_format', 'csv')
                export_filename = f"enriched_{filename.rsplit('.', 1)[0]}"
                
                if export_format == 'csv':
                    export_path = export_to_csv(enriched_df, f"{export_filename}.csv")
                else:
                    export_path = export_to_excel(enriched_df, f"{export_filename}.xlsx")
                
                # Log success
                logger.info(f"Batch processing completed, exported to {export_path}")
                
                return jsonify({
                    'success': True,
                    'message': 'File processed successfully',
                    'export_path': export_path,
                    'row_count': len(enriched_df)
                })
                
            except Exception as e:
                logger.error(f"Error processing uploaded file: {str(e)}", exc_info=True)
                return jsonify({'error': str(e)}), 500
        
        return jsonify({'error': 'Invalid file type'}), 400
    except Exception as e:
        logger.error(f"Error in file upload: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@app.route('/exports/<path:filename>')
def download_file(filename):
    """Handle file downloads from the exports directory."""
    try:
        # Security check - prevent directory traversal
        if '..' in filename or filename.startswith('/'):
            abort(404)
            
        export_dir = os.path.join(BASE_DIR, 'exports')
        return send_from_directory(export_dir, filename, as_attachment=True)
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        abort(404)

@app.route('/static/sample_data.csv')
def sample_data():
    """Serve the sample data CSV file."""
    return send_from_directory(os.path.join(BASE_DIR, 'static'), 'sample_data.csv', as_attachment=True)

# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_server_error(e):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return jsonify({'error': e.description}), e.code
    
    # Log non-HTTP exceptions
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    
    # Return a generic 500 error response
    return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting LeadGen Tool on {host}:{port} (debug={debug})")
    app.run(debug=debug, host=host, port=port)
