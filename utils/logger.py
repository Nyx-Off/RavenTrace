#!/usr/bin/env python3
"""
logger.py - Système de logging avancé pour Raven Trace
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

def setup_logging(log_level=logging.DEBUG):
    """Configurer le logging avec fichier et console"""
    
    # Créer le répertoire des logs
    log_dir = Path.home() / '.raven_trace' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'log'
    
    # Format de log détaillé
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger root
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Handler fichier avec rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    # Réduire le bruit des libs externes
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('selenium').setLevel(logging.WARNING)
    logging.getLogger('dns').setLevel(logging.WARNING)
    
    return root_logger

def get_logger(name):
    """Obtenir un logger nommé"""
    return logging.getLogger(name)