#!/usr/bin/env python3
"""
data_aggregators.py - Intégrations avec agrégateurs de données
"""

import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DataAggregators:
    """Recherche sur agrégateurs de données"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def spokeo_search_email(self, email: str) -> Dict[str, Any]:
        """Rechercher un email sur Spokeo"""
        result = {
            'platform': 'spokeo',
            'query': email,
            'found': False,
            'url': None
        }
        
        try:
            url = f"https://www.spokeo.com/search?q={email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200 and len(resp.text) > 1000:
                result['found'] = True
                result['url'] = url
                # Extraire plus de données si possible
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Parser les résultats
        except Exception as e:
            logger.debug(f"Spokeo search error: {e}")
        
        return result
    
    def whitepages_search(self, query: str, query_type: str = 'email') -> Dict[str, Any]:
        """Rechercher sur WhitePages"""
        result = {
            'platform': 'whitepages',
            'query': query,
            'type': query_type,
            'found': False,
            'url': None
        }
        
        try:
            if query_type == 'email':
                url = f"https://www.whitepages.com/search/results?SearchType=email&q={query}"
            elif query_type == 'phone':
                url = f"https://www.whitepages.com/search/results?q={query}"
            else:
                return result
            
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
        except Exception as e:
            logger.debug(f"WhitePages search error: {e}")
        
        return result
    
    def radaris_search(self, email: str) -> Dict[str, Any]:
        """Rechercher un email sur Radaris"""
        result = {
            'platform': 'radaris',
            'query': email,
            'found': False,
            'url': None
        }
        
        try:
            url = f"https://radaris.com/search/email/{email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
        except Exception as e:
            logger.debug(f"Radaris search error: {e}")
        
        return result
    
    def pipl_search(self, email: str) -> Dict[str, Any]:
        """Rechercher sur Pipl"""
        result = {
            'platform': 'pipl',
            'query': email,
            'found': False,
            'url': None
        }
        
        try:
            url = f"https://pipl.com/search/?q={email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
        except Exception as e:
            logger.debug(f"Pipl search error: {e}")
        
        return result
    
    def truthfinder_search(self, email: str) -> Dict[str, Any]:
        """Rechercher sur TruthFinder"""
        result = {
            'platform': 'truthfinder',
            'query': email,
            'found': False,
            'url': None
        }
        
        try:
            url = f"https://www.truthfinder.com/search?q={email}"
            resp = requests.head(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
        except Exception as e:
            logger.debug(f"TruthFinder search error: {e}")
        
        return result
    
    def peoplefinder_search(self, email: str) -> Dict[str, Any]:
        """Rechercher sur PeopleFinder"""
        result = {
            'platform': 'peoplefinder',
            'query': email,
            'found': False,
            'url': None
        }
        
        try:
            url = f"https://www.peoplefinder.com/search?q={email}"
            resp = requests.head(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
        except Exception as e:
            logger.debug(f"PeopleFinder search error: {e}")
        
        return result
    
    def search_all_aggregators(self, query: str, query_type: str = 'email') -> List[Dict[str, Any]]:
        """Chercher sur tous les agrégateurs"""
        results = []
        
        if query_type == 'email':
            results.append(self.spokeo_search_email(query))
            results.append(self.whitepages_search(query, 'email'))
            results.append(self.radaris_search(query))
            results.append(self.pipl_search(query))
            results.append(self.truthfinder_search(query))
            results.append(self.peoplefinder_search(query))
        elif query_type == 'phone':
            results.append(self.whitepages_search(query, 'phone'))
            results.append(self.spokeo_search_email(query))
        
        return [r for r in results if r]

# Instance global
data_aggregators = DataAggregators()