#!/usr/bin/env python3
"""
AdvancedOSINT - Techniques OSINT avancées
"""

import requests
import logging
import re
import socket
import ssl
import subprocess
from typing import Dict, List, Any
from urllib.parse import urlparse
import concurrent.futures

logger = logging.getLogger(__name__)

class AdvancedOSINT:
    """Techniques OSINT avancées pour investigation approfondie"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
    
    def certificate_transparency(self, domain: str) -> List[Dict[str, Any]]:
        """Recherche via Certificate Transparency logs"""
        subdomains = []
        
        try:
            # crt.sh API
            url = f"https://crt.sh/?q=%.{domain}&output=json"
            resp = self.session.get(url, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                seen = set()
                
                for cert in data:
                    name_value = cert.get('name_value', '')
                    names = name_value.split('\n')
                    
                    for name in names:
                        name = name.strip().lower()
                        if name and name not in seen and domain in name:
                            seen.add(name)
                            subdomains.append({
                                'subdomain': name,
                                'issuer': cert.get('issuer_name', ''),
                                'not_before': cert.get('not_before', ''),
                                'not_after': cert.get('not_after', '')
                            })
                
                logger.info(f"Certificate Transparency: {len(subdomains)} sous-domaines trouvés")
        except Exception as e:
            logger.error(f"CT logs error: {e}")
        
        return subdomains
    
    def wayback_machine_search(self, domain: str) -> List[Dict[str, Any]]:
        """Rechercher dans Wayback Machine"""
        results = []
        
        try:
            # API Wayback Machine
            url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&collapse=urlkey&fl=original,timestamp,mimetype,statuscode"
            resp = self.session.get(url, timeout=30)
            
            if resp.status_code == 200:
                data = resp.json()
                
                if len(data) > 1:  # First row is headers
                    for row in data[1:]:
                        if len(row) >= 4:
                            results.append({
                                'url': row[0],
                                'timestamp': row[1],
                                'mimetype': row[2],
                                'status': row[3],
                                'archive_url': f"https://web.archive.org/web/{row[1]}/{row[0]}"
                            })
                
                logger.info(f"Wayback Machine: {len(results)} URLs archivées trouvées")
        except Exception as e:
            logger.error(f"Wayback Machine error: {e}")
        
        return results[:100]  # Limiter les résultats
    
    def shodan_search(self, query: str, api_key: str = None) -> Dict[str, Any]:
        """Recherche Shodan pour infrastructure"""
        results = {'matches': [], 'total': 0}
        
        if not api_key:
            from config import get_config
            api_key = get_config().get_api_key('shodan')
        
        if api_key:
            try:
                # Shodan API
                url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={query}"
                resp = self.session.get(url, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    results = {
                        'matches': data.get('matches', []),
                        'total': data.get('total', 0),
                        'facets': data.get('facets', {})
                    }
                    
                    logger.info(f"Shodan: {results['total']} résultats trouvés")
            except Exception as e:
                logger.error(f"Shodan error: {e}")
        
        return results
    
    def censys_search(self, query: str, api_id: str = None, api_secret: str = None) -> Dict[str, Any]:
        """Recherche Censys pour certificats et hosts"""
        results = {'results': [], 'total': 0}
        
        if not api_id:
            from config import get_config
            config = get_config()
            api_id = config.get_api_key('censys_id')
            api_secret = config.get_api_key('censys_secret')
        
        if api_id and api_secret:
            try:
                import base64
                auth = base64.b64encode(f"{api_id}:{api_secret}".encode()).decode()
                
                url = "https://search.censys.io/api/v2/hosts/search"
                headers = {
                    'Authorization': f'Basic {auth}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'q': query,
                    'per_page': 100
                }
                
                resp = requests.post(url, json=payload, headers=headers, timeout=15)
                
                if resp.status_code == 200:
                    data = resp.json()
                    results = {
                        'results': data.get('result', {}).get('hits', []),
                        'total': data.get('result', {}).get('total', 0)
                    }
                    
                    logger.info(f"Censys: {results['total']} résultats trouvés")
            except Exception as e:
                logger.error(f"Censys error: {e}")
        
        return results
    
    def dns_dumpster(self, domain: str) -> Dict[str, Any]:
        """DNSDumpster pour reconnaissance DNS"""
        results = {
            'dns_records': {},
            'mx_records': [],
            'host_records': [],
            'txt_records': []
        }
        
        try:
            # DNSDumpster nécessite une session avec CSRF token
            url = "https://dnsdumpster.com/"
            
            # Obtenir le CSRF token
            resp = self.session.get(url)
            
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                csrf_token = soup.find('input', {'name': 'csrfmiddlewaretoken'})
                
                if csrf_token:
                    # Faire la recherche
                    data = {
                        'csrfmiddlewaretoken': csrf_token['value'],
                        'targetip': domain
                    }
                    
                    headers = {
                        'Referer': url,
                        'Origin': 'https://dnsdumpster.com'
                    }
                    
                    resp = self.session.post(url, data=data, headers=headers, timeout=30)
                    
                    if resp.status_code == 200:
                        soup = BeautifulSoup(resp.text, 'html.parser')
                        
                        # Parser les résultats
                        tables = soup.find_all('table', {'class': 'table'})
                        
                        for table in tables:
                            rows = table.find_all('tr')
                            for row in rows[1:]:  # Skip header
                                cols = row.find_all('td')
                                if len(cols) >= 2:
                                    record_type = cols[0].text.strip()
                                    record_value = cols[1].text.strip()
                                    
                                    if 'MX' in record_type:
                                        results['mx_records'].append(record_value)
                                    elif 'A' in record_type:
                                        results['host_records'].append(record_value)
                                    elif 'TXT' in record_type:
                                        results['txt_records'].append(record_value)
                        
                        logger.info(f"DNSDumpster: {len(results['host_records'])} hosts trouvés")
        except Exception as e:
            logger.error(f"DNSDumpster error: {e}")
        
        return results
    
    def google_dorks(self, domain: str, email: str = None) -> List[Dict[str, str]]:
        """Google dorks pour recherche avancée"""
        dorks = []
        
        # Dorks pour domaine
        if domain:
            dorks.extend([
                {'description': 'Fichiers PDF', 'query': f'site:{domain} filetype:pdf'},
                {'description': 'Fichiers Excel', 'query': f'site:{domain} filetype:xlsx OR filetype:xls'},
                {'description': 'Fichiers Word', 'query': f'site:{domain} filetype:docx OR filetype:doc'},
                {'description': 'Sous-domaines', 'query': f'site:*.{domain}'},
                {'description': 'Pages de login', 'query': f'site:{domain} inurl:login OR inurl:signin'},
                {'description': 'Pages admin', 'query': f'site:{domain} inurl:admin OR inurl:administrator'},
                {'description': 'Fichiers de config', 'query': f'site:{domain} ext:xml OR ext:conf OR ext:ini'},
                {'description': 'Backups', 'query': f'site:{domain} ext:bkf OR ext:bkp OR ext:bak OR ext:old OR ext:backup'},
                {'description': 'Bases de données', 'query': f'site:{domain} ext:sql OR ext:db OR ext:dbf OR ext:mdb'},
                {'description': 'Logs', 'query': f'site:{domain} ext:log'},
                {'description': 'Emails exposés', 'query': f'site:{domain} "@{domain}"'},
                {'description': 'Répertoires listables', 'query': f'site:{domain} intitle:"index of"'},
                {'description': 'Erreurs PHP', 'query': f'site:{domain} "PHP Parse error" OR "PHP Warning" OR "PHP Error"'},
                {'description': 'Informations sensibles', 'query': f'site:{domain} "password" OR "passwd" OR "pwd"'}
            ])
        
        # Dorks pour email
        if email:
            dorks.extend([
                {'description': 'Email dans les résultats', 'query': f'"{email}"'},
                {'description': 'Email sur pastebin', 'query': f'site:pastebin.com "{email}"'},
                {'description': 'Email sur GitHub', 'query': f'site:github.com "{email}"'},
                {'description': 'Email dans les dumps', 'query': f'"{email}" password'},
                {'description': 'Profils sociaux', 'query': f'"{email}" OR "{email.split("@")[0]}"'}
            ])
        
        # Construire les URLs Google
        for dork in dorks:
            dork['url'] = f"https://www.google.com/search?q={requests.utils.quote(dork['query'])}"
        
        return dorks
    
    def port_scan(self, host: str, top_ports: int = 100) -> List[Dict[str, Any]]:
        """Scanner les ports ouverts"""
        open_ports = []
        
        # Ports communs à scanner
        common_ports = [
            21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 445, 
            993, 995, 1723, 3306, 3389, 5900, 8080, 8443, 8888
        ]
        
        if top_ports > len(common_ports):
            # Ajouter plus de ports
            common_ports.extend(range(1, min(top_ports + 1, 65536)))
        
        common_ports = list(set(common_ports[:top_ports]))
        
        def scan_port(port):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                service = self._get_service_name(port)
                return {
                    'port': port,
                    'state': 'open',
                    'service': service,
                    'banner': self._grab_banner(host, port)
                }
            return None
        
        # Scan parallèle
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            futures = [executor.submit(scan_port, port) for port in common_ports]
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    open_ports.append(result)
        
        open_ports.sort(key=lambda x: x['port'])
        logger.info(f"Port scan: {len(open_ports)} ports ouverts sur {host}")
        
        return open_ports
    
    def _get_service_name(self, port: int) -> str:
        """Obtenir le nom du service pour un port"""
        services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS',
            80: 'HTTP', 110: 'POP3', 143: 'IMAP', 443: 'HTTPS',
            445: 'SMB', 3306: 'MySQL', 3389: 'RDP', 5432: 'PostgreSQL',
            6379: 'Redis', 8080: 'HTTP-Proxy', 8443: 'HTTPS-Alt',
            27017: 'MongoDB', 9200: 'Elasticsearch'
        }
        return services.get(port, f'Unknown({port})')
    
    def _grab_banner(self, host: str, port: int) -> str:
        """Récupérer la bannière d'un service"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            
            # Certains services nécessitent d'envoyer des données d'abord
            if port in [80, 443, 8080, 8443]:
                sock.send(b'HEAD / HTTP/1.0\r\n\r\n')
            
            banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
            sock.close()
            
            return banner[:100] if banner else ''
        except:
            return ''
    
    def metadata_extraction(self, url: str) -> Dict[str, Any]:
        """Extraire les métadonnées d'un site web"""
        metadata = {
            'title': None,
            'description': None,
            'keywords': None,
            'author': None,
            'generator': None,
            'technologies': [],
            'social_media': {},
            'emails': [],
            'phones': []
        }
        
        try:
            resp = self.session.get(url, timeout=15)
            
            if resp.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, 'html.parser')
                
                # Métadonnées basiques
                title = soup.find('title')
                if title:
                    metadata['title'] = title.text.strip()
                
                # Meta tags
                for meta in soup.find_all('meta'):
                    name = meta.get('name', '').lower()
                    property = meta.get('property', '').lower()
                    content = meta.get('content', '')
                    
                    if name == 'description':
                        metadata['description'] = content
                    elif name == 'keywords':
                        metadata['keywords'] = content
                    elif name == 'author':
                        metadata['author'] = content
                    elif name == 'generator':
                        metadata['generator'] = content
                    
                    # Open Graph tags
                    if property.startswith('og:'):
                        metadata['social_media'][property] = content
                    
                    # Twitter cards
                    if name.startswith('twitter:'):
                        metadata['social_media'][name] = content
                
                # Technologies détectées
                # Framework detection
                if soup.find(attrs={'name': 'csrf-token'}):
                    metadata['technologies'].append('Laravel/Rails (CSRF token found)')
                if soup.find(text=re.compile('wp-content')):
                    metadata['technologies'].append('WordPress')
                if soup.find(attrs={'class': re.compile('drupal')}):
                    metadata['technologies'].append('Drupal')
                
                # Extraire emails
                email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
                emails = re.findall(email_pattern, resp.text)
                metadata['emails'] = list(set(emails))[:10]
                
                # Extraire téléphones
                phone_pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,5}[-\s\.]?[0-9]{1,5}'
                phones = re.findall(phone_pattern, resp.text)
                metadata['phones'] = list(set(phones))[:10]
                
                logger.info(f"Métadonnées extraites de {url}")
                
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
        
        return metadata

# Instance globale
advanced_osint = AdvancedOSINT()