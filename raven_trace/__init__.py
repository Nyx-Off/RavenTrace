#!/usr/bin/env python3
"""
Raven Trace - __init__.py files for all modules
Copier ce contenu dans chaque dossier
"""

# ========== raven_trace/__init__.py ==========
"""
Raven Trace - Advanced OSINT Intelligence Tool
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from raven_trace.core.engine import SearchEngine

__all__ = ['SearchEngine']


# ========== raven_trace/core/__init__.py ==========
"""
Core module - Engine et logique principale
"""

from raven_trace.core.engine import SearchEngine
from raven_trace.core.validators import (
    validate_email,
    validate_phone,
    validate_username
)

__all__ = [
    'SearchEngine',
    'validate_email',
    'validate_phone',
    'validate_username'
]


# ========== raven_trace/modules/__init__.py ==========
"""
Modules - Lookups spécialisés
"""

from raven_trace.modules.email_lookup import EmailLookup
from raven_trace.modules.phone_lookup import PhoneLookup
from raven_trace.modules.username_lookup import UsernameLookup
from raven_trace.modules.breaches import BreachChecker

__all__ = [
    'EmailLookup',
    'PhoneLookup',
    'UsernameLookup',
    'BreachChecker'
]


# ========== raven_trace/storage/__init__.py ==========
"""
Storage module - Gestion cache et base de données
"""

from raven_trace.storage.database import CacheDB

__all__ = ['CacheDB']


# ========== raven_trace/utils/__init__.py ==========
"""
Utils module - Utilitaires généraux
"""

from raven_trace.utils.formatter import (
    format_results,
    create_results_table,
    export_json,
    export_csv
)
from raven_trace.utils.logger import setup_logging

__all__ = [
    'format_results',
    'create_results_table',
    'export_json',
    'export_csv',
    'setup_logging'
]


# ========== raven_trace/cli/__init__.py ==========
"""
CLI module - Interface en ligne de commande
"""

from raven_trace.cli.interface import (
    show_banner,
    show_menu,
    get_search_mode,
    search_email_interactive,
    search_phone_interactive,
    search_username_interactive,
    show_help,
    show_error,
    show_success,
    show_warning,
    show_info
)

__all__ = [
    'show_banner',
    'show_menu',
    'get_search_mode',
    'search_email_interactive',
    'search_phone_interactive',
    'search_username_interactive',
    'show_help',
    'show_error',
    'show_success',
    'show_warning',
    'show_info'
]