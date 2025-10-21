#!/usr/bin/env python3
"""
Formatter - Formatage avancé des résultats
Version complète avec tous les exports
"""

import logging
import sys
import json
import csv
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from typing import Dict, Any, List
from datetime import datetime

console = Console()

def setup_logging(log_level=logging.DEBUG):
    """Configurer le logging avec fichier et console"""
    
    log_dir = Path.home() / '.raven_trace' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = log_dir / 'raven_trace.log'
    
    log_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Handler fichier
    from logging.handlers import RotatingFileHandler
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10485760,
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(log_format)
    root_logger.addHandler(file_handler)
    
    # Handler console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_format)
    root_logger.addHandler(console_handler)
    
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return root_logger

def format_results(results: Dict[str, Any]) -> str:
    """Formater les résultats selon le type"""
    if 'email' in results:
        return format_email_results(results)
    elif 'username' in results:
        return format_username_results(results)
    elif 'phone' in results:
        return format_phone_results(results)
    return "[yellow]Format non reconnu[/yellow]"

def format_email_results(results: Dict[str, Any]) -> str:
    """Formater les résultats d'email"""
    
    if 'error' in results:
        return f"[bold red]❌ Erreur: {results['error']}[/bold red]"
    
    output = ""
    output += f"\n[bold cyan]📧 Email: {results.get('email', 'N/A')}[/bold cyan]\n"
    
    if 'confidence' in results:
        confidence = results['confidence']
        bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        output += f"[cyan]Confiance: [{bar}] {confidence}%[/cyan]\n\n"
    
    rep = results.get('reputation', {}).get('emailrep', {})
    if rep:
        output += "[bold]🔍 Réputation (EmailRep.io):[/bold]\n"
        output += f"  • Score: {rep.get('reputation', 'N/A')}\n"
        output += f"  • Références: {rep.get('references', 0)}\n"
        if rep.get('details'):
            output += f"  • Domaine valide: {rep['details'].get('domain_exists', False)}\n"
            output += f"  • Blacklisté: {rep['details'].get('blacklisted', False)}\n"
            output += f"  • Credentials fuités: {rep['details'].get('credentials_leaked', False)}\n"
        output += "\n"
    
    dns = results.get('dns', {}).get('dns', {})
    if dns:
        output += "[bold]🔐 Configuration DNS:[/bold]\n"
        output += f"  • Domaine: {dns.get('domain', 'N/A')}\n"
        output += f"  • MX Records: {len(dns.get('mx_records', []))} trouvés\n"
        output += f"  • SPF Configuré: {'✓' if dns.get('spf_configured') else '✗'}\n"
        output += f"  • DMARC Configuré: {'✓' if dns.get('dmarc_configured') else '✗'}\n"
        output += f"  • Domaine Valide: {'✓' if dns.get('valid_domain') else '✗'}\n"
        output += "\n"
    
    breaches = results.get('breaches', [])
    if breaches:
        if breaches[0].get('status') != 'clean':
            output += "[bold red]⚠️  FUITES DE DONNÉES DÉTECTÉES:[/bold red]\n"
            for breach in breaches:
                if breach.get('breach_name'):
                    severity = breach.get('severity', 'CRITIQUE')
                    output += f"  • [red]{breach['breach_name']}[/red] ({breach.get('date', 'N/A')}) - {severity}\n"
                    if breach.get('data_classes'):
                        classes = ', '.join(breach['data_classes'][:3])
                        output += f"    Types: {classes}\n"
        else:
            output += "[bold green]✓ Aucune fuite de données détectée[/bold green]\n"
        output += "\n"
    
    profiles = results.get('social_profiles', [])
    if profiles:
        output += "[bold]👥 Profils Sociaux Trouvés:[/bold]\n"
        for profile in profiles:
            output += f"  • {profile.get('platform', 'N/A')}\n"
        output += "\n"
    
    domain = results.get('domain', {})
    if domain and domain.get('registered'):
        output += "[bold]🌐 Domaine:[/bold]\n"
        output += f"  • Enregistré: ✓\n"
        output += f"  • Vérification: {domain.get('whois_url', 'N/A')}\n"
    
    return output

def format_username_results(results: Dict[str, Any]) -> str:
    """Formater les résultats d'username"""
    
    if 'error' in results:
        return f"[bold red]❌ Erreur: {results['error']}[/bold red]"
    
    output = ""
    output += f"\n[bold cyan]👤 Username: {results.get('username', 'N/A')}[/bold cyan]\n"
    
    if 'confidence' in results:
        confidence = results['confidence']
        bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        output += f"[cyan]Confiance: [{bar}] {confidence}%[/cyan]\n"
    
    if 'profiles_found' in results:
        output += f"[bold yellow]Profils trouvés: {results['profiles_found']}[/bold yellow]\n\n"
    
    social = results.get('social_media', [])
    found_social = [p for p in social if p.get('found')]
    if found_social:
        output += "[bold]📱 Réseaux Sociaux:[/bold]\n"
        for profile in found_social:
            output += f"  [green]✓ {profile.get('platform')}[/green]: {profile.get('url', 'N/A')}\n"
        output += "\n"
    
    code_repos = results.get('code_repositories', [])
    
    github = [r for r in code_repos if r.get('platform') == 'github' and r.get('found')]
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
    
    reddit = [r for r in code_repos if r.get('platform') == 'reddit' and r.get('found')]
    if reddit:
        r = reddit[0]
        output += "[bold]🔴 Reddit:[/bold]\n"
        output += f"  • Nom: {r.get('display_name', 'N/A')}\n"
        output += f"  • Link Karma: {r.get('link_karma', 0)}\n"
        output += f"  • Comment Karma: {r.get('comment_karma', 0)}\n"
        output += f"  • Gold: {'✓' if r.get('is_gold') else '✗'}\n"
        output += "\n"
    
    forums = results.get('forums', [])
    found_forums = [f for f in forums if f.get('found')]
    if found_forums:
        output += "[bold]📝 Forums:[/bold]\n"
        for forum in found_forums:
            output += f"  • {forum.get('platform', 'N/A')}\n"
        output += "\n"
    
    return output

def format_phone_results(results: Dict[str, Any]) -> str:
    """Formater les résultats de téléphone"""
    
    if 'error' in results:
        return f"[bold red]❌ Erreur: {results['error']}[/bold red]"
    
    output = ""
    output += f"\n[bold cyan]📱 Téléphone: {results.get('phone', 'N/A')}[/bold cyan]\n"
    
    carrier = results.get('carrier_info', {})
    if carrier:
        output += "[bold]📡 Opérateur:[/bold]\n"
        output += f"  • Opérateur: {carrier.get('carrier', 'N/A')}\n"
        output += f"  • Pays: {carrier.get('country', 'N/A')}\n"
        output += f"  • Région: {carrier.get('region', 'N/A')}\n"
        output += f"  • Type: {carrier.get('type', 'N/A')}\n"
        output += f"  • Valide: {'✓' if carrier.get('valid') else '✗'}\n"
        output += "\n"
    
    location = results.get('location', {})
    if location:
        output += "[bold]📍 Localisation:[/bold]\n"
        output += f"  • Location: {location.get('location', 'N/A')}\n"
        output += f"  • Pays: {location.get('country_code', 'N/A')}\n"
        output += "\n"
    
    reputation = results.get('reputation', {})
    if reputation:
        output += "[bold]⭐ Réputation:[/bold]\n"
        output += f"  • TrueCaller: {'Trouvé ✓' if reputation.get('truecaller_found') else 'Non trouvé'}\n"
        output += f"  • Reverse Phone: {'Trouvé ✓' if reputation.get('reverse_phone_found') else 'Non trouvé'}\n"
        output += "\n"
    
    brokers = results.get('data_brokers', [])
    if brokers:
        output += "[bold]🔍 Agrégateurs de Données:[/bold]\n"
        for broker in brokers:
            output += f"  • {broker.get('platform', 'N/A')}\n"
    
    return output

def create_results_table(results: Dict[str, Any]) -> None:
    """Créer et afficher une table de résultats"""
    if 'email' in results:
        create_email_table(results)
    elif 'username' in results:
        create_username_table(results)
    elif 'phone' in results:
        create_phone_table(results)

def create_email_table(results: Dict[str, Any]) -> None:
    """Table pour email"""
    table = Table(title="Résultats Email OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Catégorie", style="cyan", width=20)
    table.add_column("Information", style="green")
    
    rep = results.get('reputation', {}).get('emailrep', {})
    if rep:
        table.add_row("Réputation", f"Score: {rep.get('reputation', 'N/A')}")
    
    dns = results.get('dns', {}).get('dns', {})
    if dns:
        spf = '✓' if dns.get('spf_configured') else '✗'
        dmarc = '✓' if dns.get('dmarc_configured') else '✗'
        table.add_row("DNS", f"MX: {len(dns.get('mx_records', []))} | SPF: {spf} | DMARC: {dmarc}")
    
    breaches = results.get('breaches', [])
    if breaches and breaches[0].get('status') != 'clean':
        table.add_row("Fuites", f"⚠️  {len(breaches)} fuite(s)")
    else:
        table.add_row("Fuites", "✓ Aucune")
    
    profiles = results.get('social_profiles', [])
    table.add_row("Profils Sociaux", f"{len(profiles)} trouvé(s)")
    
    if 'confidence' in results:
        table.add_row("Confiance", f"{results['confidence']}%")
    
    console.print(table)

def create_username_table(results: Dict[str, Any]) -> None:
    """Table pour username"""
    table = Table(title="Résultats Username OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Plateforme", style="cyan", width=20)
    table.add_column("Statut", style="green")
    
    social = results.get('social_media', [])
    for platform in social:
        status = "✓ Trouvé" if platform.get('found') else "✗ Non trouvé"
        table.add_row(platform.get('platform', 'N/A'), status)
    
    code_repos = results.get('code_repositories', [])
    for repo in code_repos:
        status = "✓ Trouvé" if repo.get('found') else "✗ Non trouvé"
        table.add_row(repo.get('platform', 'N/A'), status)
    
    if 'confidence' in results:
        table.add_row("Confiance", f"{results['confidence']}%")
    
    console.print(table)

def create_phone_table(results: Dict[str, Any]) -> None:
    """Table pour phone"""
    table = Table(title="Résultats Phone OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Information", style="cyan", width=20)
    table.add_column("Valeur", style="green")
    
    carrier = results.get('carrier_info', {})
    if carrier:
        table.add_row("Opérateur", carrier.get('carrier', 'N/A'))
        table.add_row("Pays", carrier.get('country', 'N/A'))
        table.add_row("Région", carrier.get('region', 'N/A'))
    
    location = results.get('location', {})
    if location:
        table.add_row("Location", location.get('location', 'N/A'))
    
    console.print(table)

def export_json(results: Dict[str, Any], filepath: str) -> None:
    """Exporter en JSON"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        console.print(f"[green]✓ Résultats exportés: {filepath}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Erreur export JSON: {e}[/red]")

def export_csv(results: Dict[str, Any], filepath: str) -> None:
    """Exporter en CSV"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
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
    except Exception as e:
        console.print(f"[red]❌ Erreur export CSV: {e}[/red]")

def export_html(results: Dict[str, Any], filepath: str) -> None:
    """Exporter en HTML"""
    try:
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        html = generate_html_report(results)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        
        console.print(f"[green]✓ Rapport HTML généré: {filepath}[/green]")
    except Exception as e:
        console.print(f"[red]❌ Erreur export HTML: {e}[/red]")

def generate_html_report(results: Dict[str, Any]) -> str:
    """Générer un rapport HTML"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    query_type = "Email" if 'email' in results else "Username" if 'username' in results else "Phone"
    query_value = results.get('email') or results.get('username') or results.get('phone')
    
    html = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Rapport OSINT - RavenTrace</title>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
            .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
            .header p {{ font-size: 1.1em; opacity: 0.9; }}
            .info-box {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
            .info-box h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.5em; }}
            .info-row {{ display: flex; padding: 10px 0; border-bottom: 1px solid #eee; }}
            .info-row:last-child {{ border-bottom: none; }}
            .info-label {{ font-weight: 600; width: 200px; color: #555; }}
            .info-value {{ flex: 1; color: #333; }}
            .status-good {{ color: #4caf50; font-weight: 600; }}
            .status-warning {{ color: #ff9800; font-weight: 600; }}
            .status-danger {{ color: #f44336; font-weight: 600; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
            table th {{ background: #f5f5f5; padding: 12px; text-align: left; border-bottom: 2px solid #667eea; }}
            table td {{ padding: 12px; border-bottom: 1px solid #eee; }}
            .footer {{ text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #eee; color: #999; }}
            .confidence-bar {{ width: 100%; height: 20px; background: #eee; border-radius: 10px; overflow: hidden; }}
            .confidence-fill {{ height: 100%; background: linear-gradient(90deg, #4caf50, #8bc34a); }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🐦 RavenTrace - Rapport OSINT</h1>
                <p>Recherche: <strong>{query_type}</strong> - {query_value}</p>
                <p>Généré le: {timestamp}</p>
            </div>
    """
    
    if 'email' in results:
        html += generate_email_html(results)
    elif 'username' in results:
        html += generate_username_html(results)
    elif 'phone' in results:
        html += generate_phone_html(results)
    
    html += """
            <div class="footer">
                <p>Rapport généré par RavenTrace v1.0</p>
                <p>⚠️  Usage légal et éthique uniquement</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html

def generate_email_html(results: Dict[str, Any]) -> str:
    """Générer la partie HTML pour email"""
    html = ""
    
    confidence = results.get('confidence', 0)
    html += f"""
        <div class="info-box">
            <h2>📊 Score de Confiance</h2>
            <div class="info-row">
                <div class="info-label">Confiance</div>
                <div class="info-value">
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {confidence}%;"></div>
                    </div>
                    {confidence}%
                </div>
            </div>
        </div>
    """
    
    rep = results.get('reputation', {}).get('emailrep', {})
    if rep:
        html += """
        <div class="info-box">
            <h2>🔍 Réputation</h2>
        """
        html += f"<div class='info-row'><div class='info-label'>Score</div><div class='info-value'>{rep.get('reputation', 'N/A')}</div></div>"
        html += f"<div class='info-row'><div class='info-label'>Références</div><div class='info-value'>{rep.get('references', 0)}</div></div>"
        
        if rep.get('details'):
            blacklisted = rep['details'].get('blacklisted', False)
            status_class = 'status-danger' if blacklisted else 'status-good'
            html += f"<div class='info-row'><div class='info-label'>Blacklisté</div><div class='info-value {status_class}'>{'❌ Oui' if blacklisted else '✓ Non'}</div></div>"
        
        html += "</div>"
    
    breaches = results.get('breaches', [])
    if breaches:
        html += """
        <div class="info-box">
            <h2>⚠️  Fuites de Données</h2>
        """
        if breaches[0].get('status') == 'clean':
            html += "<div class='info-row'><div class='info-value status-good'>✓ Aucune fuite détectée</div></div>"
        else:
            html += """
            <table>
                <thead>
                    <tr>
                        <th>Nom</th>
                        <th>Date</th>
                        <th>Sévérité</th>
                    </tr>
                </thead>
                <tbody>
            """
            for breach in breaches:
                if breach.get('breach_name'):
                    html += f"""
                    <tr>
                        <td>{breach.get('breach_name', 'N/A')}</td>
                        <td>{breach.get('date', 'N/A')}</td>
                        <td><span class="status-danger">{breach.get('severity', 'CRITIQUE')}</span></td>
                    </tr>
                    """
            html += "</tbody></table>"
        
        html += "</div>"
    
    return html

def generate_username_html(results: Dict[str, Any]) -> str:
    """Générer la partie HTML pour username"""
    html = ""
    
    profiles_found = results.get('profiles_found', 0)
    html += f"""
        <div class="info-box">
            <h2>👤 Résumé</h2>
            <div class="info-row">
                <div class="info-label">Profils trouvés</div>
                <div class="info-value"><strong>{profiles_found}</strong></div>
            </div>
        </div>
    """
    
    social = results.get('social_media', [])
    found_social = [p for p in social if p.get('found')]
    
    if found_social:
        html += """
        <div class="info-box">
            <h2>📱 Réseaux Sociaux</h2>
            <table>
                <thead>
                    <tr>
                        <th>Plateforme</th>
                        <th>URL</th>
                    </tr>
                </thead>
                <tbody>
        """
        for profile in found_social:
            html += f"""
            <tr>
                <td><strong>{profile.get('platform', 'N/A')}</strong></td>
                <td><a href="{profile.get('url')}" target="_blank">{profile.get('url', 'N/A')}</a></td>
            </tr>
            """
        html += "</tbody></table></div>"
    
    return html

def generate_phone_html(results: Dict[str, Any]) -> str:
    """Générer la partie HTML pour phone"""
    html = ""
    
    carrier = results.get('carrier_info', {})
    if carrier:
        html += """
        <div class="info-box">
            <h2>📡 Informations Opérateur</h2>
        """
        html += f"<div class='info-row'><div class='info-label'>Opérateur</div><div class='info-value'>{carrier.get('carrier', 'N/A')}</div></div>"
        html += f"<div class='info-row'><div class='info-label'>Pays</div><div class='info-value'>{carrier.get('country', 'N/A')}</div></div>"
        html += f"<div class='info-row'><div class='info-label'>Région</div><div class='info-value'>{carrier.get('region', 'N/A')}</div></div>"
        html += "</div>"
    
    return html