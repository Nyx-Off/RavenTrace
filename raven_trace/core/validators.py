#!/usr/bin/env python3
"""
Validators - Validation et normalisation des inputs
"""

import re
import logging
from email_validator import validate_email as validate_email_lib, EmailNotValidError
import phonenumbers

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Exception de validation"""
    pass

def validate_email(email: str) -> bool:
    """Valide un email"""
    try:
        # Normaliser
        email = email.lower().strip()
        
        # Utiliser la lib email-validator
        validate_email_lib(email, check_deliverability=False)
        return True
    except EmailNotValidError as e:
        logger.debug(f"Email invalide: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur validation email: {e}")
        return False

def validate_phone(phone: str, country_code: str = "FR") -> bool:
    """Valide un numéro de téléphone"""
    try:
        # Normaliser
        phone = phone.strip().replace(' ', '').replace('-', '')
        
        # Parser avec phonenumbers
        parsed = phonenumbers.parse(phone, country_code)
        
        # Vérifier validité
        is_valid = phonenumbers.is_valid_number(parsed)
        
        if is_valid:
            logger.debug(f"Phone valide: {phone} ({country_code})")
        
        return is_valid
    except phonenumbers.NumberParseException as e:
        logger.debug(f"Phone parsing erreur: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur validation phone: {e}")
        return False

def validate_username(username: str) -> bool:
    """Valide un nom d'utilisateur"""
    try:
        # Normaliser
        username = username.strip()
        
        # Vérifier longueur
        if len(username) < 2 or len(username) > 50:
            logger.debug(f"Username hors limites: {len(username)}")
            return False
        
        # Caractères autorisés
        if not re.match(r'^[a-zA-Z0-9._-]+$', username):
            logger.debug(f"Username caractères non autorisés: {username}")
            return False
        
        logger.debug(f"Username valide: {username}")
        return True
    except Exception as e:
        logger.error(f"Erreur validation username: {e}")
        return False

def normalize_email(email: str) -> str:
    """Normalise un email"""
    return email.lower().strip()

def normalize_phone(phone: str, country_code: str = "FR") -> str:
    """Normalise un numéro de téléphone"""
    try:
        phone = phone.strip().replace(' ', '').replace('-', '')
        parsed = phonenumbers.parse(phone, country_code)
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    except:
        return phone

def normalize_username(username: str) -> str:
    """Normalise un username"""
    return username.lower().strip()