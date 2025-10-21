#!/usr/bin/env python3
"""
EmailLookup - Recherche avancée par email
Multiple sources, APIs, et scrapers personnalisés
"""

import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import httpx
import json

logger = logging.getLogger(__name__)

class EmailLookup:
    """Moteur de recherche pour emails"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def check_reputation(self, email: str) -> Dict[str, Any]:
        """Vérifier la réputation de l'email"""
        results = {}
        
        # 1. AbuseIPDB Email Checker (alternatif)
        try:
            # Scrape depuis emailrep.io (source publique)
            url = f"https://emailrep.io/{email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                results['emailrep'] = {
                    'reputation': data.get('reputation'),
                    'suspicious': data.get('suspicious'),
                    'details': data.get('details')
                }
        except Exception as e:
            logger.debug(f"EmailRep erreur: {e}")
        
        # 2. Vérifier via HunterIO API (public domain search)
        try:
            domain = email.split('@')[1]
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}"
            resp = requests.get(url, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                results['hunter'] = {
                    'found': len(data.get('data', {}).get('emails', [])) > 0,
                    'company': data.get('data', {}).get('organization')
                }
        except Exception as e:
            logger.debug(f"Hunter erreur: {e}")
        
        return results
    
    def check_dns(self, email: str) -> Dict[str, Any]:
        """Vérifier les enregistrements DNS du domaine"""
        import dns.resolver
        results = {}
        
        try:
            domain = email.split('@')[1]
            
            # Enregistrements MX
            mx_records = []
            try:
                for mx in dns.resolver.resolve(domain, 'MX'):
                    mx_records.append(str(mx.exchange))
            except:
                pass
            
            # Enregistrements SPF
            spf_records = []
            try:
                for txt in dns.resolver.resolve(domain, 'TXT'):
                    if 'v=spf1' in str(txt):
                        spf_records.append(str(txt))
            except:
                pass
            
            results['dns'] = {
                'mx_records': mx_records,
                'spf_configured': len(spf_records) > 0,
                'valid_domain': len(mx_records) > 0
            }
        except Exception as e:
            logger.debug(f"DNS erreur: {e}")
        
        return results
    
    def search_data_brokers(self, email: str) -> List[Dict[str, Any]]:
        """Chercher sur les agrégateurs de données"""
        brokers = []
        
        # 1. Search via Sherlock (osint-framework)
        try:
            # Sherlock-like search on various platforms
            platforms = [
                "https://spokeo.com/search?q=",
                "https://www.whitepages.com/search/results?SearchType=email&q=",
                "https://radaris.com/search/email/",
            ]
            
            for platform in platforms:
                try:
                    resp = requests.get(platform + email, headers=self.headers, timeout=5)
                    if resp.status_code == 200 and len(resp.text) > 100:
                        brokers.append({
                            'platform': platform.split('/')[2],
                            'found': True,
                            'url': platform + email
                        })
                except:
                    pass
        except Exception as e:
            logger.debug(f"Data brokers erreur: {e}")
        
        return brokers
    
    def search_social(self, email: str) -> List[Dict[str, str]]:
        """Chercher les profils sociaux associés à l'email"""
        profiles = []
        
        # Méthode: Scraper les résultats Google spécialisés
        try:
            search_url = f"https://www.google.com/search?q={email} site:linkedin.com OR site:facebook.com OR site:twitter.com"
            # Note: Utiliser un vrai navigateur + Selenium pour un vrai scraping
            
            # Alternatively, search known platforms directly
            platforms = {
                'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={email}",
                'facebook': f"https://www.facebook.com/search/people/?q={email}",
                'twitter': f"https://twitter.com/search?q={email}",
            }
            
            for platform, url in platforms.items():
                profiles.append({
                    'platform': platform,
                    'search_url': url,
                    'type': 'social_media'
                })
        except Exception as e:
            logger.debug(f"Social search erreur: {e}")
        
        return profiles