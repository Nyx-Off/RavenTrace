#!/usr/bin/env python3
"""
config.py - Gestion centralisée de la configuration
Charge depuis YAML avec support complet
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

class Config:
    """Gestionnaire de configuration Raven Trace"""
    
    # Chemins
    CONFIG_DIR = Path.home() / '.raven_trace'
    CACHE_DIR = CONFIG_DIR / 'cache'
    LOG_DIR = CONFIG_DIR / 'logs'
    EXPORT_DIR = CONFIG_DIR / 'exports'
    REPORT_DIR = CONFIG_DIR / 'reports'
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialiser la configuration"""
        self.config_file = Path(config_file) if config_file else Path("config.yaml")
        self.config = {}
        self._setup_directories()
        self._load_config()
    
    def _setup_directories(self):
        """Créer les répertoires nécessaires"""
        for directory in [self.CONFIG_DIR, self.CACHE_DIR, self.LOG_DIR, 
                         self.EXPORT_DIR, self.REPORT_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """Charger la configuration depuis YAML"""
        try:
            # Chercher config.yaml dans plusieurs emplacements
            config_paths = [
                self.config_file,
                Path.cwd() / 'config.yaml',
                self.CONFIG_DIR / 'config.yaml',
                Path(__file__).parent / 'config.yaml'
            ]
            
            for path in config_paths:
                if path.exists():
                    with open(path, 'r', encoding='utf-8') as f:
                        self.config = yaml.safe_load(f) or {}
                    logger.info(f"Configuration chargée depuis: {path}")
                    self.config_file = path
                    break
            else:
                logger.warning("Aucun fichier config.yaml trouvé, utilisation des valeurs par défaut")
                self._set_defaults()
                
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
            self._set_defaults()
    
    def _set_defaults(self):
        """Définir les valeurs par défaut"""
        self.config = {
            'app': {'name': 'Raven Trace', 'version': '1.0.0'},
            'search': {'timeout': 10, 'workers': 5, 'rate_limit': 30},
            'cache': {'ttl_hours': 24, 'auto_cleanup': True},
            'apis': {},
            'sources': {
                'email': {'emailrep': True, 'hunter': True, 'dns_records': True},
                'phone': {'carrier_lookup': True, 'truecaller': True},
                'username': {'github': True, 'twitter': True, 'instagram': True}
            },
            'kali_tools': {
                'theharvester': True,
                'sherlock': True,
                'holehe': True,
                'phoneinfoga': True
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtenir une valeur de configuration avec notation pointée"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_api_key(self, api_name: str) -> Optional[str]:
        """Obtenir une clé API depuis config ou env"""
        # D'abord essayer depuis le config
        api_key = self.get(f'apis.{api_name}_api_key')
        
        # Si pas trouvé, essayer depuis les variables d'environnement
        if not api_key:
            env_var = f"{api_name.upper()}_API_KEY"
            api_key = os.getenv(env_var)
        
        return api_key if api_key else None

# Instance globale
_config_instance = None

def get_config() -> Config:
    """Obtenir l'instance globale de configuration"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance