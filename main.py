#!/usr/bin/env python3
"""
Raven Trace - OSINT Intelligence Tool
Recherche avancée par Email, Téléphone, Pseudo
CLI complète avec toutes les fonctionnalités
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# Import des modules locaux
from core.engine import SearchEngine
from cli.interface import (
    show_banner, setup_logging, show_help, show_menu,
    search_email_interactive, search_phone_interactive, 
    search_username_interactive, show_config_menu, show_history,
    show_success, show_error, show_warning, show_info,
    show_results_table, confirm_action
)
from utils.formatter import (
    format_results, create_results_table, export_html, 
    export_json, export_csv
)

console = Console()

class RavenTrace:
    def __init__(self):
        self.engine = SearchEngine(max_workers=5)
        self.logger = setup_logging()
    
    def search_email(self, email: str, deep_scan: bool = False, 
                     export_format: Optional[str] = None) -> Dict:
        """Recherche par email"""
        console.print(f"\n[bold cyan]🔍 Recherche par Email: {email}[/bold cyan]\n")
        
        try:
            results = self.engine.search_email(email, deep_scan)
            
            if 'error' in results:
                show_error(results['error'])
                return results
            
            # Affichage formaté
            output = format_results(results)
            console.print(Panel(output, title="[bold]Résultats Email[/bold]", border_style="green"))
            
            # Table de résumé
            create_results_table(results)
            
            # Export si demandé
            if export_format:
                self._export_results(results, export_format)
            
            return results
        except Exception as e:
            show_error(f"Erreur recherche email: {e}")
            return {"error": str(e)}
    
    def search_phone(self, phone: str, country: str = "FR", deep_scan: bool = False, 
                     export_format: Optional[str] = None) -> Dict:
        """Recherche par téléphone"""
        console.print(f"\n[bold cyan]📱 Recherche par Téléphone: {phone}[/bold cyan]\n")
        
        try:
            results = self.engine.search_phone(phone, country, deep_scan)
            
            if 'error' in results:
                show_error(results['error'])
                return results
            
            # Affichage formaté
            output = format_results(results)
            console.print(Panel(output, title="[bold]Résultats Téléphone[/bold]", border_style="green"))
            
            # Table de résumé
            create_results_table(results)
            
            # Export si demandé
            if export_format:
                self._export_results(results, export_format)
            
            return results
        except Exception as e:
            show_error(f"Erreur recherche phone: {e}")
            return {"error": str(e)}
    
    def search_username(self, username: str, deep_scan: bool = False, 
                       export_format: Optional[str] = None) -> Dict:
        """Recherche par pseudo"""
        console.print(f"\n[bold cyan]👤 Recherche par Pseudo: {username}[/bold cyan]\n")
        
        try:
            results = self.engine.search_username(username, deep_scan)
            
            if 'error' in results:
                show_error(results['error'])
                return results
            
            # Affichage formaté
            output = format_results(results)
            console.print(Panel(output, title="[bold]Résultats Username[/bold]", border_style="green"))
            
            # Table de résumé
            create_results_table(results)
            
            # Export si demandé
            if export_format:
                self._export_results(results, export_format)
            
            return results
        except Exception as e:
            show_error(f"Erreur recherche username: {e}")
            return {"error": str(e)}
    
    def _export_results(self, results: Dict, export_format: str) -> None:
        """Exporter les résultats"""
        try:
            export_dir = Path.home() / '.raven_trace' / 'exports'
            export_dir.mkdir(parents=True, exist_ok=True)
            
            query = results.get('email') or results.get('username') or results.get('phone', 'search')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = export_dir / f"{query}_{timestamp}.{export_format}"
            
            if export_format == 'json':
                export_json(results, str(filepath))
            elif export_format == 'csv':
                export_csv(results, str(filepath))
            elif export_format == 'html':
                export_html(results, str(filepath))
            
            show_success(f"Résultats exportés: {filepath}")
        except Exception as e:
            show_error(f"Erreur export: {e}")
    
    def interactive_mode(self) -> None:
        """Mode interactif complet"""
        while True:
            show_banner()
            show_menu()
            
            choice = click.prompt(
                "[bold cyan]Sélectionnez une option[/bold cyan]",
                type=click.Choice(['1', '2', '3', '4', '5', '6', '7', '8'])
            )
            
            if choice == '1':
                # Email
                params = search_email_interactive()
                self.search_email(
                    params['query'],
                    deep_scan=params['deep'],
                    export_format=params['export'] if params['export'] != 'none' else None
                )
            
            elif choice == '2':
                # Phone
                params = search_phone_interactive()
                self.search_phone(
                    params['query'],
                    country=params['country'],
                    deep_scan=params['deep'],
                    export_format=params['export'] if params['export'] != 'none' else None
                )
            
            elif choice == '3':
                # Username
                params = search_username_interactive()
                self.search_username(
                    params['query'],
                    deep_scan=params['deep'],
                    export_format=params['export'] if params['export'] != 'none' else None
                )
            
            elif choice == '4':
                # Recherche combinée
                query = click.prompt("[bold cyan]Entrez votre recherche[/bold cyan]")
                results = self.engine.search_combined(query)
                console.print(Panel(str(results), title="[bold]Résultats Combinés[/bold]", border_style="yellow"))
            
            elif choice == '5':
                # Historique
                show_history()
            
            elif choice == '6':
                # Configuration
                show_config_menu()
            
            elif choice == '7':
                # Aide
                show_help()
            
            elif choice == '8':
                # Quitter
                show_info("Au revoir!")
                sys.exit(0)
            
            # Pause
            click.pause()


# CLI avec Click
@click.group()
@click.version_option(version='1.0.0', prog_name='RavenTrace')
def cli():
    """🐦 RavenTrace - Advanced OSINT Intelligence Tool"""
    pass


@cli.command()
@click.argument('email')
@click.option('--deep', is_flag=True, help='Deep scan mode')
@click.option('--export', type=click.Choice(['json', 'csv', 'html']), help='Format export')
def email(email: str, deep: bool, export: Optional[str]) -> None:
    """Recherche par Email"""
    rt = RavenTrace()
    rt.search_email(email, deep, export)


@cli.command()
@click.argument('phone')
@click.option('--country', default='FR', help='Code pays (FR, US, etc)')
@click.option('--deep', is_flag=True, help='Deep scan mode')
@click.option('--export', type=click.Choice(['json', 'csv', 'html']), help='Format export')
def phone(phone: str, country: str, deep: bool, export: Optional[str]) -> None:
    """Recherche par Téléphone"""
    rt = RavenTrace()
    rt.search_phone(phone, country, deep, export)


@cli.command()
@click.argument('username')
@click.option('--deep', is_flag=True, help='Deep scan mode')
@click.option('--export', type=click.Choice(['json', 'csv', 'html']), help='Format export')
def username(username: str, deep: bool, export: Optional[str]) -> None:
    """Recherche par Pseudo"""
    rt = RavenTrace()
    rt.search_username(username, deep, export)


@cli.command()
@click.argument('query', required=False)
def interactive(query: Optional[str]) -> None:
    """Mode interactif"""
    rt = RavenTrace()
    
    if query:
        # Recherche directe en mode interactif
        results = rt.engine.search_combined(query)
        console.print(Panel(str(results), title="[bold]Résultats[/bold]", border_style="yellow"))
    else:
        # Menu interactif complet
        rt.interactive_mode()


@cli.command()
def info() -> None:
    """Afficher les informations du système"""
    from config import get_config, get_cache_config
    
    config = get_config()
    cache_config = get_cache_config()
    
    table = Table(title="🐦 RavenTrace - Information Système", show_header=True, header_style="bold magenta")
    table.add_column("Paramètre", style="cyan")
    table.add_column("Valeur", style="green")
    
    table.add_row("Version", "1.0.0")
    table.add_row("Cache Directory", str(cache_config.directory))
    table.add_row("Cache TTL", f"{cache_config.ttl_hours} heures")
    table.add_row("Log Directory", str(Path.home() / '.raven_trace' / 'logs'))
    table.add_row("Export Directory", str(Path.home() / '.raven_trace' / 'exports'))
    
    console.print(table)


@cli.command()
def clear_cache() -> None:
    """Nettoyer le cache"""
    rt = RavenTrace()
    
    if confirm_action("Êtes-vous sûr de vouloir nettoyer le cache?"):
        rt.engine.clear_cache(days=0)
        show_success("Cache nettoyé avec succès")
    else:
        show_warning("Opération annulée")


@cli.command()
def show_config() -> None:
    """Afficher la configuration"""
    from config import get_config
    
    config = get_config()
    
    table = Table(title="⚙️  Configuration RavenTrace", show_header=True, header_style="bold magenta")
    table.add_column("Clé", style="cyan")
    table.add_column("Valeur", style="green")
    
    for key, value in config.to_dict().items():
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                table.add_row(f"{key}.{subkey}", str(subvalue))
        else:
            table.add_row(key, str(value))
    
    console.print(table)


@cli.command()
@click.argument('email')
@click.argument('username')
@click.argument('phone', required=False)
def batch(email: str, username: str, phone: Optional[str]) -> None:
    """Recherche par batch"""
    rt = RavenTrace()
    
    results = {
        'email': rt.search_email(email) if email else None,
        'username': rt.search_username(username) if username else None,
        'phone': rt.search_phone(phone) if phone else None,
    }
    
    # Export résultats
    export_dir = Path.home() / '.raven_trace' / 'exports'
    export_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = export_dir / f"batch_search_{timestamp}.json"
    
    export_json(results, str(filepath))
    show_success(f"Recherche batch exportée: {filepath}")


@cli.command()
def version() -> None:
    """Afficher la version"""
    console.print("[bold cyan]🐦 RavenTrace v2.0.1[/bold cyan]")
    console.print("[yellow]Advanced OSINT Intelligence Tool[/yellow]")
    console.print("[dim]© 2025 - Samy Nyx[/dim]")


@cli.command()
def help_cmd() -> None:
    """Afficher l'aide complète"""
    show_help()


if __name__ == '__main__':
    cli()