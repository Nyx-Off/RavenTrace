#!/usr/bin/env python3
"""
social_media.py - Intégrations réseaux sociaux
"""

import requests
import logging
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class SocialMediaSearcher:
    """Recherche sur réseaux sociaux"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        }
        self.timeout = 8
    
    def check_platform(self, username: str, platform: str, url_template: str) -> Dict[str, Any]:
        """Vérifier un username sur une plateforme"""
        result = {
            'platform': platform,
            'username': username,
            'found': False,
            'url': None,
            'status_code': None
        }
        
        try:
            url = url_template.format(username=username)
            resp = requests.head(url, headers=self.headers, timeout=self.timeout, allow_redirects=True)
            
            result['status_code'] = resp.status_code
            
            if resp.status_code == 200:
                result['found'] = True
                result['url'] = url
            else:
                result['found'] = False
        except requests.Timeout:
            result['status'] = 'timeout'
        except Exception as e:
            logger.debug(f"Error checking {platform}: {e}")
            result['status'] = 'error'
        
        return result
    
    def search_all_platforms(self, username: str, parallel: bool = True) -> List[Dict[str, Any]]:
        """Chercher un username sur tous les réseaux"""
        
        platforms = {
            'twitter': 'https://twitter.com/{username}',
            'instagram': 'https://www.instagram.com/{username}/',
            'facebook': 'https://www.facebook.com/{username}',
            'linkedin': 'https://www.linkedin.com/in/{username}',
            'youtube': 'https://www.youtube.com/@{username}',
            'tiktok': 'https://www.tiktok.com/@{username}',
            'reddit': 'https://www.reddit.com/user/{username}',
            'snapchat': 'https://www.snapchat.com/add/{username}',
            'twitch': 'https://www.twitch.tv/{username}',
            'pinterest': 'https://www.pinterest.com/{username}',
            'tumblr': 'https://{username}.tumblr.com',
            'github': 'https://github.com/{username}',
            'gitlab': 'https://gitlab.com/{username}',
            'patreon': 'https://www.patreon.com/{username}',
            'telegram': 'https://t.me/{username}',
            'mastodon': 'https://mastodon.social/@{username}',
            'medium': 'https://medium.com/@{username}',
            'deviantart': 'https://www.deviantart.com/{username}',
            'flickr': 'https://www.flickr.com/photos/{username}',
            'vimeo': 'https://vimeo.com/{username}',
        }
        
        results = []
        
        if parallel:
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
                        logger.debug(f"Parallel search error: {e}")
        else:
            for platform, url in platforms.items():
                result = self.check_platform(username, platform, url)
                results.append(result)
        
        return results
    
    def search_email_platforms(self, email: str) -> List[Dict[str, Any]]:
        """Chercher un email sur les réseaux"""
        
        platforms = {
            'facebook_search': f"https://www.facebook.com/search/people/?q={email}",
            'linkedin_search': f"https://www.linkedin.com/search/results/people/?keywords={email}",
            'twitter_search': f"https://twitter.com/search?q={email}",
            'github_search': f"https://github.com/search?q={email}",
        }
        
        results = []
        
        for platform, url in platforms.items():
            result = {
                'platform': platform,
                'email': email,
                'search_url': url,
                'reachable': False
            }
            
            try:
                resp = requests.head(url, headers=self.headers, timeout=5)
                result['reachable'] = resp.status_code < 400
            except:
                pass
            
            results.append(result)
        
        return results
    
    def search_phone_platforms(self, phone: str) -> List[Dict[str, Any]]:
        """Chercher un téléphone sur certains réseaux"""
        
        platforms = {
            'facebook': f"https://www.facebook.com/search/people/?phone={phone}",
            'linkedin': f"https://www.linkedin.com/search/results/people/?phone={phone}",
            'whatsapp': f"https://www.whatsapp.com/?phone={phone}",
        }
        
        results = []
        
        for platform, url in platforms.items():
            result = {
                'platform': platform,
                'phone': phone,
                'search_url': url,
                'reachable': False
            }
            
            try:
                resp = requests.head(url, headers=self.headers, timeout=5)
                result['reachable'] = resp.status_code < 400
            except:
                pass
            
            results.append(result)
        
        return results

# Instance global
social_media_searcher = SocialMediaSearcher()