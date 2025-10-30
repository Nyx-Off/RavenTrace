#!/usr/bin/env python3
"""
EmailLookup - Recherche avancée par email avec résultats réels
APIs publiques, scraping et intégration Kali tools
"""

import requests
import logging
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import time
import json
import dns.resolver
import hashlib
from config import get_config

logger = logging.getLogger(__name__)

class EmailLookup:
    """Moteur de recherche pour emails avec résultats réels"""
    
    def __init__(self):
        self.config = get_config()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.timeout = 15
    
    def check_reputation(self, email: str) -> Dict[str, Any]:
        """Vérifier la réputation de l'email via multiples sources"""
        results = {}
        
        # 1. EmailRep.io (API gratuite)
        try:
            url = f"https://emailrep.io/{email}"
            resp = self.session.get(url, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results['emailrep'] = {
                    'reputation': data.get('reputation', 'unknown'),
                    'suspicious': data.get('suspicious', False),
                    'references': data.get('references', 0),
                    'details': {
                        'blacklisted': data.get('details', {}).get('blacklisted', False),
                        'malicious_activity': data.get('details', {}).get('malicious_activity', False),
                        'credentials_leaked': data.get('details', {}).get('credentials_leaked', False),
                        'spam': data.get('details', {}).get('spam', False),
                        'domain_exists': data.get('details', {}).get('domain_exists', False),
                        'domain_reputation': data.get('details', {}).get('domain_reputation', 'unknown'),
                        'new_domain': data.get('details', {}).get('new_domain', False),
                        'days_since_domain_creation': data.get('details', {}).get('days_since_domain_creation', 0),
                        'suspicious_tld': data.get('details', {}).get('suspicious_tld', False),
                        'data_breach': data.get('details', {}).get('data_breach', False)
                    },
                    'profiles': data.get('profiles', [])
                }
                logger.info(f"EmailRep: Réputation {data.get('reputation')} pour {email}")
        except Exception as e:
            logger.debug(f"EmailRep erreur: {e}")
        
        # 2. Vérifier via Hunter.io (si clé API disponible)
        hunter_key = self.config.get_api_key('hunter')
        if hunter_key:
            try:
                domain = email.split('@')[1]
                url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={hunter_key}"
                resp = self.session.get(url, timeout=self.timeout)
                
                if resp.status_code == 200:
                    data = resp.json()
                    results['hunter'] = {
                        'status': data.get('data', {}).get('status'),
                        'score': data.get('data', {}).get('score'),
                        'result': data.get('data', {}).get('result'),
                        'regexp': data.get('data', {}).get('regexp'),
                        'gibberish': data.get('data', {}).get('gibberish'),
                        'disposable': data.get('data', {}).get('disposable'),
                        'webmail': data.get('data', {}).get('webmail'),
                        'mx_records': data.get('data', {}).get('mx_records'),
                        'smtp_server': data.get('data', {}).get('smtp_server'),
                        'smtp_check': data.get('data', {}).get('smtp_check'),
                        'accept_all': data.get('data', {}).get('accept_all'),
                        'sources': data.get('data', {}).get('sources', [])
                    }
                    logger.info(f"Hunter.io: Score {data.get('data', {}).get('score')} pour {email}")
            except Exception as e:
                logger.debug(f"Hunter.io erreur: {e}")
        
        return results
    
    def check_dns(self, email: str) -> Dict[str, Any]:
        """Vérifier les enregistrements DNS du domaine"""
        results = {}
        
        try:
            domain = email.split('@')[1]
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            resolver.lifetime = 5
            
            # MX Records
            mx_records = []
            try:
                mx_answers = resolver.resolve(domain, 'MX')
                for mx in mx_answers:
                    mx_records.append({
                        'exchange': str(mx.exchange).rstrip('.'),
                        'priority': mx.preference
                    })
                mx_records.sort(key=lambda x: x['priority'])
            except Exception as e:
                logger.debug(f"MX lookup error: {e}")
            
            # SPF Records
            spf_records = []
            try:
                txt_answers = resolver.resolve(domain, 'TXT')
                for txt in txt_answers:
                    txt_str = str(txt).strip('"')
                    if 'v=spf1' in txt_str:
                        spf_records.append(txt_str)
            except Exception as e:
                logger.debug(f"SPF lookup error: {e}")
            
            # DMARC Records
            dmarc_records = []
            try:
                dmarc_answers = resolver.resolve(f"_dmarc.{domain}", 'TXT')
                for txt in dmarc_answers:
                    dmarc_records.append(str(txt).strip('"'))
            except Exception as e:
                logger.debug(f"DMARC lookup error: {e}")
            
            # A Records
            a_records = []
            try:
                a_answers = resolver.resolve(domain, 'A')
                for a in a_answers:
                    a_records.append(str(a))
            except Exception as e:
                logger.debug(f"A record lookup error: {e}")
            
            # AAAA Records (IPv6)
            aaaa_records = []
            try:
                aaaa_answers = resolver.resolve(domain, 'AAAA')
                for aaaa in aaaa_answers:
                    aaaa_records.append(str(aaaa))
            except Exception as e:
                logger.debug(f"AAAA record lookup error: {e}")
            
            # NS Records
            ns_records = []
            try:
                ns_answers = resolver.resolve(domain, 'NS')
                for ns in ns_answers:
                    ns_records.append(str(ns).rstrip('.'))
            except Exception as e:
                logger.debug(f"NS record lookup error: {e}")
            
            results['dns'] = {
                'domain': domain,
                'mx_records': mx_records,
                'spf_configured': len(spf_records) > 0,
                'spf_records': spf_records,
                'dmarc_configured': len(dmarc_records) > 0,
                'dmarc_records': dmarc_records,
                'a_records': a_records,
                'aaaa_records': aaaa_records,
                'ns_records': ns_records,
                'valid_domain': len(mx_records) > 0,
                'mail_servers': [mx['exchange'] for mx in mx_records]
            }
            
            logger.info(f"DNS: {len(mx_records)} MX, SPF={len(spf_records)>0}, DMARC={len(dmarc_records)>0} pour {domain}")
            
        except Exception as e:
            logger.error(f"DNS erreur: {e}")
            results['dns'] = {'error': str(e)}
        
        return results
    
    def check_breaches(self, email: str) -> List[Dict[str, Any]]:
        """Vérifier les fuites de données via multiples sources"""
        breaches = []
        
        # 1. Have I Been Pwned
        hibp_key = self.config.get_api_key('hibp')
        try:
            url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}?truncateResponse=false"
            headers = {**self.headers}
            
            if hibp_key:
                headers['hibp-api-key'] = hibp_key
            
            headers['User-Agent'] = 'RavenTrace-OSINT/1.0'
            
            resp = requests.get(url, headers=headers, timeout=self.timeout)
            time.sleep(1.6)  # Rate limiting HIBP
            
            if resp.status_code == 200:
                data = resp.json()
                for breach in data:
                    breaches.append({
                        'source': 'Have I Been Pwned',
                        'breach_name': breach.get('Name'),
                        'title': breach.get('Title'),
                        'domain': breach.get('Domain'),
                        'date': breach.get('BreachDate'),
                        'added_date': breach.get('AddedDate'),
                        'modified_date': breach.get('ModifiedDate'),
                        'compromised_count': breach.get('PwnCount'),
                        'description': breach.get('Description'),
                        'data_classes': breach.get('DataClasses', []),
                        'is_verified': breach.get('IsVerified'),
                        'is_fabricated': breach.get('IsFabricated'),
                        'is_sensitive': breach.get('IsSensitive'),
                        'is_retired': breach.get('IsRetired'),
                        'is_spam_list': breach.get('IsSpamList'),
                        'logo_path': breach.get('LogoPath'),
                        'severity': 'CRITICAL' if breach.get('IsSensitive') else 'HIGH'
                    })
                logger.info(f"HIBP: {len(breaches)} fuites trouvées pour {email}")
            elif resp.status_code == 404:
                breaches.append({
                    'source': 'Have I Been Pwned',
                    'status': 'clean',
                    'message': 'Aucune fuite détectée dans HIBP',
                    'severity': 'SAFE'
                })
        except Exception as e:
            logger.debug(f"HIBP erreur: {e}")
        
        # 2. DeHashed (si API key disponible)
        dehashed_key = self.config.get_api_key('dehashed')
        if dehashed_key:
            try:
                # DeHashed API implementation
                pass
            except Exception as e:
                logger.debug(f"DeHashed erreur: {e}")
        
        # 3. LeakCheck via web scraping (respectueux)
        try:
            url = f"https://leakcheck.net/api/public?check={email}"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('found') and data.get('sources'):
                    for source in data.get('sources', []):
                        breaches.append({
                            'source': 'LeakCheck',
                            'breach_name': source,
                            'found': True,
                            'severity': 'HIGH'
                        })
        except Exception as e:
            logger.debug(f"LeakCheck erreur: {e}")
        
        return breaches
    
    def search_social_profiles(self, email: str) -> List[Dict[str, Any]]:
        """Chercher les profils sociaux associés à l'email"""
        profiles = []
        domain = email.split('@')[1]
        username = email.split('@')[0]
        
        # Intégration avec holehe si disponible
        try:
            from modules.kali_tools import kali_tools
            if kali_tools.tools_available.get('holehe'):
                holehe_results = kali_tools.holehe_check(email)
                profiles.extend(holehe_results)
        except ImportError:
            pass
        
        # Recherche manuelle sur les plateformes
        platforms = {
            'gravatar': self._check_gravatar(email),
            'github': self._check_github_email(email),
            'keybase': self._check_keybase(email),
            'linkedin': f"https://www.linkedin.com/search/results/people/?keywords={email}",
            'facebook': f"https://www.facebook.com/search/people/?q={email}",
            'twitter': f"https://twitter.com/search?q={email}"
        }
        
        for platform, result in platforms.items():
            if isinstance(result, dict):
                profiles.append(result)
            elif isinstance(result, str):
                profiles.append({
                    'platform': platform,
                    'search_url': result,
                    'type': 'search_link'
                })
        
        logger.info(f"Profils sociaux: {len(profiles)} trouvés pour {email}")
        return profiles
    
    def _check_gravatar(self, email: str) -> Dict[str, Any]:
        """Vérifier si un Gravatar existe"""
        email_hash = hashlib.md5(email.lower().encode()).hexdigest()
        url = f"https://www.gravatar.com/avatar/{email_hash}?d=404"
        
        try:
            resp = requests.head(url, timeout=5)
            if resp.status_code == 200:
                return {
                    'platform': 'gravatar',
                    'found': True,
                    'profile_url': f"https://gravatar.com/{email_hash}",
                    'avatar_url': url.replace('?d=404', '?s=200')
                }
        except:
            pass
        
        return {'platform': 'gravatar', 'found': False}
    
    def _check_github_email(self, email: str) -> Dict[str, Any]:
        """Chercher sur GitHub par email"""
        try:
            # GitHub API pour recherche par email
            url = f"https://api.github.com/search/users?q={email}+in:email"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('total_count', 0) > 0:
                    users = data.get('items', [])
                    return {
                        'platform': 'github',
                        'found': True,
                        'users': [
                            {
                                'username': u.get('login'),
                                'profile_url': u.get('html_url'),
                                'avatar_url': u.get('avatar_url')
                            } for u in users[:5]
                        ]
                    }
        except Exception as e:
            logger.debug(f"GitHub email search error: {e}")
        
        return {'platform': 'github', 'found': False}
    
    def _check_keybase(self, email: str) -> Dict[str, Any]:
        """Vérifier sur Keybase"""
        try:
            url = f"https://keybase.io/_/api/1.0/user/lookup.json?email={email}"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get('them'):
                    user = data['them'][0] if isinstance(data['them'], list) else data['them']
                    return {
                        'platform': 'keybase',
                        'found': True,
                        'username': user.get('basics', {}).get('username'),
                        'profile_url': f"https://keybase.io/{user.get('basics', {}).get('username')}"
                    }
        except Exception as e:
            logger.debug(f"Keybase error: {e}")
        
        return {'platform': 'keybase', 'found': False}
    
    def verify_domain_registration(self, email: str) -> Dict[str, Any]:
        """Vérifier l'enregistrement du domaine via WHOIS"""
        results = {}
        
        try:
            import whois
            domain = email.split('@')[1]
            
            # WHOIS lookup
            w = whois.whois(domain)
            
            results = {
                'domain': domain,
                'registered': True if w.domain_name else False,
                'registrar': w.registrar if hasattr(w, 'registrar') else None,
                'creation_date': str(w.creation_date) if hasattr(w, 'creation_date') else None,
                'expiration_date': str(w.expiration_date) if hasattr(w, 'expiration_date') else None,
                'updated_date': str(w.updated_date) if hasattr(w, 'updated_date') else None,
                'status': w.status if hasattr(w, 'status') else None,
                'name_servers': w.name_servers if hasattr(w, 'name_servers') else [],
                'org': w.org if hasattr(w, 'org') else None,
                'emails': w.emails if hasattr(w, 'emails') else [],
                'country': w.country if hasattr(w, 'country') else None
            }
            
            logger.info(f"WHOIS: Domaine {domain} - Registrar: {results.get('registrar')}")
            
        except ImportError:
            logger.warning("Module python-whois non installé")
            # Fallback vers une API web
            try:
                domain = email.split('@')[1]
                url = f"https://www.whoisxmlapi.com/whoisserver/WhoisService?apiKey={self.config.get_api_key('whois')}&domainName={domain}&outputFormat=JSON"
                
                if self.config.get_api_key('whois'):
                    resp = self.session.get(url, timeout=10)
                    if resp.status_code == 200:
                        data = resp.json()
                        results = {
                            'domain': domain,
                            'registered': True,
                            'registrar': data.get('WhoisRecord', {}).get('registrarName'),
                            'creation_date': data.get('WhoisRecord', {}).get('createdDate'),
                            'expiration_date': data.get('WhoisRecord', {}).get('expiresDate')
                        }
            except Exception as e:
                logger.debug(f"WHOIS API error: {e}")
        except Exception as e:
            logger.debug(f"WHOIS error: {e}")
        
        return results
    
    def check_pastebin_leaks(self, email: str) -> List[Dict[str, Any]]:
        """Chercher des leaks sur Pastebin et similaires"""
        leaks = []
        
        try:
            # Psbdmp (Pastebin dump search)
            url = f"https://psbdmp.ws/api/v3/search/{email}"
            resp = self.session.get(url, timeout=10)
            
            if resp.status_code == 200:
                data = resp.json()
                for paste in data.get('data', []):
                    leaks.append({
                        'source': 'Pastebin',
                        'id': paste.get('id'),
                        'date': paste.get('time'),
                        'text_preview': paste.get('text', '')[:200],
                        'url': f"https://pastebin.com/{paste.get('id')}"
                    })
        except Exception as e:
            logger.debug(f"Pastebin search error: {e}")
        
        return leaks