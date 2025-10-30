#!/usr/bin/env python3
"""
CacheDB - Gestion du cache SQLite local
Utilise sqlite3 intégré à Python
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class CacheDB:
    """Gestion du cache SQLite"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            cache_dir = Path.home() / '.raven_trace' / 'cache'
            cache_dir.mkdir(parents=True, exist_ok=True)
            db_path = cache_dir / 'cache.db'  # Ajout de l'extension .db
        
        self.db_path = str(db_path)  # Convertir en string pour sqlite3
        self.init_db()
    
    def init_db(self):
        """Initialiser la base de données"""
        try:
            # Utiliser sqlite3 intégré
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Table pour emails
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS email_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    results TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table pour téléphones
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS phone_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone TEXT UNIQUE NOT NULL,
                    results TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table pour usernames
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS username_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    results TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Créer des index pour améliorer les performances
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON email_cache(email)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_email_timestamp ON email_cache(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone ON phone_cache(phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_phone_timestamp ON phone_cache(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username ON username_cache(username)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_username_timestamp ON username_cache(timestamp)')
            
            conn.commit()
            conn.close()
            logger.debug(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Erreur init DB: {e}")
    
    def save_email(self, email: str, results: Dict[str, Any], ttl_hours: int = 24):
        """Sauvegarder les résultats d'une recherche email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            
            cursor.execute('''
                INSERT OR REPLACE INTO email_cache (email, results, timestamp)
                VALUES (?, ?, datetime('now'))
            ''', (email, results_json))
            
            conn.commit()
            conn.close()
            logger.debug(f"Email cache sauvegardé: {email}")
        except Exception as e:
            logger.error(f"Erreur save email cache: {e}")
    
    def get_email(self, email: str, ttl_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Récupérer les résultats en cache pour un email"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # SQLite utilise datetime('now', '-X hours') pour le calcul de date
            cursor.execute('''
                SELECT results FROM email_cache 
                WHERE email = ? AND timestamp > datetime('now', '-' || ? || ' hours')
            ''', (email, ttl_hours))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.debug(f"Email cache récupéré: {email}")
                return json.loads(row[0])
            else:
                logger.debug(f"Email cache expiré ou non trouvé: {email}")
                return None
        except Exception as e:
            logger.error(f"Erreur get email cache: {e}")
            return None
    
    def save_phone(self, phone: str, results: Dict[str, Any], ttl_hours: int = 24):
        """Sauvegarder les résultats d'une recherche téléphone"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            
            cursor.execute('''
                INSERT OR REPLACE INTO phone_cache (phone, results, timestamp)
                VALUES (?, ?, datetime('now'))
            ''', (phone, results_json))
            
            conn.commit()
            conn.close()
            logger.debug(f"Phone cache sauvegardé: {phone}")
        except Exception as e:
            logger.error(f"Erreur save phone cache: {e}")
    
    def get_phone(self, phone: str, ttl_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Récupérer les résultats en cache pour un téléphone"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT results FROM phone_cache 
                WHERE phone = ? AND timestamp > datetime('now', '-' || ? || ' hours')
            ''', (phone, ttl_hours))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.debug(f"Phone cache récupéré: {phone}")
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Erreur get phone cache: {e}")
            return None
    
    def save_username(self, username: str, results: Dict[str, Any], ttl_hours: int = 24):
        """Sauvegarder les résultats d'une recherche username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            results_json = json.dumps(results, ensure_ascii=False, indent=2)
            
            cursor.execute('''
                INSERT OR REPLACE INTO username_cache (username, results, timestamp)
                VALUES (?, ?, datetime('now'))
            ''', (username, results_json))
            
            conn.commit()
            conn.close()
            logger.debug(f"Username cache sauvegardé: {username}")
        except Exception as e:
            logger.error(f"Erreur save username cache: {e}")
    
    def get_username(self, username: str, ttl_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Récupérer les résultats en cache pour un username"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT results FROM username_cache 
                WHERE username = ? AND timestamp > datetime('now', '-' || ? || ' hours')
            ''', (username, ttl_hours))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                logger.debug(f"Username cache récupéré: {username}")
                return json.loads(row[0])
            return None
        except Exception as e:
            logger.error(f"Erreur get username cache: {e}")
            return None
    
    def clear_old_cache(self, days: int = 7):
        """Nettoyer le cache expiré"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Utiliser la syntaxe SQLite pour les dates
            cursor.execute('''
                DELETE FROM email_cache 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            cursor.execute('''
                DELETE FROM phone_cache 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            cursor.execute('''
                DELETE FROM username_cache 
                WHERE timestamp < datetime('now', '-' || ? || ' days')
            ''', (days,))
            
            conn.commit()
            
            # Optimiser la base de données après suppression
            cursor.execute('VACUUM')
            
            conn.close()
            logger.info(f"Cache nettoyé (> {days} jours)")
        except Exception as e:
            logger.error(f"Erreur clear cache: {e}")
    
    def get_stats(self) -> Dict[str, int]:
        """Obtenir les statistiques du cache"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            stats = {}
            
            # Compter les entrées dans chaque table
            cursor.execute('SELECT COUNT(*) FROM email_cache')
            stats['emails'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM phone_cache')
            stats['phones'] = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM username_cache')
            stats['usernames'] = cursor.fetchone()[0]
            
            # Taille de la base de données
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['db_size_bytes'] = cursor.fetchone()[0]
            
            conn.close()
            
            return stats
        except Exception as e:
            logger.error(f"Erreur get stats: {e}")
            return {'emails': 0, 'phones': 0, 'usernames': 0, 'db_size_bytes': 0}