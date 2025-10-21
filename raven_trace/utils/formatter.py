#!/usr/bin/env python3
"""
Utilities - Formatting et Logging
"""

import logging
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from typing import Dict, Any

console = Console()

# ============ LOGGER ============

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
    
    # Réduire le bruit des libs externes
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

# ============ FORMATTER ============

def format_results(results: Dict[str, Any]) -> str:
    """Formater les résultats pour affichage"""
    
    if 'error' in results:
        return f"❌ Erreur: {results['error']}"
    
    output = ""
    
    # En-tête
    if 'email' in results:
        output += f"\n📧 Email: {results['email']}\n"
    elif 'phone' in results:
        output += f"\n📱 Téléphone: {results['phone']}\n"
    elif 'username' in results:
        output += f"\n👤 Pseudo: {results['username']}\n"
    
    # Score de confiance
    if 'confidence' in results:
        confidence = results['confidence']
        bar = "█" * int(confidence / 10) + "░" * (10 - int(confidence / 10))
        output += f"[cyan]Confiance: [{bar}] {confidence}%[/cyan]\n\n"
    
    # Sources trouvées
    if 'sources' in results:
        output += "[bold]Sources Trouvées:[/bold]\n"
        
        for source_name, source_data in results['sources'].items():
            if isinstance(source_data, dict) and len(source_data) > 0:
                output += f"  ✓ {source_name}:\n"
                for key, value in source_data.items():
                    if value:
                        output += f"    • {key}: {str(value)[:60]}\n"
            elif isinstance(source_data, list) and len(source_data) > 0:
                output += f"  ✓ {source_name}: {len(source_data)} résultats\n"
    
    # Fuites/Breaches
    if 'breaches' in results and len(results['breaches']) > 0:
        output += f"\n[bold red]⚠️  Fuites Détectées:[/bold red]\n"
        for breach in results['breaches']:
            if 'breach_name' in breach:
                output += f"  • {breach['breach_name']}"
                if 'date' in breach:
                    output += f" ({breach['date']})"
                output += "\n"
    
    return output

def create_results_table(results: Dict[str, Any]) -> Table:
    """Créer une table Rich des résultats"""
    
    table = Table(title="Résultats Raven Trace", show_header=True, header_style="bold magenta")
    table.add_column("Clé", style="cyan")
    table.add_column("Valeur", style="green")
    
    def flatten_dict(d, parent_key=''):
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            
            if isinstance(v, dict):
                items.extend(flatten_dict(v, new_key).items())
            elif isinstance(v, list):
                items.append((new_key, f"[{len(v)} items]"))
            else:
                items.append((new_key, str(v)[:80]))
        return dict(items)
    
    flat_results = flatten_dict(results)
    
    for key, value in flat_results.items():
        table.add_row(key, value)
    
    return table

def export_json(results: Dict[str, Any], filepath: str):
    """Exporter les résultats en JSON"""
    import json
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    console.print(f"[green]✓ Résultats exportés: {filepath}[/green]")

def export_csv(results: Dict[str, Any], filepath: str):
    """Exporter les résultats en CSV"""
    import csv
    import json
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # En-têtes
        writer.writerow(['Clé', 'Valeur'])
        
        # Flatten et écrire
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