#!/usr/bin/env python3
"""
UsernameLookup - Recherche avancée par pseudo
Réseaux sociaux, forums, repos, plateformes gaming
"""

import requests
import logging
import json
from typing import Dict, List, Any
from bs4 import BeautifulSoup
import concurrent.futures

logger = logging.getLogger(__name__)

class UsernameLookup:
    """Moteur de recherche pour pseudonymes"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 8
    
    def search_all_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur tous les réseaux sociaux"""
        results = []
        
        platforms = {
            'twitter': f"https://twitter.com/{username}",
            'instagram': f"https://www.instagram.com/{username}",
            'facebook': f"https://www.facebook.com/{username}",
            'tiktok': f"https://www.tiktok.com/@{username}",
            'youtube': f"https://www.youtube.com/@{username}",
            'snapchat': f"https://www.snapchat.com/add/{username}",
            'reddit': f"https://www.reddit.com/user/{username}",
            'twitch': f"https://www.twitch.tv/{username}",
            'pinterest': f"https://www.pinterest.com/{username}",
            'tumblr': f"https://{username}.tumblr.com",
        }
        
        for platform, url in platforms.items():
            try:
                resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
                
                if resp.status_code == 200:
                    results.append({
                        'platform': platform,
                        'username': username,
                        'url': url,
                        'found': True,
                        'status_code': resp.status_code
                    })
                else:
                    results.append({
                        'platform': platform,
                        'username': username,
                        'url': url,
                        'found': False,
                        'status_code': resp.status_code
                    })
            except requests.Timeout:
                results.append({
                    'platform': platform,
                    'username': username,
                    'url': url,
                    'found': False,
                    'status': 'timeout'
                })
            except Exception as e:
                logger.debug(f"Erreur {platform}: {e}")
        
        return results
    
    def search_forums(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur les forums populaires"""
        results = []
        
        forums = {
            'stack_overflow': f"https://stackoverflow.com/users/?tab=newest&searchTab=&search={username}",
            'medium': f"https://medium.com/search?q={username}",
            '4chan_archive': f"https://www.4plebs.org/search?q={username}",
            'reddit': f"https://www.reddit.com/search/?q={username}",
            'discourse_hub': f"https://www.discourse.org/users/{username}",
        }
        
        for forum, url in forums.items():
            try:
                resp = requests.get(url, headers=self.headers, timeout=self.timeout)
                
                if resp.status_code == 200 and len(resp.text) > 500:
                    results.append({
                        'platform': forum,
                        'username': username,
                        'url': url,
                        'found': True,
                        'content_size': len(resp.text)
                    })
                else:
                    results.append({
                        'platform': forum,
                        'username': username,
                        'found': False
                    })
            except Exception as e:
                logger.debug(f"Forum erreur {forum}: {e}")
        
        return results
    
    def search_github_gitlab(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur GitHub et GitLab"""
        results = []
        
        repos = {
            'github': f"https://api.github.com/users/{username}",
            'gitlab': f"https://gitlab.com/api/v4/users?username={username}",
        }
        
        # GitHub API
        try:
            resp = requests.get(repos['github'], headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                results.append({
                    'platform': 'github',
                    'username': username,
                    'found': True,
                    'profile_url': data.get('html_url'),
                    'name': data.get('name'),
                    'company': data.get('company'),
                    'location': data.get('location'),
                    'bio': data.get('bio'),
                    'public_repos': data.get('public_repos'),
                    'followers': data.get('followers'),
                })
            else:
                results.append({
                    'platform': 'github',
                    'username': username,
                    'found': False
                })
        except Exception as e:
            logger.debug(f"GitHub erreur: {e}")
        
        # GitLab API
        try:
            resp = requests.get(repos['gitlab'], headers=self.headers, timeout=self.timeout)
            if resp.status_code == 200:
                data = resp.json()
                if len(data) > 0:
                    user = data[0]
                    results.append({
                        'platform': 'gitlab',
                        'username': username,
                        'found': True,
                        'name': user.get('name'),
                        'profile_url': user.get('web_url'),
                        'location': user.get('location'),
                    })
                else:
                    results.append({
                        'platform': 'gitlab',
                        'username': username,
                        'found': False
                    })
        except Exception as e:
            logger.debug(f"GitLab erreur: {e}")
        
        return results
    
    def search_gaming_platforms(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur les plateformes gaming"""
        results = []
        
        platforms = {
            'steam': f"https://steamcommunity.com/search/users/?text={username}",
            'xbox_live': f"https://www.xbox.com/en-US/live/",
            'psn': f"https://www.playstation.com/en-us/",
            'discord': f"https://discord.com/users/{username}",
            'minecraft': f"https://namemc.com/search?q={username}",
        }
        
        for platform, url in platforms.items():
            try:
                resp = requests.head(url, headers=self.headers, timeout=self.timeout)
                
                results.append({
                    'platform': platform,
                    'username': username,
                    'search_url': url,
                    'reachable': resp.status_code < 400
                })
            except:
                results.append({
                    'platform': platform,
                    'username': username,
                    'search_url': url,
                    'reachable': False
                })
        
        return results
    
    def search_aggregators(self, username: str) -> List[Dict[str, Any]]:
        """Chercher sur les agrégateurs OSINT"""
        results = []
        
        aggregators = {
            'sherlock': f"https://sherlock-project.github.io/",
            'namechk': f"https://www.namechk.com/?u={username}",
            'knowem': f"https://knowem.com/?s={username}",
            'google_dorking': f"https://www.google.com/search?q=%22{username}%22",
        }
        
        for agg, url in aggregators.items():
            try:
                resp = requests.head(url, headers=self.headers, timeout=self.timeout)
                
                results.append({
                    'aggregator': agg,
                    'username': username,
                    'url': url,
                    'available': resp.status_code < 400
                })
            except:
                results.append({
                    'aggregator': agg,
                    'username': username,
                    'url': url,
                    'available': False
                })
        
        return results