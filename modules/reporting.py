#!/usr/bin/env python3
"""
Reporting - Génération de rapports détaillés et statistiques
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Génération de rapports détaillés"""
    
    def __init__(self):
        self.report_dir = Path.home() / '.raven_trace' / 'reports'
        self.report_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_email_report(self, results: Dict[str, Any], filepath: str = None) -> str:
        """Générer un rapport email détaillé"""
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.report_dir / f"email_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'email',
            'email': results.get('email'),
            'confidence': results.get('confidence', 0),
            'summary': {
                'total_sources': len(results.get('sources', {})),
                'breaches_found': len(results.get('breaches', [])),
                'social_profiles': len(results.get('social_profiles', [])),
                'dns_valid': results.get('dns', {}).get('dns', {}).get('valid_domain', False),
            },
            'details': results,
            'recommendations': self._get_email_recommendations(results)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Email report généré: {filepath}")
        return str(filepath)
    
    def generate_username_report(self, results: Dict[str, Any], filepath: str = None) -> str:
        """Générer un rapport username détaillé"""
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.report_dir / f"username_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'username',
            'username': results.get('username'),
            'confidence': results.get('confidence', 0),
            'summary': {
                'total_profiles_found': results.get('profiles_found', 0),
                'social_platforms': len(results.get('social_media', [])),
                'code_repositories': len(results.get('code_repositories', [])),
                'forums': len(results.get('forums', [])),
            },
            'platforms_found': [
                p.get('platform') for p in results.get('social_media', []) 
                if p.get('found')
            ],
            'details': results,
            'recommendations': self._get_username_recommendations(results)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Username report généré: {filepath}")
        return str(filepath)
    
    def generate_phone_report(self, results: Dict[str, Any], filepath: str = None) -> str:
        """Générer un rapport phone détaillé"""
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.report_dir / f"phone_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'phone',
            'phone': results.get('phone'),
            'summary': {
                'valid': results.get('carrier_info', {}).get('valid', False),
                'carrier': results.get('carrier_info', {}).get('carrier', 'N/A'),
                'country': results.get('carrier_info', {}).get('country', 'N/A'),
                'location': results.get('location', {}).get('location', 'N/A'),
                'is_voip': results.get('voip_info', {}).get('is_voip', False),
                'data_brokers_count': len(results.get('data_brokers', [])),
            },
            'details': results,
            'recommendations': self._get_phone_recommendations(results)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Phone report généré: {filepath}")
        return str(filepath)
    
    def _get_email_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Recommandations pour email"""
        recommendations = []
        
        breaches = results.get('breaches', [])
        if breaches and breaches[0].get('status') != 'clean':
            recommendations.append("⚠️  Email trouvé dans des fuites de données - Changer le mot de passe")
        
        rep = results.get('reputation', {}).get('emailrep', {})
        if rep and rep.get('details', {}).get('credentials_leaked'):
            recommendations.append("🔐 Credentials fuités - Vérifier la sécurité du compte")
        
        if not results.get('dns', {}).get('dns', {}).get('spf_configured'):
            recommendations.append("📧 SPF non configuré - Risque de spoofing")
        
        if not results.get('dns', {}).get('dns', {}).get('dmarc_configured'):
            recommendations.append("📧 DMARC non configuré - Renforcer la sécurité")
        
        if results.get('confidence', 0) < 50:
            recommendations.append("❓ Confiance faible - Vérifier manuellement")
        
        return recommendations
    
    def _get_username_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Recommandations pour username"""
        recommendations = []
        
        profiles_found = results.get('profiles_found', 0)
        if profiles_found > 5:
            recommendations.append(f"👤 {profiles_found} profils trouvés - Contrôler les comptes")
        
        github = [r for r in results.get('code_repositories', []) if r.get('platform') == 'github' and r.get('found')]
        if github:
            g = github[0]
            if g.get('public_repos', 0) > 0:
                recommendations.append(f"💻 Vérifier les {g['public_repos']} repos publics")
        
        if results.get('confidence', 0) > 80:
            recommendations.append("✓ Identification très probable - Informations fiables")
        
        return recommendations
    
    def _get_phone_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Recommandations pour phone"""
        recommendations = []
        
        if not results.get('carrier_info', {}).get('valid'):
            recommendations.append("❌ Numéro invalide - Vérifier le format")
        
        voip = results.get('voip_info', {})
        if voip.get('is_voip'):
            recommendations.append(f"📞 Numéro VoIP ({voip.get('voip_provider')}) - Authenticité à vérifier")
        
        brokers = results.get('data_brokers', [])
        reachable = [b for b in brokers if b.get('reachable')]
        if len(reachable) > 0:
            recommendations.append(f"🔍 {len(reachable)} agrégateurs de données contiennent ce numéro")
        
        reputation = results.get('reputation', {})
        if reputation.get('truecaller_found'):
            recommendations.append("👤 Numéro identifié sur TrueCaller")
        
        return recommendations
    
    def generate_comparison_report(self, results_list: List[Dict[str, Any]], 
                                   filepath: str = None) -> str:
        """Générer un rapport de comparaison"""
        
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = self.report_dir / f"comparison_report_{timestamp}.json"
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'report_type': 'comparison',
            'total_searches': len(results_list),
            'searches': results_list,
            'statistics': self._calculate_statistics(results_list)
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Comparison report généré: {filepath}")
        return str(filepath)
    
    def _calculate_statistics(self, results_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculer les statistiques"""
        stats = {
            'average_confidence': 0,
            'total_sources_found': 0,
            'search_types': defaultdict(int),
            'errors': 0
        }
        
        total_confidence = 0
        valid_results = 0
        
        for result in results_list:
            if 'error' not in result:
                total_confidence += result.get('confidence', 0)
                valid_results += 1
                
                # Type de recherche
                if 'email' in result:
                    stats['search_types']['email'] += 1
                elif 'username' in result:
                    stats['search_types']['username'] += 1
                elif 'phone' in result:
                    stats['search_types']['phone'] += 1
            else:
                stats['errors'] += 1
        
        if valid_results > 0:
            stats['average_confidence'] = round(total_confidence / valid_results, 1)
        
        stats['search_types'] = dict(stats['search_types'])
        
        return stats
    
    def get_all_reports(self) -> List[str]:
        """Lister tous les rapports"""
        return [str(f) for f in self.report_dir.glob('*.json')]
    
    def delete_old_reports(self, days: int = 30) -> int:
        """Supprimer les anciens rapports"""
        from datetime import datetime, timedelta
        import os
        
        cutoff_time = (datetime.now() - timedelta(days=days)).timestamp()
        deleted = 0
        
        for filepath in self.report_dir.glob('*.json'):
            if os.path.getmtime(filepath) < cutoff_time:
                os.remove(filepath)
                deleted += 1
                logger.debug(f"Rapport supprimé: {filepath}")
        
        logger.info(f"{deleted} anciens rapports supprimés")
        return deleted


class StatisticsCollector:
    """Collecte de statistiques OSINT"""
    
    def __init__(self):
        self.stats_file = Path.home() / '.raven_trace' / 'stats.json'
        self.load_stats()
    
    def load_stats(self) -> Dict[str, Any]:
        """Charger les statistiques"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        return {
            'total_searches': 0,
            'email_searches': 0,
            'phone_searches': 0,
            'username_searches': 0,
            'average_confidence': 0,
            'total_profiles_found': 0,
            'searches_with_breaches': 0
        }
    
    def save_stats(self) -> None:
        """Sauvegarder les statistiques"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def record_search(self, search_type: str, results: Dict[str, Any]) -> None:
        """Enregistrer une recherche"""
        self.stats = self.load_stats()
        
        self.stats['total_searches'] += 1
        
        if search_type == 'email':
            self.stats['email_searches'] += 1
            if results.get('breaches') and results['breaches'][0].get('status') != 'clean':
                self.stats['searches_with_breaches'] += 1
        elif search_type == 'phone':
            self.stats['phone_searches'] += 1
        elif search_type == 'username':
            self.stats['username_searches'] += 1
            self.stats['total_profiles_found'] += results.get('profiles_found', 0)
        
        # Mettre à jour la confiance moyenne
        total = self.stats['total_searches']
        old_avg = self.stats['average_confidence']
        new_confidence = results.get('confidence', 0)
        self.stats['average_confidence'] = round((old_avg * (total - 1) + new_confidence) / total, 1)
        
        self.save_stats()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Obtenir les statistiques"""
        return self.load_stats()
    
    def reset_statistics(self) -> None:
        """Réinitialiser les statistiques"""
        self.stats_file.unlink(missing_ok=True)
        logger.info("Statistiques réinitialisées")