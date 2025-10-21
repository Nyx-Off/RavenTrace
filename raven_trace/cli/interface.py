#!/usr/bin/env python3
"""
CLI Interface - Interface en ligne de commande avec Rich
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.progress import track
from rich.table import Table
import time

console = Console()

def show_banner():
    """Afficher le banner du programme"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║                  🐦 RAVEN TRACE v1.0 🐦                     ║
    ║                                                              ║
    ║              Advanced OSINT Intelligence Tool                ║
    ║                                                              ║
    ║          Email | Phone | Username Reconnaissance             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    [bold cyan]Documentation:[/bold cyan] https://github.com/raven-trace
    [bold yellow]⚠️  Usage légal et éthique uniquement[/bold yellow]
    """
    
    console.print(Panel(banner, border_style="magenta", expand=False))

def setup_logging():
    """Configurer le logging"""
    from raven_trace.utils.logger import setup_logging as _setup
    return _setup()

def show_menu():
    """Afficher le menu principal"""
    menu = """
    [bold cyan]┌─ MENU PRINCIPAL ─┐[/bold cyan]
    
    [1] 🔍 Recherche par Email
    [2] 📱 Recherche par Téléphone
    [3] 👤 Recherche par Pseudo
    [4] 🔗 Recherche Combinée
    [5] 📊 Historique Recherches
    [6] ⚙️  Configuration
    [7] 🆘 Aide
    [8] ❌ Quitter
    """
    console.print(menu)

def get_search_mode():
    """Demander le mode de recherche"""
    show_banner()
    show_menu()
    
    choice = Prompt.ask(
        "[bold cyan]Sélectionnez une option[/bold cyan]",
        choices=["1", "2", "3", "4", "5", "6", "7", "8"]
    )
    
    return choice

def search_email_interactive():
    """Recherche email interactive"""
    console.print("\n[bold cyan]📧 Recherche par Email[/bold cyan]")
    
    email = Prompt.ask("Entrez l'email")
    
    deep = Prompt.ask(
        "Mode deep scan?",
        choices=["y", "n"],
        default="n"
    ) == "y"
    
    export_format = Prompt.ask(
        "Format export",
        choices=["none", "json", "csv"],
        default="none"
    )
    
    return {
        'query': email,
        'deep': deep,
        'export': export_format,
        'type': 'email'
    }

def search_phone_interactive():
    """Recherche téléphone interactive"""
    console.print("\n[bold cyan]📱 Recherche par Téléphone[/bold cyan]")
    
    phone = Prompt.ask("Entrez le numéro (ex: +33612345678)")
    country = Prompt.ask(
        "Code pays",
        default="FR"
    )
    
    deep = Prompt.ask(
        "Mode deep scan?",
        choices=["y", "n"],
        default="n"
    ) == "y"
    
    export_format = Prompt.ask(
        "Format export",
        choices=["none", "json", "csv"],
        default="none"
    )
    
    return {
        'query': phone,
        'country': country,
        'deep': deep,
        'export': export_format,
        'type': 'phone'
    }

def search_username_interactive():
    """Recherche username interactive"""
    console.print("\n[bold cyan]👤 Recherche par Pseudo[/bold cyan]")
    
    username = Prompt.ask("Entrez le pseudo")
    
    deep = Prompt.ask(
        "Mode deep scan?",
        choices=["y", "n"],
        default="n"
    ) == "y"
    
    export_format = Prompt.ask(
        "Format export",
        choices=["none", "json", "csv"],
        default="none"
    )
    
    return {
        'query': username,
        'deep': deep,
        'export': export_format,
        'type': 'username'
    }

def show_search_progress():
    """Afficher la progression de recherche"""
    steps = [
        "Validation input",
        "Cache lookup",
        "Recherche sources",
        "Agrégation données",
        "Analyse résultats",
        "Formatage résultats"
    ]
    
    for step in track(steps, description="[cyan]Recherche en cours..."):
        time.sleep(0.3)

def show_config_menu():
    """Menu de configuration"""
    console.print("\n[bold cyan]⚙️  CONFIGURATION[/bold cyan]\n")
    
    table = Table(title="Paramètres Actuels")
    table.add_column("Paramètre", style="cyan")
    table.add_column("Valeur", style="green")
    
    table.add_row("Cache TTL", "24 heures")
    table.add_row("Timeout Requêtes", "10 secondes")
    table.add_row("Workers Parallèles", "5")
    table.add_row("Deep Scan Défaut", "Non")
    table.add_row("User Agent Rotation", "Oui")
    
    console.print(table)

def show_history():
    """Afficher l'historique des recherches"""
    from raven_trace.storage.database import CacheDB
    
    console.print("\n[bold cyan]📊 HISTORIQUE[/bold cyan]\n")
    
    # Lire depuis le cache
    cache = CacheDB()
    
    console.print("[yellow]Fonctionnalité en développement[/yellow]")

def show_help():
    """Afficher l'aide"""
    help_text = """
    [bold cyan]╔═══════════════════════════════════════════════════════════════╗[/bold cyan]
    [bold cyan]║                    AIDE - RAVEN TRACE                         ║[/bold cyan]
    [bold cyan]╚═══════════════════════════════════════════════════════════════╝[/bold cyan]
    
    [bold]COMMANDES PRINCIPALES:[/bold]
    
    1️⃣  EMAIL LOOKUP
        • Recherche complète par adresse email
        • Vérification réputation
        • DNS records
        • Fuites de données (HIBP)
        • Profils sociaux associés
    
    2️⃣  PHONE LOOKUP
        • Identification opérateur
        • Géolocalisation
        • Vérification réputation
        • Recherche profils
        • Agrégateurs de données
    
    3️⃣  USERNAME LOOKUP
        • Recherche sur réseaux sociaux
        • Forums et communautés
        • GitHub/GitLab
        • Plateformes gaming
        • Agrégateurs OSINT
    
    [bold yellow]⚠️  AVERTISSEMENTS LÉGAUX:[/bold yellow]
    • Usage personnel et légal uniquement
    • Respect de la vie privée
    • Conformité RGPD
    • Pas de scraping agressif
    • Vérifier les ToS des sources
    
    [bold]OPTIONS AVANCÉES:[/bold]
    • --deep : Deep scan (toutes les sources)
    • --export json : Exporter en JSON
    • --export csv : Exporter en CSV
    • --cache-clear : Nettoyer le cache
    
    [bold]EXEMPLES:[/bold]
    
    $ raven-trace email user@example.com
    $ raven-trace email user@example.com --deep
    $ raven-trace phone +33612345678 --export json
    $ raven-trace username john_doe --deep
    
    [bold cyan]Pour plus d'info: https://github.com/raven-trace[/bold cyan]
    """
    
    console.print(help_text)

def show_results_table(results):
    """Afficher les résultats en table"""
    table = Table(title="Résultats OSINT", show_header=True, header_style="bold magenta")
    table.add_column("Source", style="cyan")
    table.add_column("Données", style="green")
    
    sources = results.get('sources', {})
    for source, data in sources.items():
        if isinstance(data, dict) and len(data) > 0:
            table.add_row(source, f"✓ Trouvé")
        elif isinstance(data, list) and len(data) > 0:
            table.add_row(source, f"✓ {len(data)} résultats")
        else:
            table.add_row(source, "✗ Aucun résultat")
    
    console.print(table)

def confirm_action(message: str) -> bool:
    """Demander une confirmation"""
    response = Prompt.ask(
        f"[bold yellow]{message}[/bold yellow]",
        choices=["y", "n"],
        default="n"
    )
    return response == "y"

def show_error(message: str):
    """Afficher une erreur"""
    console.print(f"[bold red]❌ Erreur: {message}[/bold red]")

def show_success(message: str):
    """Afficher un succès"""
    console.print(f"[bold green]✓ {message}[/bold green]")

def show_warning(message: str):
    """Afficher un avertissement"""
    console.print(f"[bold yellow]⚠️  {message}[/bold yellow]")

def show_info(message: str):
    """Afficher une info"""
    console.print(f"[bold cyan]ℹ️  {message}[/bold cyan]")