#!/usr/bin/env python3
"""
helpers.py - Fonctions utilitaires générales pour Raven Trace
"""

import re
import hashlib
from typing import Any, Dict, List
from urllib.parse import quote, unquote
import random
from fake_useragent import UserAgent

# User agents
ua = UserAgent()

def get_random_user_agent() -> str:
    """Obtenir un user agent aléatoire"""
    try:
        return ua.random
    except:
        agents = [
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        ]
        return random.choice(agents)

def sanitize_string(s: str, max_length: int = 255) -> str:
    """Nettoyer une chaîne"""
    s = s.strip()
    if len(s) > max_length:
        s = s[:max_length]
    return s

def is_valid_email_format(email: str) -> bool:
    """Vérifier le format basic d'un email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_domain(email: str) -> str:
    """Extraire le domaine d'un email"""
    try:
        return email.split('@')[1]
    except:
        return None

def hash_string(s: str, algorithm: str = 'sha256') -> str:
    """Hasher une chaîne"""
    if algorithm == 'sha256':
        return hashlib.sha256(s.encode()).hexdigest()
    elif algorithm == 'md5':
        return hashlib.md5(s.encode()).hexdigest()
    elif algorithm == 'sha1':
        return hashlib.sha1(s.encode()).hexdigest()
    return None

def url_encode(s: str) -> str:
    """Encoder une URL"""
    return quote(s, safe='')

def url_decode(s: str) -> str:
    """Décoder une URL"""
    return unquote(s)

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict:
    """Aplatir un dictionnaire"""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def merge_dicts(*dicts: Dict) -> Dict:
    """Fusionner plusieurs dictionnaires"""
    result = {}
    for d in dicts:
        result.update(d)
    return result

def remove_duplicates(items: List) -> List:
    """Supprimer les doublons d'une liste"""
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

def sort_dict_by_value(d: Dict, reverse: bool = True) -> Dict:
    """Trier un dictionnaire par valeur"""
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=reverse))

def truncate_string(s: str, length: int = 50, suffix: str = '...') -> str:
    """Tronquer une chaîne"""
    if len(s) <= length:
        return s
    return s[:length - len(suffix)] + suffix

def safe_get(d: Dict, *keys, default=None):
    """Accès sécurisé à un dictionnaire imbriqué"""
    for key in keys:
        if isinstance(d, dict):
            d = d.get(key)
        else:
            return default
    return d if d is not None else default

def retry_decorator(max_retries: int = 3, delay: int = 1):
    """Décorateur pour réessayer une fonction"""
    import time
    from functools import wraps
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def normalize_whitespace(s: str) -> str:
    """Normaliser les espaces blancs"""
    return ' '.join(s.split())

def remove_special_chars(s: str, keep_chars: str = '') -> str:
    """Supprimer les caractères spéciaux"""
    pattern = f'[^a-zA-Z0-9{keep_chars}]'
    return re.sub(pattern, '', s)

def is_phone_like(s: str) -> bool:
    """Vérifier si la chaîne ressemble à un téléphone"""
    s = s.replace(' ', '').replace('-', '').replace('+', '')
    return len(s) >= 7 and len(s) <= 15 and s.isdigit()

def is_url(s: str) -> bool:
    """Vérifier si la chaîne est une URL"""
    pattern = r'^https?://'
    return bool(re.match(pattern, s))

def extract_urls(text: str) -> List[str]:
    """Extraire les URLs d'un texte"""
    pattern = r'https?://[^\s]+'
    return re.findall(pattern, text)