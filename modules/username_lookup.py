#!/usr/bin/env python3
"""
UsernameLookup - Recherche avancée par pseudo avec résultats réels
"""

import requests
import logging
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

logger = logging.getLogger(__name__)

class UsernameLookup:
    """Moteur de recherche pour pseudonymes avec résultats concrets"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
    
    def check_platform(self, username: str, platform: str, url: str) -> Dict[str, Any]:
        """Vérifier un username sur une plateforme"""
        result = {
            'platform': platform,
            'username': username,
            'found': False,
            'url': url,
            'status_code': None,
            'accessible': False
        }
        
        try:
            resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            result['status_code'] = resp.status_code
            result['accessible'] = True
            
            if resp.status_code == 200:
                result['found'] = True
                logger.debug(f"✓ {platform}: {username} TROUVÉ")
            else:
                logger.debug(f"✗ {platform}: Status {resp.status_code}")
                
        except requests.Timeout:
            result['status'] = 'timeout'
            logger.debug(f"✗ {platform}: Timeout")
        except Exception as e:
            result['status'] = 'error'
            logger.debug(f"✗ {platform}: {str(e)}")
        
        return result
    
    def search_all_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Chercher un username sur les réseaux sociaux majeurs"""
        
        platforms = {
            'github': f"https://github.com/{username}",
            'twitter': f"https://twitter.com/{username}",
            'instagram': f"https://www.instagram.com/{username}/",
            'facebook': f"https://www.facebook.com/{username}",
            'linkedin': f"https://www.linkedin.com/in/{username}",
            'youtube': f"https://www.youtube.com/@{username}",
            'tiktok': f"https://www.tiktok.com/@{username}",
            'reddit': f"https://www.reddit.com/user/{username}",
            'twitch': f"https://www.twitch.tv/{username}",
            'pinterest': f"https://www.pinterest.com/{username}",
            'snapchat': f"https://www.snapchat.com/add/{username}",
            'telegram': f"https://t.me/{username}",
            'mastodon': f"https://mastodon.social/@{username}",
            'bluesky': f"https://bsky.app/profile/{username}",
            'tumblr': f"https://{username}.tumblr.com",
            'gitlab': f"https://gitlab.com/{username}",
            'medium': f"https://medium.com/@{username}",
        }
        
        results = []
        
        # Recherche parallèle pour plus de performance
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(self.check_platform, username, platform, url): platform
                for platform, url in platforms.items()
            }
            
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    logger.debug(f"Erreur parallèle: {e}")
        
        # Trier par trouvés d'abord
        results.sort(key=lambda x: x['found'], reverse=True)
        logger.info(f"Résultats trouvés: {sum(1 for r in results if r['found'])}/{len(results)}")
        
        return results
    
    def search_github_advanced(self, username: str) -> Dict[str, Any]:
        """Recherche avancée GitHub via API"""
        results = {}
        
        try:
            # GitHub API publique - pas de clé requise
            url = f"https://api.github.com/users/{username}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                results = {
                    'platform': 'github',
                    'username': username,
                    'found': True,
                    'name': data.get('name'),
                    'bio': data.get('bio'),
                    'location': data.get('location'),
                    'company': data.get('company'),
                    'blog': data.get('blog'),
                    'email': data.get('email'),
                    'followers': data.get('followers'),
                    'following': data.get('following'),
                    'public_repos': data.get('public_repos'),
                    'public_gists': data.get('public_gists'),
                    'profile_url': data.get('html_url'),
                    'created_at': data.get('created_at'),
                    'updated_at': data.get('updated_at'),
                }
                logger.info(f"GitHub: {username} - {data.get('followers')} followers")
            else:
                results['found'] = False
                
        except Exception as e:
            logger.debug(f"GitHub API erreur: {e}")
        
        return results
    
    def search_reddit_advanced(self, username: str) -> Dict[str, Any]:
        """Recherche avancée Reddit via API"""
        results = {}
        
        try:
            url = f"https://www.reddit.com/user/{username}/about.json"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200:
                data = resp.json()
                user_data = data.get('data', {})
                
                results = {
                    'platform': 'reddit',
                    'username': username,
                    'found': True,
                    'display_name': user_data.get('name'),
                    'link_karma': user_data.get('link_karma'),
                    'comment_karma': user_data.get('comment_karma'),
                    'is_gold': user_data.get('is_gold'),
                    'is_mod': user_data.get('is_mod'),
                    'is_verified': user_data.get('verified'),
                    'created_utc': user_data.get('created_utc'),
                    'profile_url': f"https://www.reddit.com/user/{username}",
                }
                logger.info(f"Reddit: {username} - {user_data.get('link_karma')} link karma")
            else:
                results['found'] = False
                
        except Exception as e:
            logger.debug(f"Reddit API erreur: {e}")
        
        return results
    
    def search_twitter_advanced(self, username: str) -> Dict[str, Any]:
        """Vérification Twitter"""
        results = {
            'platform': 'twitter',
            'username': username,
            'found': False,
            'search_url': f"https://twitter.com/{username}"
        }
        
        try:
            url = f"https://twitter.com/{username}"
            resp = requests.get(url, headers=self.headers, timeout=self.timeout)
            
            if resp.status_code == 200 and 'not found' not in resp.text.lower():
                results['found'] = True
                logger.info(f"Twitter: {username} trouvé")
        except Exception as e:
            logger.debug(f"Twitter erreur: {e}")
        
        return results
    
    def search_forums(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur les forums populaires"""
        results = []
        
        forums = {
            'stackoverflow': f"https://stackoverflow.com/users/search?tab=newest&searchTab=&search={username}",
            'medium': f"https://medium.com/search?q={username}",
            'dev.to': f"https://dev.to/search?q={username}",
            'hashnode': f"https://hashnode.com/search?q={username}",
        }
        
        for forum, url in forums.items():
            try:
                resp = requests.get(url, headers=self.headers, timeout=8)
                
                if resp.status_code == 200 and len(resp.text) > 500:
                    results.append({
                        'platform': forum,
                        'username': username,
                        'found': True,
                        'url': url,
                        'content_size': len(resp.text)
                    })
                else:
                    results.append({
                        'platform': forum,
                        'username': username,
                        'found': False,
                    })
            except Exception as e:
                logger.debug(f"Forum {forum} erreur: {e}")
        
        return results
    
    def search_code_repositories(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur les dépôts de code"""
        results = []
        
        try:
            # GitHub API
            github_result = self.search_github_advanced(username)
            if github_result.get('found'):
                results.append(github_result)
        except Exception as e:
            logger.debug(f"Code repo erreur: {e}")
        
        return results