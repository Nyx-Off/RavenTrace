"""
Core module - Engine et logique principale
"""

from core.engine import SearchEngine
from core.validators import (
    validate_email,
    validate_phone,
    validate_username,
    normalize_email,
    normalize_phone,
    normalize_username,
)

__all__ = [
    'SearchEngine',
    'validate_email',
    'validate_phone',
    'validate_username',
    'normalize_email',
    'normalize_phone',
    'normalize_username',
]
