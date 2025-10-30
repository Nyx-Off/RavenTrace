#!/usr/bin/env python3
"""
KaliTools - Intégration des outils OSINT de Kali Linux
"""

import subprocess
import json
import logging
from typing import Dict, List, Any
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class KaliToolsIntegration:
    """Intégration avec les outils OSINT de Kali Linux"""
    
    def __init__(self):
        self.check_tools_availability()
    
    def check_tools_availability(self):
        """Vérifier la disponibilité des outils"""
        self.tools_available = {
            'theharvester': self._check_command('theHarvester'),
            'sherlock': self._check_command('sherlock'),
            'holehe': self._check_command('holehe'),
            'phoneinfoga': self._check_command('phoneinfoga'),
            'whatweb': self._check_command('whatweb'),
            'dmitry': self._check_command('dmitry'),
            'maltego': self._check_command('maltego'),
            'recon-ng': self._check_command('recon-ng')
        }
        
        logger.info(f"Outils Kali disponibles: {[k for k,v in self.tools_available.items() if v]}")
    
    def _check_command(self, command: str) -> bool:
        """Vérifier si une commande est disponible"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _run_command(self, command: List[str], timeout: int = 30) -> str:
        """Exécuter une commande système"""
        try:
            result = subprocess.run(
                command, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout lors de l'exécution de: {' '.join(command)}")
            return ""
        except Exception as e:
            logger.error(f"Erreur commande: {e}")
            return ""
    
    def theharvester_search(self, domain: str) -> Dict[str, Any]:
        """Utiliser theHarvester pour rechercher des emails et sous-domaines"""
        if not self.tools_available.get('theharvester'):
            return {'error': 'theHarvester not available'}
        
        results = {
            'emails': [],
            'hosts': [],
            'ips': [],
            'subdomains': []
        }
        
        try:
            # Exécuter theHarvester avec plusieurs sources
            sources = ['google', 'bing', 'linkedin', 'twitter', 'yahoo']
            
            for source in sources:
                cmd = [
                    'theHarvester',
                    '-d', domain,
                    '-b', source,
                    '-l', '100'
                ]
                
                output = self._run_command(cmd, timeout=60)
                
                # Parser les résultats
                if output:
                    # Extraire les emails
                    email_pattern = r'[\w\.-]+@' + re.escape(domain)
                    emails = re.findall(email_pattern, output)
                    results['emails'].extend(emails)
                    
                    # Extraire les hosts
                    host_pattern = r'[\w\.-]+\.' + re.escape(domain)
                    hosts = re.findall(host_pattern, output)
                    results['hosts'].extend(hosts)
                    
                    # Extraire les IPs
                    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
                    ips = re.findall(ip_pattern, output)
                    results['ips'].extend(ips)
            
            # Dédupliquer
            results['emails'] = list(set(results['emails']))
            results['hosts'] = list(set(results['hosts']))
            results['ips'] = list(set(results['ips']))
            
            logger.info(f"TheHarvester: {len(results['emails'])} emails, {len(results['hosts'])} hosts trouvés")
            
        except Exception as e:
            logger.error(f"TheHarvester error: {e}")
        
        return results
    
    def sherlock_search(self, username: str) -> List[Dict[str, Any]]:
        """Utiliser Sherlock pour chercher un username"""
        if not self.tools_available.get('sherlock'):
            return []
        
        results = []
        
        try:
            # Créer un fichier temporaire pour les résultats JSON
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                output_file = f.name
            
            cmd = [
                'sherlock',
                username,
                '--output', output_file,
                '--print-all',
                '--timeout', '10'
            ]
            
            # Exécuter Sherlock
            output = self._run_command(cmd, timeout=120)
            
            # Parser le fichier JSON de sortie
            if Path(output_file).exists():
                with open(output_file, 'r') as f:
                    try:
                        sherlock_data = json.load(f)
                        
                        for platform, data in sherlock_data.items():
                            if isinstance(data, dict):
                                results.append({
                                    'platform': platform,
                                    'username': username,
                                    'found': data.get('status', '').lower() == 'claimed',
                                    'url': data.get('url_main', ''),
                                    'error': data.get('error_msg', ''),
                                    'source': 'sherlock'
                                })
                    except json.JSONDecodeError:
                        # Si pas de JSON, parser la sortie texte
                        for line in output.split('\n'):
                            if 'https://' in line or 'http://' in line:
                                # Extraire l'URL et la plateforme
                                parts = line.strip().split()
                                if parts:
                                    url = [p for p in parts if p.startswith('http')][0] if any(p.startswith('http') for p in parts) else ''
                                    if url:
                                        platform = url.split('/')[2].replace('www.', '').split('.')[0]
                                        results.append({
                                            'platform': platform,
                                            'username': username,
                                            'found': True,
                                            'url': url,
                                            'source': 'sherlock'
                                        })
                
                # Nettoyer le fichier temporaire
                Path(output_file).unlink(missing_ok=True)
            
            logger.info(f"Sherlock: {len(results)} profils trouvés pour {username}")
            
        except Exception as e:
            logger.error(f"Sherlock error: {e}")
        
        return results
    
    def holehe_check(self, email: str) -> List[Dict[str, Any]]:
        """Utiliser holehe pour vérifier l'existence d'un email"""
        if not self.tools_available.get('holehe'):
            return []
        
        results = []
        
        try:
            cmd = ['holehe', email, '--only-used']
            output = self._run_command(cmd, timeout=60)
            
            # Parser la sortie de holehe
            for line in output.split('\n'):
                if '[+]' in line:  # Compte trouvé
                    parts = line.split('[+]')[1].strip()
                    platform = parts.split()[0] if parts else 'unknown'
                    
                    results.append({
                        'platform': platform.lower(),
                        'email': email,
                        'found': True,
                        'source': 'holehe'
                    })
            
            logger.info(f"Holehe: {len(results)} comptes trouvés pour {email}")
            
        except Exception as e:
            logger.error(f"Holehe error: {e}")
        
        return results
    
    def phoneinfoga_scan(self, phone: str) -> Dict[str, Any]:
        """Utiliser PhoneInfoga pour scanner un numéro"""
        if not self.tools_available.get('phoneinfoga'):
            return {}
        
        results = {
            'valid': False,
            'carrier': None,
            'country': None,
            'line_type': None,
            'location': None
        }
        
        try:
            cmd = ['phoneinfoga', 'scan', '-n', phone]
            output = self._run_command(cmd, timeout=30)
            
            # Parser la sortie
            if 'Valid' in output:
                results['valid'] = True
            
            # Extraire les informations
            patterns = {
                'carrier': r'Carrier:\s*(.+)',
                'country': r'Country:\s*(.+)',
                'line_type': r'Line type:\s*(.+)',
                'location': r'Location:\s*(.+)'
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    results[key] = match.group(1).strip()
            
            logger.info(f"PhoneInfoga: Scan complété pour {phone}")
            
        except Exception as e:
            logger.error(f"PhoneInfoga error: {e}")
        
        return results
    
    def dmitry_gather(self, domain: str) -> Dict[str, Any]:
        """Utiliser dmitry pour gather des infos sur un domaine"""
        if not self.tools_available.get('dmitry'):
            return {}
        
        results = {
            'emails': [],
            'subdomains': [],
            'whois_info': {}
        }
        
        try:
            cmd = ['dmitry', '-wine', domain]
            output = self._run_command(cmd, timeout=45)
            
            # Parser emails
            email_pattern = r'[\w\.-]+@[\w\.-]+'
            results['emails'] = list(set(re.findall(email_pattern, output)))
            
            # Parser subdomains
            subdomain_pattern = r'[\w\.-]+\.' + re.escape(domain)
            results['subdomains'] = list(set(re.findall(subdomain_pattern, output)))
            
            logger.info(f"Dmitry: {len(results['emails'])} emails trouvés")
            
        except Exception as e:
            logger.error(f"Dmitry error: {e}")
        
        return results

# Instance globale
kali_tools = KaliToolsIntegration()