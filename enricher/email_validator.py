import re
import socket
import logging
import dns.resolver
from email_validator import validate_email, EmailNotValidError

from leadgen_tool.utils.config import EMAIL_CHECK_TIMEOUT
from leadgen_tool.utils.helpers import rate_limit

logger = logging.getLogger(__name__)

class EmailValidator:
    """Validate email addresses using various methods."""
    
    def __init__(self):
        pass
    
    def syntax_check(self, email):
        """Check if email has valid syntax."""
        if not email:
            return False
        
        # Simple regex pattern for basic validation
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def domain_check(self, email):
        """Check if the email domain has valid MX records."""
        if not email:
            return False
        
        try:
            domain = email.split('@')[-1]
            # Check for MX records
            dns.resolver.resolve(domain, 'MX')
            return True
        except Exception as e:
            logger.debug(f"Domain check failed for {email}: {str(e)}")
            return False
    
    @rate_limit
    def full_check(self, email):
        """Perform a comprehensive email validation."""
        if not email:
            return {'valid': False, 'reason': 'Empty email'}
        
        # Step 1: Syntax check
        if not self.syntax_check(email):
            return {'valid': False, 'reason': 'Invalid syntax'}
        
        # Step 2: Use email_validator library for deeper validation
        try:
            valid = validate_email(email, check_deliverability=True)
            normalized_email = valid.normalized
            return {
                'valid': True, 
                'normalized_email': normalized_email,
                'reason': 'Valid'
            }
        except EmailNotValidError as e:
            return {'valid': False, 'reason': str(e)}
    
    def validate_emails(self, emails):
        """Validate a list of emails and return results."""
        if not emails:
            return []
        
        results = []
        for email in emails:
            if not email:
                continue
                
            check_result = self.full_check(email)
            results.append({
                'email': email,
                'valid': check_result['valid'],
                'reason': check_result.get('reason', ''),
                'normalized_email': check_result.get('normalized_email', email)
            })
        
        return results
    
    def filter_valid_emails(self, emails):
        """Return only valid emails from a list."""
        validation_results = self.validate_emails(emails)
        return [result['normalized_email'] for result in validation_results if result['valid']]

# Functional interface for simpler usage
def validate_email_list(emails):
    """Validate a list of emails."""
    validator = EmailValidator()
    return validator.validate_emails(emails)

def validate_email_single(email):
    """Validate a single email address."""
    validator = EmailValidator()
    return validator.full_check(email)

def filter_valid_emails(emails):
    """Filter only valid emails from a list."""
    validator = EmailValidator()
    return validator.filter_valid_emails(emails)
