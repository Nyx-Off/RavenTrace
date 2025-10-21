#!/usr/bin/env python3
"""
Raven Trace - OSINT Intelligence Tool
Recherche avancée par Email, Téléphone, Pseudo
"""

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys
from pathlib import Path

# Import des modules locaux
from raven_trace.core.engine import SearchEngine
from raven_trace.cli.interface import show_banner, setup_logging
from raven_trace.utils.formatter import format_results

console = Console()

class RavenTrace:
    def __init__(self):
        self.engine = SearchEngine()
        setup_logging()
    
    def search_email(self, email, deep_scan=False):
        """Recherche par email"""
        console.print(f"\n[bold cyan]🔍 Recherche par Email: {email}[/bold cyan]")
        results = self.engine.search_email(email, deep_scan)
        self._display_results(results, "EMAIL")
        return results
    
    def search_phone(self, phone, country=None, deep_scan=False):
        """Recherche par numéro de téléphone"""
        console.print(f"\n[bold cyan]📱 Recherche par Téléphone: {phone}[/bold cyan]")
        results = self.engine.search_phone(phone, country, deep_scan)
        self._display_results(results, "PHONE")
        return results
    
    def search_username(self, username, deep_scan=False):
        """Recherche par pseudo"""
        console.print(f"\n[bold cyan]👤 Recherche par Pseudo: {username}[/bold cyan]")
        results = self.engine.search_username(username, deep_scan)
        self._display_results(results, "USERNAME")
        return results
    
    def _display_results(self, results, search_type):
        """Affiche les résultats formatés"""
        if not results:
            console.print("[yellow]❌ Aucun résultat trouvé[/yellow]")
            return
        
        console.print(Panel(
            format_results(results),
            title=f"[bold]Résultats {search_type}[/bold]",
            border_style="green"
        ))

@click.group()
@click.version_option(version='1.0.0')
def cli():
    """Raven Trace - OSINT Intelligence Tool"""
    show_banner()

@cli.command()
@click.argument('email')
@click.option('--deep', is_flag=True, help='Deep scan mode')
def email(email, deep):
    """Recherche par Email"""
    rt = RavenTrace()
    rt.search_email(email, deep)

@cli.command()
@click.argument('phone')
@click.option('--country', default=None, help='Code pays (FR, US, etc)')
@click.option('--deep', is_flag=True, help='Deep scan mode')
def phone(phone, country, deep):
    """Recherche par Téléphone"""
    rt = RavenTrace()
    rt.search_phone(phone, country, deep)

@cli.command()
@click.argument('username')
@click.option('--deep', is_flag=True, help='Deep scan mode')
def username(username, deep):
    """Recherche par Pseudo"""
    rt = RavenTrace()
    rt.search_username(username, deep)

@cli.command()
@click.option('--query', prompt='Votre recherche', help='Recherche combinée')
def interactive(query):
    """Mode interactif avancé"""
    rt = RavenTrace()
    console.print("[bold magenta]Mode Interactif Activé[/bold magenta]")
    # TODO: Implémenter recherche intelligente

if __name__ == '__main__':
    cli()