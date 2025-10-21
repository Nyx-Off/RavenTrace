#!/usr/bin/env python3
"""
SearchEngine - Moteur central de recherche OSINT amélioré
Résultats réels des APIs publiques
"""

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import logging

from raven_trace.modules.email_lookup import EmailLookup
from raven_trace.modules.username_lookup import UsernameLookup
from raven_trace.core.validators import validate_email, validate_username
from raven_trace.storage.database import CacheDB

logger = logging.getLogger(__name__)

class SearchEngine:
    """Moteur de recherche OSINT avec résultats concrets"""
    
    def __init__(self):
        self.email_lookup = EmailLookup()
        self.username_lookup = UsernameLookup()
        self.cache = CacheDB()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def search_email(self, email: str, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche complète par email"""
        if not validate_email(email):
            logger.error(f"Email invalide: {email}")
            return {"error": "Email invalide", "email": email}
        
        # Vérifier cache
        cached = self.cache.get_email(email)
        if cached and not deep_scan:
            logger.info(f"Résultat du cache pour {email}")
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
            "timestamp": None
        }
        
        try:
            # Recherche parallèle
            logger.info(f"Démarrage recherche email: {email}")
            
            # 1. Réputation
            logger.debug("Vérification réputation...")
            results["reputation"] = self.email_lookup.check_reputation(email)
            
            # 2. DNS Records
            logger.debug("Vérification DNS...")
            results["dns"] = self.email_lookup.check_dns(email)
            
            # 3. Fuites de données
            logger.debug("Vérification fuites...")
            results["breaches"] = self.email_lookup.check_breaches(email)
            
            # 4. Vérification domaine
            logger.debug("Vérification domaine...")
            results["domain"] = self.email_lookup.verify_domain_registration(email)
            
            # 5. Profils sociaux
            logger.debug("Recherche profils sociaux...")
            results["social_profiles"] = self.email_lookup.search_social_profiles(email)
            
            # Agrégation des résultats
            results["sources"] = {
                "reputation": results["reputation"],
                "dns_records": results["dns"],
                "breaches": results["breaches"],
                "social_profiles": results["social_profiles"],
                "domain_info": results["domain"]
            }
            
            # Calculer confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Mettre en cache
            from datetime import datetime
            results["timestamp"] = datetime.now().isoformat()
            self.cache.save_email(email, results)
            
            logger.info(f"Recherche email terminée: {email} - Confiance: {results['confidence']}%")
            
        except Exception as e:
            logger.error(f"Erreur recherche email: {e}")
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
            return cached
        
        results = {
            "username": username,
            "sources": {},
            "social_media": [],
            "code_repositories": [],
            "forums": [],
            "confidence": 0,
            "profiles_found": 0,
            "timestamp": None
        }
        
        try:
            logger.info(f"Démarrage recherche username: {username}")
            
            # 1. Réseaux sociaux
            logger.debug("Recherche réseaux sociaux...")
            social_results = self.username_lookup.search_all_platforms(username)
            results["social_media"] = social_results
            
            # 2. Dépôts de code
            logger.debug("Recherche dépôts code...")
            github_result = self.username_lookup.search_github_advanced(username)
            if github_result.get('found'):
                results["code_repositories"].append(github_result)
                logger.info(f"Profil GitHub trouvé: {github_result.get('followers')} followers")
            
            # 3. Forums
            logger.debug("Recherche forums...")
            forum_results = self.username_lookup.search_forums(username)
            results["forums"] = forum_results
            
            # 4. Reddit
            logger.debug("Recherche Reddit...")
            reddit_result = self.username_lookup.search_reddit_advanced(username)
            if reddit_result.get('found'):
                results["code_repositories"].append(reddit_result)
                logger.info(f"Profil Reddit trouvé: {reddit_result.get('link_karma')} karma")
            
            # Compter les profils trouvés
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
            
            # Calculer confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Mettre en cache
            from datetime import datetime
            results["timestamp"] = datetime.now().isoformat()
            self.cache.save_username(username, results)
            
            logger.info(f"Recherche username terminée: {username} - {found_count} profils trouvés")
            
        except Exception as e:
            logger.error(f"Erreur recherche username: {e}")
            results["error"] = str(e)
        
        return results
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calcule le score de confiance des résultats"""
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