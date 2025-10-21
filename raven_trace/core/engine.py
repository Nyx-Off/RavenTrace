#!/usr/bin/env python3
"""
SearchEngine - Moteur central de recherche OSINT
Agrège les données de multiples sources
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
import logging

from raven_trace.modules.email_lookup import EmailLookup
from raven_trace.modules.phone_lookup import PhoneLookup
from raven_trace.modules.username_lookup import UsernameLookup
from raven_trace.modules.breaches import BreachChecker
from raven_trace.core.validators import validate_email, validate_phone, validate_username
from raven_trace.storage.database import CacheDB

logger = logging.getLogger(__name__)

class SearchEngine:
    def __init__(self):
        self.email_lookup = EmailLookup()
        self.phone_lookup = PhoneLookup()
        self.username_lookup = UsernameLookup()
        self.breach_checker = BreachChecker()
        self.cache = CacheDB()
        self.executor = ThreadPoolExecutor(max_workers=5)
    
    def search_email(self, email: str, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche agrégée par email"""
        if not validate_email(email):
            logger.error(f"Email invalide: {email}")
            return {"error": "Email invalide"}
        
        # Vérifier le cache
        cached = self.cache.get_email(email)
        if cached and not deep_scan:
            logger.info(f"Résultat du cache pour {email}")
            return cached
        
        results = {
            "email": email,
            "sources": {},
            "breaches": [],
            "confidence": 0
        }
        
        try:
            # Recherche parallèle sur multiples sources
            results["sources"]["email_reputation"] = self.email_lookup.check_reputation(email)
            results["sources"]["dns_records"] = self.email_lookup.check_dns(email)
            results["sources"]["data_aggregators"] = self.email_lookup.search_data_brokers(email)
            results["breaches"] = self.breach_checker.check_breaches(email)
            results["sources"]["social_profiles"] = self.email_lookup.search_social(email)
            
            # Calculer la confiance
            results["confidence"] = self._calculate_confidence(results)
            
            # Mettre en cache
            self.cache.save_email(email, results)
            
        except Exception as e:
            logger.error(f"Erreur recherche email: {e}")
            results["error"] = str(e)
        
        return results
    
    def search_phone(self, phone: str, country: str = None, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche agrégée par téléphone"""
        if not validate_phone(phone, country):
            logger.error(f"Téléphone invalide: {phone}")
            return {"error": "Téléphone invalide"}
        
        cached = self.cache.get_phone(phone)
        if cached and not deep_scan:
            return cached
        
        results = {
            "phone": phone,
            "country": country,
            "sources": {},
            "confidence": 0
        }
        
        try:
            results["sources"]["carrier_info"] = self.phone_lookup.get_carrier_info(phone)
            results["sources"]["location"] = self.phone_lookup.get_location(phone, country)
            results["sources"]["reputation"] = self.phone_lookup.check_reputation(phone)
            results["sources"]["data_aggregators"] = self.phone_lookup.search_data_brokers(phone)
            results["sources"]["social_profiles"] = self.phone_lookup.search_social(phone)
            
            results["confidence"] = self._calculate_confidence(results)
            self.cache.save_phone(phone, results)
            
        except Exception as e:
            logger.error(f"Erreur recherche phone: {e}")
            results["error"] = str(e)
        
        return results
    
    def search_username(self, username: str, deep_scan: bool = False) -> Dict[str, Any]:
        """Recherche agrégée par pseudo"""
        if not validate_username(username):
            logger.error(f"Username invalide: {username}")
            return {"error": "Username invalide"}
        
        cached = self.cache.get_username(username)
        if cached and not deep_scan:
            return cached
        
        results = {
            "username": username,
            "sources": {},
            "confidence": 0
        }
        
        try:
            results["sources"]["social_media"] = self.username_lookup.search_all_platforms(username)
            results["sources"]["forums"] = self.username_lookup.search_forums(username)
            results["sources"]["code_repos"] = self.username_lookup.search_github_gitlab(username)
            results["sources"]["gaming"] = self.username_lookup.search_gaming_platforms(username)
            results["sources"]["aggregators"] = self.username_lookup.search_aggregators(username)
            
            results["confidence"] = self._calculate_confidence(results)
            self.cache.save_username(username, results)
            
        except Exception as e:
            logger.error(f"Erreur recherche username: {e}")
            results["error"] = str(e)
        
        return results
    
    def _calculate_confidence(self, results: Dict) -> float:
        """Calcule le score de confiance des résultats"""
        total_sources = 0
        found_sources = 0
        
        for source_type, data in results.get("sources", {}).items():
            if isinstance(data, list):
                total_sources += 1
                if data and len(data) > 0:
                    found_sources += 1
            elif isinstance(data, dict):
                total_sources += 1
                if data and len(data) > 0:
                    found_sources += 1
        
        if total_sources == 0:
            return 0.0
        
        return round((found_sources / total_sources) * 100, 2)