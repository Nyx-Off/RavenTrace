#!/usr/bin/env python3
"""
PhoneLookup - Recherche avancée par téléphone
Carriers, localisation, réputation
"""

import requests
import logging
import phonenumbers
from typing import Dict, List, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class PhoneLookup:
    """Moteur de recherche pour numéros de téléphone"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 10
    
    def get_carrier_info(self, phone: str, country: str = "FR") -> Dict[str, Any]:
        """Obtenir les infos de l'opérateur"""
        results = {}
        
        try:
            # Parser le numéro
            parsed = phonenumbers.parse(phone, country)
            
            # Infos basiques
            from phonenumbers import geocoder, carrier as carrier_module
            
            results['country'] = phonenumbers.region_code_for_number(parsed)
            results['carrier'] = carrier_module.name_for_number(parsed, "en")
            results['region'] = geocoder.description_for_number(parsed, "en")
            results['type'] = str(phonenumbers.number_type(parsed))
            results['valid'] = phonenumbers.is_valid_number(parsed)
            
            logger.debug(f"Carrier info récupéré pour {phone}")
        except Exception as e:
            logger.debug(f"Carrier lookup erreur: {e}")
        
        return results
    
    def get_location(self, phone: str, country: str = None) -> Dict[str, Any]:
        """Localiser le numéro de téléphone"""
        results = {}
        
        try:
            # Utiliser phonenumbers pour la géolocalisation
            if country:
                parsed = phonenumbers.parse(phone, country)
            else:
                parsed = phonenumbers.parse(phone)
            
            from phonenumbers import geocoder
            location = geocoder.description_for_number(parsed, "en")
            
            results['location'] = location
            results['country_code'] = phonenumbers.region_code_for_number(parsed)
            
        except Exception as e:
            logger.debug(f"Location lookup erreur: {e}")
        
        return results
    
    def check_reputation(self, phone: str) -> Dict[str, Any]:
        """Vérifier la réputation du numéro"""
        results = {}
        
        # 1. Vérifier via TrueCaller API (ou alternatives)
        try:
            # Scraper TrueCaller search (limited)
            url = f"https://www.truecaller.com/search/{phone.replace('+', '').replace(' ', '')}"
            resp = requests.get(url, headers=self.headers, timeout=5)
            
            if resp.status_code == 200:
                # Vérifier si le numéro est connu
                results['truecaller_found'] = "No results found" not in resp.text
                results['reputation_url'] = url
        except:
            pass
        
        # 2. Vérifier via ReverseLookup
        try:
            phone_clean = phone.replace('+', '').replace(' ', '')
            url = f"https://www.reversephone.com/search?phone={phone_clean}"
            resp = requests.get(url, headers=self.headers, timeout=5)
            
            if resp.status_code == 200 and len(resp.text) > 500:
                results['reverse_phone_found'] = True
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Extraire les résultats
                results['search_url'] = url
        except:
            pass
        
        return results
    
    def search_data_brokers(self, phone: str) -> List[Dict[str, Any]]:
        """Chercher sur les agrégateurs de données"""
        brokers = []
        
        try:
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            platforms = {
                'whitepages': f"https://www.whitepages.com/search/results?q={phone_clean}",
                'spokeo': f"https://www.spokeo.com/search?q={phone_clean}",
                'truecaller': f"https://www.truecaller.com/search/{phone_clean}",
            }
            
            for platform, url in platforms.items():
                try:
                    resp = requests.head(url, headers=self.headers, timeout=5)
                    if resp.status_code == 200:
                        brokers.append({
                            'platform': platform,
                            'url': url,
                            'reachable': True
                        })
                except:
                    pass
        except Exception as e:
            logger.debug(f"Data brokers erreur: {e}")
        
        return brokers
    
    def search_social(self, phone: str) -> List[Dict[str, str]]:
        """Chercher les comptes sociaux associés au téléphone"""
        profiles = []
        
        try:
            phone_clean = phone.replace('+', '').replace(' ', '').replace('-', '')
            
            # Créer des URLs de recherche sur les réseaux sociaux
            platforms = {
                'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={phone_clean}",
                'facebook': f"https://www.facebook.com/search/people/?q={phone_clean}",
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