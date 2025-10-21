#!/usr/bin/env python3
"""
EmailLookup - Recherche avancée par email avec vrais résultats
APIs publiques et scraping responsable
"""

import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import json

logger = logging.getLogger(__name__)

class EmailLookup:
    """Moteur de recherche pour emails avec résultats réels"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 15
    
    def check_reputation(self, email: str) -> Dict[str, Any]:
        """Vérifier la réputation de l'email via EmailRep.io"""
        results = {}
        
        try:
            # EmailRep.io - Source réelle et libre d'accès
            url = f"https://emailrep.io/{email}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results['emailrep'] = {
                    'reputation': data.get('reputation', 'N/A'),
                    'suspicious': data.get('suspicious', False),
                    'references': data.get('references', 0),
                    'details': {
                        'blacklisted': data.get('details', {}).get('blacklisted', False),
                        'malicious_activity': data.get('details', {}).get('malicious_activity', False),
                        'credentials_leaked': data.get('details', {}).get('credentials_leaked', False),
                        'spam': data.get('details', {}).get('spam', False),
                        'domain_exists': data.get('details', {}).get('domain_exists', False),
                        'domain_reputation': data.get('details', {}).get('domain_reputation', 'N/A')
                    }
                }
                logger.info(f"EmailRep données reçues pour {email}")
            else:
                logger.debug(f"EmailRep réponse {resp.status_code}")
        except requests.exceptions.Timeout:
            logger.warning("EmailRep timeout")
        except Exception as e:
            logger.debug(f"EmailRep erreur: {e}")
        
        return results
    
    def check_dns(self, email: str) -> Dict[str, Any]:
        """Vérifier les enregistrements DNS du domaine"""
        import dns.resolver
        results = {}
        
        try:
            domain = email.split('@')[1]
            
            # MX Records
            mx_records = []
            try:
                for mx in dns.resolver.resolve(domain, 'MX'):
                    mx_records.append({
                        'exchange': str(mx.exchange),
                        'priority': mx.preference
                    })
            except Exception as e:
                logger.debug(f"MX lookup error: {e}")
            
            # SPF Records
            spf_records = []
            try:
                for txt in dns.resolver.resolve(domain, 'TXT'):
                    txt_str = str(txt)
                    if 'v=spf1' in txt_str:
                        spf_records.append(txt_str)
            except Exception as e:
                logger.debug(f"SPF lookup error: {e}")
            
            # DMARC Records
            dmarc_records = []
            try:
                for txt in dns.resolver.resolve(f"_dmarc.{domain}", 'TXT'):
                    dmarc_records.append(str(txt))
            except Exception as e:
                logger.debug(f"DMARC lookup error: {e}")
            
            results['dns'] = {
                'domain': domain,
                'mx_records': mx_records,
                'spf_configured': len(spf_records) > 0,
                'spf_records': spf_records,
                'dmarc_configured': len(dmarc_records) > 0,
                'dmarc_records': dmarc_records,
                'valid_domain': len(mx_records) > 0
            }
            logger.info(f"DNS records trouvés pour {domain}")
        except Exception as e:
            logger.debug(f"DNS erreur: {e}")
        
        return results
    
    def check_breaches(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier les fuites de données - Have I Been Pwned"""
        breaches = []
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {**self.headers, 'User-Agent': 'Raven-Trace/1.0'}
            
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            time.sleep(1.5)  # Rate limiting respectueux
            
            if resp.status_code == 200:
                data = resp.json()
                for breach in data:
                    breaches.append({
                        'source': 'Have I Been Pwned',
                        'breach_name': breach.get('Name'),
                        'date': breach.get('BreachDate'),
                        'title': breach.get('Title'),
                        'description': breach.get('Description'),
                        'compromised_count': breach.get('PwnCount'),
                        'data_classes': breach.get('DataClasses'),
                        'is_verified': breach.get('IsVerified'),
                        'is_sensitive': breach.get('IsSensitive'),
                        'url': f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                        'severity': 'CRITIQUE' if breach.get('IsSensitive') else 'ÉLEVÉE'
                    })
                logger.info(f"Fuites trouvées pour {email}: {len(breaches)}")
            elif resp.status_code == 404:
                breaches.append({
                    'source': 'Have I Been Pwned',
                    'status': 'clean',
                    'message': 'Email non trouvé dans les données compromises (bon signe!)',
                    'severity': 'SÛRE'
                })
        except Exception as e:
            logger.debug(f"HIBP erreur: {e}")
        
        return breaches
    
    def search_social_profiles(self, email: str) -> List[Dict[str, Any]]:
        """Chercher les profils sociaux associés à l'email"""
        profiles = []
        
        try:
            domain = email.split('@')[1]
            name_part = email.split('@')[0]
            
            # Plateformes à vérifier
            social_platforms = {
                'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={email}",
                'github': f"https://github.com/search?q={email}",
                'twitter': f"https://twitter.com/search?q={email}",
                'facebook': f"https://www.facebook.com/search/people/?q={email}",
                'instagram': f"https://www.instagram.com/search/users/?q={name_part}",
            }
            
            for platform, url in social_platforms.items():
                try:
                    resp = requests.head(url, headers=self.headers, timeout=5, allow_redirects=True)
                    if resp.status_code == 200:
                        profiles.append({
                            'platform': platform,
                            'search_url': url,
                            'accessible': True,
                            'type': 'social_media'
                        })
                except:
                    pass
            
            logger.info(f"Profils sociaux trouvés: {len(profiles)}")
        except Exception as e:
            logger.debug(f"Social search erreur: {e}")
        
        return profiles
    
    def verify_domain_registration(self, email: str) -> Dict[str, Any]:
        """Vérifier l'enregistrement du domaine"""
        results = {}
        
        try:
            domain = email.split('@')[1]
            
            # Vérification WHOIS via whois.com
            url = f"https://www.whois.com/whois/{domain}"
            resp = requests.get(url, headers=self.headers, timeout=10)
            
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Chercher les infos du domaine
                content = resp.text
                
                results['domain'] = domain
                results['registered'] = 'No matching query' not in content
                results['whois_url'] = url
                
                logger.info(f"Domaine {domain} vérif: {results['registered']}")
        except Exception as e:
            logger.debug(f"Domain verification erreur: {e}")
        
        return results