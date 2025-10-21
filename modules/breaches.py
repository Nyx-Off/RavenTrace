#!/usr/bin/env python3
"""
BreachChecker - Vérification des données compromises
Utilise multiples sources de fuites connus
"""

import requests
import logging
import hashlib
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class BreachChecker:
    """Vérification des fuites de données"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Raven-Trace/1.0'
        }
        self.timeout = 10
    
    def check_breaches(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier si l'email a été compromis"""
        breaches = []
        
        # 1. Have I Been Pwned API
        breaches.extend(self._check_hibp(email))
        
        # 2. LeakCheck API
        breaches.extend(self._check_leakcheck(email))
        
        # 3. Breach Database Aggregators
        breaches.extend(self._check_breachodb(email))
        
        return breaches
    
    def _check_hibp(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier Have I Been Pwned"""
        results = []
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                breaches_data = resp.json()
                for breach in breaches_data:
                    results.append({
                        'source': 'Have I Been Pwned',
                        'breach_name': breach.get('Name'),
                        'date': breach.get('BreachDate'),
                        'compromised_count': breach.get('PwnCount'),
                        'data_types': breach.get('DataClasses'),
                        'title': breach.get('Title'),
                        'description': breach.get('Description'),
                        'url': f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                    })
            elif resp.status_code == 404:
                logger.info(f"Email {email} non trouvé dans HIBP (bon signe)")
                results.append({
                    'source': 'Have I Been Pwned',
                    'status': 'not_found',
                    'message': 'Email non trouvé dans les données compromises'
                })
            else:
                logger.debug(f"HIBP réponse: {resp.status_code}")
        except Exception as e:
            logger.debug(f"HIBP erreur: {e}")
        
        return results
    
    def _check_leakcheck(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier LeakCheck"""
        results = []
        
        try:
            # LeakCheck (gratuit sans API key pour recherche basique)
            url = f"https://leakcheck.io/search?q={email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200 and "not found" not in resp.text.lower():
                # Scraper les résultats
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Chercher les breaches dans la réponse
                if soup.find('div', class_='breaches'):
                    results.append({
                        'source': 'LeakCheck',
                        'found': True,
                        'url': url,
                        'requires_manual_check': True
                    })
        except Exception as e:
            logger.debug(f"LeakCheck erreur: {e}")
        
        return results
    
    def _check_breachodb(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier BreachODB et autres agrégateurs"""
        results = []
        
        try:
            # BreachDatabase API
            url = f"https://breachdirectory.org/api/v1/search?term={email}&limit=100"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                
                if data.get('found'):
                    for breach in data.get('results', []):
                        results.append({
                            'source': 'Breach Directory',
                            'breach_name': breach.get('sources'),
                            'date_found': breach.get('last_seen'),
                            'exposed_data': breach.get('exposed_data'),
                            'url': f"https://breachdirectory.org/?term={email}",
                        })
        except Exception as e:
            logger.debug(f"BreachODB erreur: {e}")
        
        return results
    
    def check_password_strength(self, email: str) -> Dict[str, Any]:
        """Analyser la force des mots de passe potentiels (éducatif)"""
        # Note: Fonction éducative, ne pas utiliser malveillamment
        
        result = {
            'warning': 'Educational purpose only',
            'recommendations': [
                'Utiliser des mots de passe uniques par site',
                'Minimum 16 caractères',
                'Combiner majuscules, minuscules, chiffres, symboles',
                'Utiliser un gestionnaire de mots de passe',
            ]
        }
        
        return result