#!/usr/bin/env python3
"""
config.py - Gestion centralisée de la configuration
Charge depuis YAML, variables env, ou défauts
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
    
    PROJECT_DIR = Path(__file__).parent  
    CONFIG_FILE = PROJECT_DIR / 'config.yaml'
    
    # Defaults
    DEFAULTS = {
        'app': {
            'name': 'Raven Trace',
            'version': '1.0.0',
            'debug': False,
            'verbose': True,
        },
        'search': {
            'timeout': 10,
            'workers': 5,
            'rotate_user_agent': True,
            'rate_limit': 30,
            'deep_scan_default': False,
        },
        'cache': {
            'ttl_hours': 24,
            'auto_cleanup': True,
            'cleanup_days': 7,
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
        'output': {
            'default_format': 'table',
            'show_confidence': True,
            'show_breaches': True,
        },
        'security': {
            'verify_ssl': True,
            'mask_sensitive': True,
        },
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """Initialiser la configuration"""
        # Utiliser le fichier fourni ou celui par défaut dans le projet
        if config_file:
            self.config_file = Path(config_file)
        else:
            self.config_file = self.CONFIG_FILE
            
        self.config = self.DEFAULTS.copy()
        self._setup_directories()
        self._load_config()
    
    def _setup_directories(self):
        """Créer les répertoires nécessaires"""
        try:
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)
            self.LOG_DIR.mkdir(parents=True, exist_ok=True)
            self.EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            self.REPORT_DIR.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Répertoires créés: {self.CONFIG_DIR}")
        except Exception as e:
            logger.error(f"Erreur création répertoires: {e}")
    
    def _load_config(self):
        """Charger la configuration depuis YAML"""
        try:
            # Afficher le chemin pour debug
            logger.debug(f"Recherche du fichier config dans: {self.config_file}")
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f) or {}
                    self._merge_config(yaml_config)
                logger.info(f"Configuration chargée depuis: {self.config_file}")
            else:
                # Si le fichier n'existe pas, essayer dans le répertoire courant
                alternative_path = Path.cwd() / 'config.yaml'
                if alternative_path.exists():
                    self.config_file = alternative_path
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        yaml_config = yaml.safe_load(f) or {}
                        self._merge_config(yaml_config)
                    logger.info(f"Configuration chargée depuis: {self.config_file}")
                else:
                    logger.warning(f"Fichier config non trouvé dans: {self.config_file} ou {alternative_path}")
                    logger.info("Utilisation de la configuration par défaut")
        except Exception as e:
            logger.error(f"Erreur chargement config: {e}")
            logger.info("Utilisation de la configuration par défaut")
    
    def _merge_config(self, yaml_config: Dict[str, Any]):
        """Fusionner configuration YAML avec defaults"""
        for key, value in yaml_config.items():
            if key in self.config and isinstance(self.config[key], dict):
                self.config[key].update(value)
            else:
                self.config[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Obtenir une valeur de configuration"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Définir une valeur de configuration"""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        logger.debug(f"Configuration définie: {key} = {value}")
    
    def get_or_env(self, key: str, env_var: str, default: Any = None) -> Any:
        """Obtenir depuis config ou variable d'environnement"""
        env_value = os.getenv(env_var)
        
        if env_value is not None:
            return env_value
        
        return self.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Exporter la configuration en dictionnaire"""
        return self.config.copy()
    
    def to_yaml(self) -> str:
        """Exporter la configuration en YAML"""
        return yaml.dump(self.config, default_flow_style=False, allow_unicode=True)
    
    def save_to_file(self, filepath: str = None):
        """Sauvegarder la configuration en fichier"""
        filepath = filepath or self.config_file
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.to_yaml())
            logger.debug(f"Configuration sauvegardée: {filepath}")
        except Exception as e:
            logger.error(f"Erreur sauvegarde config: {e}")


class SearchConfig:
    """Configuration pour les recherches"""
    
    def __init__(self, config: Config):
        self.config = config
    
    @property
    def timeout(self) -> int:
        return self.config.get('search.timeout', 10)
    
    @property
    def workers(self) -> int:
        return self.config.get('search.workers', 5)
    
    @property
    def rotate_user_agent(self) -> bool:
        return self.config.get('search.rotate_user_agent', True)
    
    @property
    def rate_limit(self) -> int:
        return self.config.get('search.rate_limit', 30)
    
    @property
    def deep_scan_default(self) -> bool:
        return self.config.get('search.deep_scan_default', False)


class CacheConfig:
    """Configuration du cache"""
    
    def __init__(self, config: Config):
        self.config = config
    
    @property
    def directory(self) -> Path:
        cache_dir = self.config.get('cache.directory')
        if cache_dir:
            return Path(cache_dir).expanduser()
        return Config.CACHE_DIR
    
    @property
    def ttl_hours(self) -> int:
        return self.config.get('cache.ttl_hours', 24)
    
    @property
    def auto_cleanup(self) -> bool:
        return self.config.get('cache.auto_cleanup', True)
    
    @property
    def cleanup_days(self) -> int:
        return self.config.get('cache.cleanup_days', 7)


class OutputConfig:
    """Configuration de sortie"""
    
    def __init__(self, config: Config):
        self.config = config
    
    @property
    def default_format(self) -> str:
        return self.config.get('output.default_format', 'table')
    
    @property
    def show_confidence(self) -> bool:
        return self.config.get('output.show_confidence', True)
    
    @property
    def show_breaches(self) -> bool:
        return self.config.get('output.show_breaches', True)
    
    @property
    def export_dir(self) -> Path:
        export_dir = self.config.get('output.export_dir')
        if export_dir:
            return Path(export_dir).expanduser()
        return Config.EXPORT_DIR


# Instance globale de configuration
_config_instance = None

def get_config() -> Config:
    """Obtenir l'instance globale de configuration"""
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance

def get_search_config() -> SearchConfig:
    """Obtenir la config de recherche"""
    return SearchConfig(get_config())

def get_cache_config() -> CacheConfig:
    """Obtenir la config de cache"""
    return CacheConfig(get_config())

def get_output_config() -> OutputConfig:
    """Obtenir la config de sortie"""
    return OutputConfig(get_config())

# Exemple d'utilisation
if __name__ == '__main__':
    # Pour debug
    logging.basicConfig(level=logging.DEBUG)
    
    config = get_config()
    
    print(f"Fichier config utilisé: {config.config_file}")
    print(f"Fichier existe: {config.config_file.exists()}")
    print("\nConfiguration Raven Trace:")
    print(config.to_yaml())
    
    # Accès aux valeurs
    print(f"\nTimeout: {config.get('search.timeout')}")
    print(f"Cache TTL: {config.get('cache.ttl_hours')} heures")
    print(f"Workers: {config.get('search.workers')}")