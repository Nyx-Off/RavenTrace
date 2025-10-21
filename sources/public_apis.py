#!/usr/bin/env python3
"""
public_apis.py - Intégrations avec APIs publiques
"""

import requests
import logging
from typing import Dict, List, Any
import os

logger = logging.getLogger(__name__)

class PublicAPIs:
    """Gestion des APIs publiques"""
    
    def __init__(self):
        self.timeout = 10
    
    def ipify_api(self, domain: str) -> Dict[str, Any]:
        """Obtenir l'IP d'un domaine via ipify API"""
        results = {}
        
        try:
            url = f"https://api.ipify.org?format=json&domain={domain}"
            resp = requests.get(url, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results['ip'] = data.get('ip')
        except Exception as e:
            logger.debug(f"ipify API error: {e}")
        
        return results
    
    def shodan_api(self, query: str, api_key: str = None) -> Dict[str, Any]:
        """Requête Shodan API (nécessite API key)"""
        results = {}
        api_key = api_key or os.getenv('SHODAN_API_KEY')
        
        if not api_key:
            logger.warning("Shodan API key not found")
            return results
        
        try:
            url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={query}"
            resp = requests.get(url, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results['matches'] = data.get('matches', [])
                results['total'] = data.get('total')
        except Exception as e:
            logger.debug(f"Shodan API error: {e}")
        
        return results
    
    def virustotal_api(self, domain: str, api_key: str = None) -> Dict[str, Any]:
        """Vérifier un domaine via VirusTotal API"""
        results = {}
        api_key = api_key or os.getenv('VIRUSTOTAL_API_KEY')
        
        if not api_key:
            logger.debug("VirusTotal API key not found")
            return results
        
        try:
            url = f"https://www.virustotal.com/api/v3/domains/{domain}"
            headers = {'x-apikey': api_key}
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results = {
                    'last_analysis_stats': data.get('data', {}).get('attributes', {}).get('last_analysis_stats'),
                    'last_dns_records': data.get('data', {}).get('attributes', {}).get('last_dns_records'),
                }
        except Exception as e:
            logger.debug(f"VirusTotal API error: {e}")
        
        return results
    
    def hunter_io_api(self, domain: str, api_key: str = None) -> Dict[str, Any]:
        """Chercher les emails d'un domaine via Hunter.io"""
        results = {}
        api_key = api_key or os.getenv('HUNTER_API_KEY')
        
        try:
            url = f"https://api.hunter.io/v2/domain-search?domain={domain}"
            
            if api_key:
                url += f"&domain_api_key={api_key}"
            
            resp = requests.get(url, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results = {
                    'emails': data.get('data', {}).get('emails', []),
                    'organization': data.get('data', {}).get('organization'),
                    'webmail': data.get('data', {}).get('webmail'),
                }
        except Exception as e:
            logger.debug(f"Hunter.io API error: {e}")
        
        return results
    
    def clearbit_api(self, email: str, api_key: str = None) -> Dict[str, Any]:
        """Obtenir les infos d'une personne via Clearbit API"""
        results = {}
        api_key = api_key or os.getenv('CLEARBIT_API_KEY')
        
        if not api_key:
            logger.debug("Clearbit API key not found")
            return results
        
        try:
            url = f"https://person.clearbit.com/v2/combined/find?email={email}"
            headers = {'Authorization': f'Bearer {api_key}'}
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results = {
                    'person': data.get('person'),
                    'company': data.get('company'),
                }
        except Exception as e:
            logger.debug(f"Clearbit API error: {e}")
        
        return results
    
    def abuseipdb_api(self, ip: str, api_key: str = None) -> Dict[str, Any]:
        """Vérifier une IP via AbuseIPDB"""
        results = {}
        api_key = api_key or os.getenv('ABUSEIPDB_API_KEY')
        
        if not api_key:
            logger.debug("AbuseIPDB API key not found")
            return results
        
        try:
            url = f"https://api.abuseipdb.com/api/v2/check"
            headers = {
                'Key': api_key,
                'Accept': 'application/json'
            }
            params = {
                'ipAddress': ip,
                'maxAgeInDays': 90
            }
            resp = requests.get(url, headers=headers, params=params, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results = data.get('data', {})
        except Exception as e:
            logger.debug(f"AbuseIPDB API error: {e}")
        
        return results
    
    def haveibeenpwned_api(self, email: str) -> Dict[str, Any]:
        """Vérifier si un email a été compromis"""
        results = {}
        
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
            headers = {'User-Agent': 'Raven-Trace/1.0'}
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                breaches = resp.json()
                results['breaches'] = breaches
                results['found'] = True
            elif resp.status_code == 404:
                results['found'] = False
        except Exception as e:
            logger.debug(f"HIBP API error: {e}")
        
        return results

# Instancia global
public_apis = PublicAPIs()