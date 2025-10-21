#!/usr/bin/env python3
"""
SearchEngine - Moteur central de recherche OSINT amélioré
Résultats réels des APIs publiques et recherches parallélisées
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Any
import logging
from datetime import datetime

from raven_trace.modules.email_lookup import EmailLookup
from raven_trace.modules.phone_lookup import PhoneLookup
from raven_trace.modules.username_lookup import UsernameLookup
from raven_trace.core.validators import validate_email, validate_phone, validate_username
from raven_trace.storage.database import CacheDB

logger = logging.getLogger(__name__)

class SearchEngine:
    """Moteur de recherche OSINT avec résultats concrets"""
    
    def __init__(self, max_workers: int = 5):
        self.email_lookup = EmailLookup()
        self.phone_lookup = PhoneLookup()
        self.username_lookup = UsernameLookup()
        self.cache = CacheDB()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.max_workers = max_workers
    
    def search_email(self, email: str, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche complète par email avec cache"""
        if not validate_email(email):
            logger.error(f"Email invalide: {email}")
            return {"error": "Email invalide", "email": email}
        
        # Vérifier cache
        cached = self.cache.get_email(email)
        if cached and not deep_scan:
            logger.info(f"Résultat du cache pour {email}")
            cached['from_cache'] = True
            return cached
        
        results = {
            "email": email,
            "sources": {},
            "breaches": [],
            "reputation": {},
            "dns": {},
            "domain": {},
            "social_profiles": [],
            "confidence": 0,
            "search_time": None,
            "timestamp": None,
            "from_cache": False
        }
        
        try:
            logger.info(f"Démarrage recherche email: {email}")
            start_time = datetime.now()
            
            # Recherche parallélisée
            futures = {
                self.executor.submit(self.email_lookup.check_reputation, email): 'reputation',
                self.executor.submit(self.email_lookup.check_dns, email): 'dns',
                self.executor.submit(self.email_lookup.check_breaches, email): 'breaches',
                self.executor.submit(self.email_lookup.verify_domain_registration, email): 'domain',
                self.executor.submit(self.email_lookup.search_social_profiles, email): 'social_profiles',
            }
            
            for future in as_completed(futures):
                key = futures[future]
                try:
                    result = future.result()
                    results[key] = result
                    logger.debug(f"Résultat {key}: OK")
                except Exception as e:
                    logger.error(f"Erreur {key}: {e}")
                    results[key] = {}
            
            # Agrégation
            results["sources"] = {
                "reputation": results["reputation"],
                "dns_records": results["dns"],
                "breaches": results["breaches"],
                "social_profiles": results["social_profiles"],
                "domain_info": results["domain"]
            }
            
            # Confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Timing
            end_time = datetime.now()
            results["search_time"] = (end_time - start_time).total_seconds()
            results["timestamp"] = end_time.isoformat()
            
            # Cache
            self.cache.save_email(email, results)
            
            logger.info(f"Email search terminée: {email} - Confiance: {results['confidence']}%")
            
        except Exception as e:
            logger.error(f"Erreur recherche email: {e}")
            results["error"] = str(e)
        
        return results
    
    def search_phone(self, phone: str, country: str = "FR", deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche complète par téléphone"""
        if not validate_phone(phone, country):
            logger.error(f"Téléphone invalide: {phone}")
            return {"error": "Téléphone invalide", "phone": phone}
        
        # Vérifier cache
        cached = self.cache.get_phone(phone)
        if cached and not deep_scan:
            logger.info(f"Résultat du cache pour {phone}")
            cached['from_cache'] = True
            return cached
        
        results = {
            "phone": phone,
            "country": country,
            "carrier_info": {},
            "location": {},
            "reputation": {},
            "data_brokers": [],
            "social_profiles": [],
            "spam_reports": {},
            "voip_info": {},
            "timezone": [],
            "confidence": 0,
            "timestamp": None,
            "from_cache": False
        }
        
        try:
            logger.info(f"Démarrage recherche phone: {phone}")
            start_time = datetime.now()
            
            # Recherche parallélisée
            futures = {
                self.executor.submit(self.phone_lookup.get_carrier_info, phone, country): 'carrier_info',
                self.executor.submit(self.phone_lookup.get_location, phone, country): 'location',
                self.executor.submit(self.phone_lookup.check_reputation, phone): 'reputation',
                self.executor.submit(self.phone_lookup.search_data_brokers, phone): 'data_brokers',
                self.executor.submit(self.phone_lookup.search_social, phone): 'social_profiles',
                self.executor.submit(self.phone_lookup.check_spam_reports, phone): 'spam_reports',
                self.executor.submit(self.phone_lookup.get_voip_provider, phone, country): 'voip_info',
            }
            
            for future in as_completed(futures):
                key = futures[future]
                try:
                    result = future.result()
                    results[key] = result
                    logger.debug(f"Résultat {key}: OK")
                except Exception as e:
                    logger.error(f"Erreur {key}: {e}")
            
            # Timezone
            try:
                results['timezone'] = self.phone_lookup.get_timezone(phone, country)
            except Exception as e:
                logger.debug(f"Timezone erreur: {e}")
            
            # Confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Timestamp
            results["timestamp"] = datetime.now().isoformat()
            
            # Cache
            self.cache.save_phone(phone, results)
            
            logger.info(f"Phone search terminée: {phone}")
            
        except Exception as e:
            logger.error(f"Erreur recherche phone: {e}")
            results["error"] = str(e)
        
        return results
    
    def search_username(self, username: str, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche complète par pseudo"""
        if not validate_username(username):
            logger.error(f"Username invalide: {username}")
            return {"error": "Username invalide", "username": username}
        
        # Vérifier cache
        cached = self.cache.get_username(username)
        if cached and not deep_scan:
            logger.info(f"Résultat du cache pour {username}")
            cached['from_cache'] = True
            return cached
        
        results = {
            "username": username,
            "sources": {},
            "social_media": [],
            "code_repositories": [],
            "forums": [],
            "confidence": 0,
            "profiles_found": 0,
            "timestamp": None,
            "from_cache": False
        }
        
        try:
            logger.info(f"Démarrage recherche username: {username}")
            start_time = datetime.now()
            
            # 1. Réseaux sociaux
            logger.debug("Recherche réseaux sociaux...")
            social_results = self.username_lookup.search_all_platforms(username)
            results["social_media"] = social_results
            
            # 2. GitHub
            logger.debug("Recherche GitHub...")
            github_result = self.username_lookup.search_github_advanced(username)
            if github_result.get('found'):
                results["code_repositories"].append(github_result)
                logger.info(f"GitHub trouvé: {github_result.get('followers')} followers")
            
            # 3. Reddit
            logger.debug("Recherche Reddit...")
            reddit_result = self.username_lookup.search_reddit_advanced(username)
            if reddit_result.get('found'):
                results["code_repositories"].append(reddit_result)
                logger.info(f"Reddit trouvé: {reddit_result.get('link_karma')} karma")
            
            # 4. Twitter
            logger.debug("Recherche Twitter...")
            twitter_result = self.username_lookup.search_twitter_advanced(username)
            if twitter_result.get('found'):
                results["social_media"].append(twitter_result)
            
            # 5. Forums
            logger.debug("Recherche forums...")
            forum_results = self.username_lookup.search_forums(username)
            results["forums"] = forum_results
            
            # Compter profils
            found_count = sum(1 for p in social_results if p.get('found'))
            found_count += sum(1 for p in forum_results if p.get('found'))
            if github_result.get('found'):
                found_count += 1
            if reddit_result.get('found'):
                found_count += 1
            
            results["profiles_found"] = found_count
            
            # Agrégation
            results["sources"] = {
                "social_media": [p for p in social_results if p.get('found')],
                "code_repositories": [p for p in results["code_repositories"] if p.get('found')],
                "forums": [p for p in forum_results if p.get('found')],
            }
            
            # Confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Timestamp
            end_time = datetime.now()
            results["search_time"] = (end_time - start_time).total_seconds()
            results["timestamp"] = end_time.isoformat()
            
            # Cache
            self.cache.save_username(username, results)
            
            logger.info(f"Username search terminée: {username} - {found_count} profils")
            
        except Exception as e:
            logger.error(f"Erreur recherche username: {e}")
            results["error"] = str(e)
        
        return results
    
    def search_combined(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Recherche combinée intelligente"""
        results = {
            'emails': [],
            'phones': [],
            'usernames': [],
            'query': query
        }
        
        try:
            logger.info(f"Recherche combinée: {query}")
            
            # Essayer chaque type
            if validate_email(query):
                results['emails'] = [self.search_email(query)]
            elif validate_phone(query):
                results['phones'] = [self.search_phone(query)]
            elif validate_username(query):
                results['usernames'] = [self.search_username(query)]
            
        except Exception as e:
            logger.error(f"Erreur recherche combinée: {e}")
        
        return results
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calcule le score de confiance"""
        if "sources" not in results:
            return 0.0
        
        total_sources = 0
        found_sources = 0
        
        for source_type, data in results.get("sources", {}).items():
            if isinstance(data, list):
                if len(data) > 0:
                    total_sources += 1
                    found_sources += 1
                else:
                    total_sources += 1
            elif isinstance(data, dict):
                if len(data) > 0 and data.get('found') is not False:
                    total_sources += 1
                    found_sources += 1
                else:
                    total_sources += 1
        
        if total_sources == 0:
            return 0.0
        
        return round((found_sources / total_sources) * 100, 1)
    
    def export_results(self, results: Dict[str, Any], format_type: str = 'json', filepath: str = None) -> None:
        """Exporter les résultats"""
        from raven_trace.utils.formatter import export_json, export_csv, export_html
        
        if filepath is None:
            from pathlib import Path
            export_dir = Path.home() / '.raven_trace' / 'exports'
            export_dir.mkdir(parents=True, exist_ok=True)
            
            query = results.get('email') or results.get('username') or results.get('phone', 'search')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = export_dir / f"{query}_{timestamp}.{format_type}"
        
        if format_type == 'json':
            export_json(results, str(filepath))
        elif format_type == 'csv':
            export_csv(results, str(filepath))
        elif format_type == 'html':
            export_html(results, str(filepath))
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Obtenir les stats du cache"""
        return {
            'cache_dir': str(self.cache.db_path),
            'cache_enabled': True,
            'ttl_hours': 24
        }
    
    def clear_cache(self, days: int = 7) -> None:
        """Nettoyer le cache"""
        self.cache.clear_old_cache(days)
        logger.info(f"Cache nettoyé (> {days} jours)")