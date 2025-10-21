"""
Utils module - Utilitaires généraux
"""

from utils.formatter import (
    format_results,
    create_results_table,
    export_json,
    export_csv,
)
from utils.logger import setup_logging, get_logger
from utils.helpers import (
    get_random_user_agent,
    sanitize_string,
    is_valid_email_format,
    extract_domain,
    hash_string,
    flatten_dict,
)

__all__ = [
    'format_results',
    'create_results_table',
    'export_json',
    'export_csv',
    'setup_logging',
    'get_logger',
    'get_random_user_agent',
    'sanitize_string',
    'is_valid_email_format',
    'extract_domain',
    'hash_string',
    'flatten_dict',
]
