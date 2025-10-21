#!/usr/bin/env python3
"""
Formatter - Formatage avancé des résultats
"""

import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import Dict, Any
import json

console = Console()

def setup_logging():
    """Configurer le logging"""
    log_dir = Path.home() / '.raven_trace' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'raven_trace.log'
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

def format_email_results(results: Dict[str, Any]) -> str:
    """Formater les résultats d'email pour affichage"""
    
    if 'error' in results:
        return f"[bold red]❌ Erreur: {results['error']}[/bold red]"
    
    output = ""
    output += f"\n[bold cyan]📧 Email: {results['email']}[/bold cyan]\n"
    
    # Confiance
    if 'confidence' in results:
        confidence = results['confidence']
        bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        output += f"[cyan]Confiance: [{bar}] {confidence}%[/cyan]\n\n"
    
    # Réputation
    if results.get('reputation'):
        output += "[bold]🔍 Réputation (EmailRep.io):[/bold]\n"
        rep = results['reputation'].get('emailrep', {})
        if rep:
            output += f"  • Score: {rep.get('reputation', 'N/A')}\n"
            output += f"  • Références: {rep.get('references', 0)}\n"
            if rep.get('details'):
                output += f"  • Domaine valide: {rep['details'].get('domain_exists', False)}\n"
                output += f"  • Blacklisté: {rep['details'].get('blacklisted', False)}\n"
        output += "\n"
    
    # DNS
    if results.get('dns'):
        dns = results['dns'].get('dns', {})
        if dns:
            output += "[bold]🔐 Configuration DNS:[/bold]\n"
            output += f"  • Domaine: {dns.get('domain', 'N/A')}\n"
            output += f"  • MX Records: {len(dns.get('mx_records', []))} trouvés\n"
            output += f"  • SPF Configuré: {'✓' if dns.get('spf_configured') else '✗'}\n"
            output += f"  • DMARC Configuré: {'✓' if dns.get('dmarc_configured') else '✗'}\n"
            output += f"  • Domaine Valide: {'✓' if dns.get('valid_domain') else '✗'}\n"
        output += "\n"
    
    # Fuites
    if results.get('breaches'):
        breaches = results['breaches']
        if breaches and breaches[0].get('status') != 'clean':
            output += "[bold red]⚠️  FUITES DE DONNÉES DÉTECTÉES:[/bold red]\n"
            for breach in breaches:
                if breach.get('breach_name'):
                    severity = breach.get('severity', 'CRITIQUE')
                    output += f"  • [red]{breach['breach_name']}[/red] ({breach.get('date', 'N/A')}) - {severity}\n"
                    if breach.get('data_classes'):
                        output += f"    Types: {', '.join(breach['data_classes'][:3])}\n"
        else:
            output += "[bold green]✓ Aucune fuite de données détectée (EmailRep.io)[/bold green]\n"
        output += "\n"
    
    # Profils sociaux
    if results.get('social_profiles'):
        social = results['social_profiles']
        if social:
            output += "[bold]👥 Profils Sociaux:[/bold]\n"
            for profile in social:
                output += f"  • {profile.get('platform', 'N/A')}\n"
        output += "\n"
    
    return output

def format_username_results(results: Dict[str, Any]) -> str:
    """Formater les résultats d'username pour affichage"""
    
    if 'error' in results:
        return f"[bold red]❌ Erreur: {results['error']}[/bold red]"
    
    output = ""
    output += f"\n[bold cyan]👤 Username: {results['username']}[/bold cyan]\n"
    
    # Confiance
    if 'confidence' in results:
        confidence = results['confidence']
        bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        output += f"[cyan]Confiance: [{bar}] {confidence}%[/cyan]\n"
    
    # Profils trouvés
    if 'profiles_found' in results:
        output += f"[bold]Profils trouvés: {results['profiles_found']}[/bold]\n\n"
    
    # Réseaux sociaux
    if results.get('social_media'):
        found = [p for p in results['social_media'] if p.get('found')]
        if found:
            output += "[bold]📱 Réseaux Sociaux:[/bold]\n"
            for profile in found:
                output += f"  [green]✓ {profile.get('platform')}[/green]: {profile.get('url', 'N/A')}\n"
            output += "\n"
    
    # GitHub
    if results.get('code_repositories'):
        github = [r for r in results['code_repositories'] if r.get('platform') == 'github']
        if github:
            g = github[0]
            output += "[bold]💻 GitHub:[/bold]\n"
            output += f"  • Nom: {g.get('name', 'N/A')}\n"
            output += f"  • Bio: {g.get('bio', 'N/A')}\n"
            output += f"  • Followers: {g.get('followers', 0)}\n"
            output += f"  • Repos publics: {g.get('public_repos', 0)}\n"
            if g.get('company'):
                output += f"  • Entreprise: {g['company']}\n"
            if g.get('location'):
                output += f"  • Location: {g['location']}\n"
            output += "\n"
    
    # Reddit
    if results.get('code_repositories'):
        reddit = [r for r in results['code_repositories'] if r.get('platform') == 'reddit']
        if reddit:
            r = reddit[0]
            output += "[bold]🔴 Reddit:[/bold]\n"
            output += f"  • Nom: {r.get('display_name', 'N/A')}\n"
            output += f"  • Link Karma: {r.get('link_karma', 0)}\n"
            output += f"  • Comment Karma: {r.get('comment_karma', 0)}\n"
            output += f"  • Gold: {'✓' if r.get('is_gold') else '✗'}\n"
            output += f"  • Modérateur: {'✓' if r.get('is_mod') else '✗'}\n"
            output += "\n"
    
    # Forums
    if results.get('forums'):
        found = [f for f in results['forums'] if f.get('found')]
        if found:
            output += "[bold]📝 Forums:[/bold]\n"
            for forum in found:
                output += f"  • {forum.get('platform', 'N/A')}\n"
            output += "\n"
    
    return output

def display_results_table(results: Dict[str, Any]) -> None:
    """Afficher les résultats en table formatée"""
    
    if 'email' in results:
        display_results_email_table(results)
    elif 'username' in results:
        display_results_username_table(results)

def display_results_email_table(results: Dict[str, Any]) -> None:
    """Table pour email"""
    table = Table(title="Résultats Email OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Catégorie", style="cyan")
    table.add_column("Information", style="green")
    
    # Réputation
    rep = results.get('reputation', {}).get('emailrep', {})
    if rep:
        table.add_row("Réputation", f"Score: {rep.get('reputation', 'N/A')}")
    
    # DNS
    dns = results.get('dns', {}).get('dns', {})
    if dns:
        table.add_row("DNS", f"MX: {len(dns.get('mx_records', []))} | SPF: {'✓' if dns.get('spf_configured') else '✗'}")
    
    # Fuites
    breaches = results.get('breaches', [])
    if breaches and breaches[0].get('status') != 'clean':
        table.add_row("Fuites", f"⚠️  {len(breaches)} fuite(s) détectée(s)")
    else:
        table.add_row("Fuites", "✓ Aucune")
    
    # Profils
    profiles = results.get('social_profiles', [])
    table.add_row("Profils Sociaux", f"{len(profiles)} trouvé(s)")
    
    console.print(table)

def display_results_username_table(results: Dict[str, Any]) -> None:
    """Table pour username"""
    table = Table(title="Résultats Username OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Plateforme", style="cyan")
    table.add_column("Statut", style="green")
    
    # Réseaux sociaux
    for platform in results.get('social_media', []):
        status = "✓ Trouvé" if platform.get('found') else "✗"
        table.add_row(platform.get('platform', 'N/A'), status)
    
    console.print(table)

def export_json(results: Dict[str, Any], filepath: str) -> None:
    """Exporter en JSON"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    console.print(f"[green]✓ Résultats exportés: {filepath}[/green]")

def export_csv(results: Dict[str, Any], filepath: str) -> None:
    """Exporter en CSV"""
    import csv
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Clé', 'Valeur'])
        
        def flatten(d, parent_key=''):
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    yield from flatten(v, new_key)
                elif isinstance(v, list):
                    yield (new_key, json.dumps(v))
                else:
                    yield (new_key, str(v))
        
        for key, value in flatten(results):
            writer.writerow([key, value])
    
    console.print(f"[green]✓ Résultats exportés: {filepath}[/green]")