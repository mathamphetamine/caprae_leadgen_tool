"""
Data enrichment modules for the LeadGen Tool

This package provides tools for validating and enriching contact information:

- email_validator: Email validation and verification tools
- data_enricher: Company data enrichment functionality

These modules help improve lead quality by validating email deliverability
and adding additional context to basic company information.
"""

from leadgen_tool.enricher.email_validator import validate_email_single, validate_email_list, filter_valid_emails, EmailValidator
from leadgen_tool.enricher.data_enricher import enrich_company_data, batch_enrich_companies, enrich_dataframe, DataEnricher

__all__ = [
    'validate_email_single',
    'validate_email_list',
    'filter_valid_emails',
    'EmailValidator',
    'enrich_company_data',
    'batch_enrich_companies',
    'enrich_dataframe',
    'DataEnricher',
]
