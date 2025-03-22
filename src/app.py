import streamlit as st
import pandas as pd
import os
import time
import json
from scraper import LeadScraper
import traceback

# Page configuration
st.set_page_config(
    page_title="Lead Generation Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #2563EB;
    }
    .info-box {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .warning-box {
        background-color: #FEF3C7;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .stProgress > div > div {
        background-color: #2563EB;
    }
</style>
""", unsafe_allow_html=True)

def save_configuration(config):
    """Save the current configuration to a file."""
    try:
        os.makedirs('config', exist_ok=True)
        timestamp = int(time.time())
        filename = f"config/config_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(config, f)
        return filename
    except Exception as e:
        st.error(f"Error saving configuration: {str(e)}")
        return None

def load_configuration(file):
    """Load a configuration from a file."""
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Error loading configuration: {str(e)}")
        return None

def main():
    # Initialize session state variables if they don't exist
    if 'leads' not in st.session_state:
        st.session_state.leads = []
    if 'filtered_leads' not in st.session_state:
        st.session_state.filtered_leads = []
    if 'lead_analysis' not in st.session_state:
        st.session_state.lead_analysis = {}
    if 'scraper' not in st.session_state:
        st.session_state.scraper = LeadScraper()
    if 'config_files' not in st.session_state:
        # Scan for existing config files
        st.session_state.config_files = []
        if os.path.exists('config'):
            st.session_state.config_files = [f for f in os.listdir('config') if f.endswith('.json')]
    
    # Header
    st.markdown('<div class="main-header">Lead Generation Tool</div>', unsafe_allow_html=True)
    st.markdown(
        "A powerful tool to identify and collect potential business leads from websites."
    )
    
    # Create sidebar for inputs
    with st.sidebar:
        st.markdown('<div class="sub-header">Configuration</div>', unsafe_allow_html=True)
        
        # Configuration management
        with st.expander("Configuration Management"):
            # Save current configuration
            if st.button("Save Current Configuration"):
                config = {
                    'url': st.session_state.get('url', ''),
                    'keywords': st.session_state.get('keywords', []),
                    'exclude_keywords': st.session_state.get('exclude_keywords', []),
                    'min_data_points': st.session_state.get('min_data_points', 3),
                    'max_pages': st.session_state.get('max_pages', 1),
                    'respect_robots': st.session_state.get('respect_robots', True)
                }
                filename = save_configuration(config)
                if filename:
                    st.success(f"Configuration saved to {filename}")
                    # Update config files list
                    if os.path.exists('config'):
                        st.session_state.config_files = [f for f in os.listdir('config') if f.endswith('.json')]
            
            # Load configuration
            if st.session_state.config_files:
                selected_config = st.selectbox(
                    "Load Saved Configuration", 
                    options=st.session_state.config_files,
                    index=0
                )
                
                if st.button("Load Selected Configuration"):
                    config_path = os.path.join('config', selected_config)
                    config = load_configuration(config_path)
                    if config:
                        # Update session state
                        for key, value in config.items():
                            st.session_state[key] = value
                        st.success("Configuration loaded successfully!")
        
        # Input for target URL
        st.markdown("### Target Website")
        url = st.text_input(
            "Enter website URL to scrape:", 
            value=st.session_state.get('url', ''),
            placeholder="https://example.com",
            help="Enter the full URL including https:// or http://"
        )
        st.session_state['url'] = url
        
        # Crawling options
        with st.expander("Crawling Options"):
            max_pages = st.slider(
                "Maximum pages to crawl:", 
                min_value=1, 
                max_value=10, 
                value=st.session_state.get('max_pages', 1),
                help="Higher values will result in more data but slower performance"
            )
            st.session_state['max_pages'] = max_pages
            
            respect_robots = st.checkbox(
                "Respect robots.txt", 
                value=st.session_state.get('respect_robots', True),
                help="Checking this box ensures ethical scraping by following website crawling rules"
            )
            st.session_state['respect_robots'] = respect_robots
        
        # Input for filtering options
        st.markdown("### Filtering Options")
        
        # Industry keywords
        st.markdown("#### Keywords to Include")
        keywords_input = st.text_input(
            "Enter keywords separated by commas:", 
            value=", ".join(st.session_state.get('keywords', [])) if st.session_state.get('keywords') else "",
            placeholder="tech, software, AI",
            help="Leads must contain at least one of these keywords"
        )
        keywords = [k.strip() for k in keywords_input.split(',')] if keywords_input else []
        st.session_state['keywords'] = keywords
        
        # Exclude keywords
        st.markdown("#### Keywords to Exclude")
        exclude_input = st.text_input(
            "Enter keywords to exclude (comma separated):", 
            value=", ".join(st.session_state.get('exclude_keywords', [])) if st.session_state.get('exclude_keywords') else "",
            placeholder="agency, freelance",
            help="Leads containing any of these keywords will be filtered out"
        )
        exclude_keywords = [k.strip() for k in exclude_input.split(',')] if exclude_input else []
        st.session_state['exclude_keywords'] = exclude_keywords
        
        # Minimum data quality
        min_data_points = st.slider(
            "Minimum data points required:", 
            min_value=2, 
            max_value=8, 
            value=st.session_state.get('min_data_points', 3),
            help="Minimum number of non-empty fields a lead must have"
        )
        st.session_state['min_data_points'] = min_data_points
        
        # Advanced filtering options
        with st.expander("Advanced Filtering"):
            st.markdown("##### Field-Specific Filtering")
            st.info("These filters apply to specific fields rather than the entire lead data.")
            
            field_options = [
                "Company Name", "Industry/Keywords", "Description", 
                "Email", "Contact Name", "Job Title"
            ]
            
            filter_field = st.selectbox("Select field to filter", field_options)
            
            filter_contains = st.text_input(
                f"{filter_field} contains:",
                placeholder="Enter terms separated by commas"
            )
            
            filter_not_contains = st.text_input(
                f"{filter_field} does not contain:",
                placeholder="Enter terms separated by commas"
            )
            
            # Build advanced filters dict
            advanced_filters = {}
            if filter_contains or filter_not_contains:
                advanced_filters[filter_field] = {}
                if filter_contains:
                    advanced_filters[filter_field]['contains'] = [term.strip() for term in filter_contains.split(',')]
                if filter_not_contains:
                    advanced_filters[filter_field]['not_contains'] = [term.strip() for term in filter_not_contains.split(',')]
            
        # Button to generate leads
        generate_button = st.button("Generate Leads", type="primary")
    
    # Main content area
    if generate_button and url:
        try:
            with st.spinner("Scraping website for lead data..."):
                # Update scraper settings
                st.session_state.scraper = LeadScraper(respect_robots_txt=respect_robots)
                
                # Add progress tracking
                progress_bar = st.progress(0)
                progress_text = st.empty()
                progress_text.text("Starting scraper...")
                
                # Scrape the website
                progress_text.text("Scraping primary website...")
                scraped_leads = st.session_state.scraper.scrape_website(url, max_pages=max_pages)
                progress_bar.progress(50)
                
                # Check for errors
                if isinstance(scraped_leads, dict) and 'error' in scraped_leads:
                    st.error(f"Error: {scraped_leads['error']}")
                else:
                    st.session_state.leads = scraped_leads
                    progress_text.text("Cleaning and validating data...")
                    progress_bar.progress(70)
                    
                    # Clean and validate the data
                    cleaned_leads = st.session_state.scraper.validate_and_clean_data(scraped_leads)
                    
                    progress_text.text("Filtering leads...")
                    progress_bar.progress(85)
                    
                    # Filter the leads
                    st.session_state.filtered_leads = st.session_state.scraper.filter_leads(
                        cleaned_leads, 
                        keywords=keywords if keywords_input else None,
                        exclude_keywords=exclude_keywords if exclude_input else None,
                        min_data_points=min_data_points,
                        advanced_filters=advanced_filters if advanced_filters else None
                    )
                    
                    progress_text.text("Analyzing leads...")
                    progress_bar.progress(95)
                    
                    # Analyze the leads
                    st.session_state.lead_analysis = st.session_state.scraper.analyze_leads(
                        st.session_state.filtered_leads
                    )
                    
                    progress_bar.progress(100)
                    progress_text.text("Process complete!")
                    
                    # Display success message
                    if st.session_state.filtered_leads:
                        st.success(f"Successfully found {len(st.session_state.filtered_leads)} leads!")
                    else:
                        st.warning("No leads found matching your criteria.")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")
            st.code(traceback.format_exc())
    
    # Display lead analysis if available
    if st.session_state.lead_analysis and st.session_state.lead_analysis.get('total', 0) > 0:
        st.markdown('<div class="sub-header">Lead Analysis</div>', unsafe_allow_html=True)
        
        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Leads", st.session_state.lead_analysis.get('total', 0))
        with col2:
            st.metric("With Email", st.session_state.lead_analysis.get('with_email', 0))
        with col3:
            st.metric("With Phone", st.session_state.lead_analysis.get('with_phone', 0))
        with col4:
            st.metric("With Contact Name", st.session_state.lead_analysis.get('with_contact_name', 0))
        
        # Show top industries if available
        col1, col2 = st.columns(2)
        
        with col1:
            if 'top_industries' in st.session_state.lead_analysis and st.session_state.lead_analysis['top_industries']:
                st.markdown("#### Top Industries/Keywords")
                for industry, count in st.session_state.lead_analysis['top_industries']:
                    st.text(f"• {industry}: {count}")
        
        with col2:
            if 'top_domains' in st.session_state.lead_analysis and st.session_state.lead_analysis['top_domains']:
                st.markdown("#### Top Domains")
                for domain, count in st.session_state.lead_analysis['top_domains']:
                    st.text(f"• {domain}: {count}")
    
    # Display the filtered leads if available
    if st.session_state.filtered_leads:
        st.markdown('<div class="sub-header">Lead Results</div>', unsafe_allow_html=True)
        
        # Search and filter within results
        search_term = st.text_input("Search within results:", placeholder="Enter search term")
        
        # Apply search filter if provided
        displayed_leads = st.session_state.filtered_leads
        if search_term:
            displayed_leads = [
                lead for lead in st.session_state.filtered_leads
                if any(search_term.lower() in str(value).lower() for value in lead.values())
            ]
            st.info(f"Found {len(displayed_leads)} leads matching '{search_term}'")
        
        # Convert to DataFrame for display
        df = pd.DataFrame(displayed_leads)
        
        # Show the DataFrame
        st.dataframe(df)
        
        # Export options
        st.markdown("#### Export Options")
        
        col1, col2 = st.columns(2)
        with col1:
            # Export to CSV
            if st.button("Download as CSV"):
                try:
                    # Create data directory if it doesn't exist
                    os.makedirs('data', exist_ok=True)
                    
                    # Generate timestamp for filename
                    timestamp = int(time.time())
                    filename = f"data/leads_{timestamp}.csv"
                    
                    # Export to CSV
                    result = st.session_state.scraper.export_to_csv(
                        displayed_leads, 
                        filename
                    )
                    
                    if isinstance(result, str) and result.startswith("Error"):
                        st.error(result)
                    else:
                        # Create download link
                        with open(filename, 'rb') as f:
                            csv_data = f.read()
                        
                        st.download_button(
                            label="Click to Download",
                            data=csv_data,
                            file_name=f"leads_{timestamp}.csv",
                            mime="text/csv"
                        )
                except Exception as e:
                    st.error(f"Error exporting to CSV: {str(e)}")
                    st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
