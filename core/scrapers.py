#!/usr/bin/env python3
"""
scrapers.py - Scrapers personnalisés pour sources spéciales
"""

import requests
import logging
from typing import Dict, List, Any
from bs4 import BeautifulSoup
from utils.helpers import get_random_user_agent

logger = logging.getLogger(__name__)

class BaseScraper:
    """Classe de base pour les scrapers"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': get_random_user_agent()
        }
        self.timeout = 10
    
    def fetch(self, url: str, **kwargs) -> requests.Response:
        """Récupérer une URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=self.timeout, **kwargs)
            return response
        except requests.Timeout:
            logger.warning(f"Timeout: {url}")
            return None
        except Exception as e:
            logger.error(f"Fetch error: {e}")
            return None
    
    def parse_html(self, html: str):
        """Parser HTML"""
        return BeautifulSoup(html, 'html.parser')


class LinkedInScraper(BaseScraper):
    """Scraper pour LinkedIn"""
    
    def search_email(self, email: str) -> Dict[str, Any]:
        """Rechercher un email sur LinkedIn"""
        results = {}
        
        try:
            url = f"https://www.linkedin.com/search/results/people/?keywords={email}"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                soup = self.parse_html(resp.text)
                results['found'] = True
                results['url'] = url
                # Extraire les résultats si possible
        except Exception as e:
            logger.debug(f"LinkedIn search error: {e}")
        
        return results


class GitHubScraper(BaseScraper):
    """Scraper pour GitHub"""
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Obtenir les infos d'un utilisateur GitHub"""
        results = {}
        
        try:
            url = f"https://api.github.com/users/{username}"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                results = {
                    'username': data.get('login'),
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'company': data.get('company'),
                    'location': data.get('location'),
                    'email': data.get('email'),
                    'blog': data.get('blog'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'public_repos': data.get('public_repos'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                    'url': data.get('html_url'),
                }
        except Exception as e:
            logger.debug(f"GitHub user info error: {e}")
        
        return results
    
    def search_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Chercher les repos d'un utilisateur"""
        repos = []
        
        try:
            url = f"https://api.github.com/users/{username}/repos?per_page=100"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                for repo in data:
                    repos.append({
                        'name': repo.get('name'),
                        'url': repo.get('html_url'),
                        'description': repo.get('description'),
                        'stars': repo.get('stargazers_count'),
                        'language': repo.get('language'),
                    })
        except Exception as e:
            logger.debug(f"GitHub repos search error: {e}")
        
        return repos


class TwitterScraper(BaseScraper):
    """Scraper pour Twitter"""
    
    def check_username(self, username: str) -> Dict[str, Any]:
        """Vérifier si un username existe sur Twitter"""
        results = {}
        
        try:
            url = f"https://twitter.com/{username}"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                results['found'] = True
                results['url'] = url
                # Parser le HTML pour extraire les infos
        except Exception as e:
            logger.debug(f"Twitter check error: {e}")
        
        return results


class RedditScraper(BaseScraper):
    """Scraper pour Reddit"""
    
    def get_user_info(self, username: str) -> Dict[str, Any]:
        """Obtenir les infos d'un utilisateur Reddit"""
        results = {}
        
        try:
            url = f"https://www.reddit.com/user/{username}/about.json"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                data = resp.json()
                user_data = data.get('data', {})
                results = {
                    'username': user_data.get('name'),
                    'link_karma': user_data.get('link_karma'),
                    'comment_karma': user_data.get('comment_karma'),
                    'created_utc': user_data.get('created_utc'),
                    'is_gold': user_data.get('is_gold'),
                    'is_mod': user_data.get('is_mod'),
                    'url': f"https://www.reddit.com/user/{username}",
                }
        except Exception as e:
            logger.debug(f"Reddit user info error: {e}")
        
        return results


class WhitepagesScraper(BaseScraper):
    """Scraper pour WhitePages"""
    
    def search_phone(self, phone: str) -> Dict[str, Any]:
        """Rechercher un téléphone sur WhitePages"""
        results = {}
        
        try:
            url = f"https://www.whitepages.com/search/results?q={phone}"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                results['found'] = True
                results['url'] = url
        except Exception as e:
            logger.debug(f"WhitePages search error: {e}")
        
        return results


class InstagramScraper(BaseScraper):
    """Scraper pour Instagram"""
    
    def check_username(self, username: str) -> Dict[str, Any]:
        """Vérifier si un username existe sur Instagram"""
        results = {}
        
        try:
            url = f"https://www.instagram.com/{username}/"
            resp = self.fetch(url)
            
            if resp and resp.status_code == 200:
                results['found'] = True
                results['url'] = url
        except Exception as e:
            logger.debug(f"Instagram check error: {e}")
        
        return results

# Instances globales
linkedin_scraper = LinkedInScraper()
github_scraper = GitHubScraper()
twitter_scraper = TwitterScraper()
reddit_scraper = RedditScraper()
whitepages_scraper = WhitepagesScraper()
instagram_scraper = InstagramScraper()