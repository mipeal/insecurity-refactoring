"""
Command Line Interface for Insecurity Refactoring

This module provides a CLI interface using Typer for vulnerability scanning and analysis.
"""

import typer
from typing import Optional, List
from pathlib import Path
from rich import print as rprint
from rich.console import Console
from rich.table import Table
import logging
from insecurity_refactoring_py.db import Neo4jDB
from insecurity_refactoring_py.scanner import VulnerabilityScanner
from insecurity_refactoring_py.config import Settings

app = typer.Typer(
    name="insecurity-cli",
    help="Insecurity Refactoring Tool - Detect and analyze security vulnerabilities in PHP code"
)
console = Console()

settings = Settings()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


@app.command()
def scan(
    path: Path = typer.Argument(..., help="Path to scan for vulnerabilities"),
    prepare_db: bool = typer.Option(True, "--prepare/--no-prepare", "-p/-n", help="Prepare database before scanning"),
    output: bool = typer.Option(False, "--output", "-o", help="Print detailed output"),
    gui: bool = typer.Option(False, "--gui", "-g", help="Launch GUI interface"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose logging"),
    specific_pattern: Optional[List[str]] = typer.Option(None, "--pattern", help="Specific pattern to scan for"),
    control_flow: bool = typer.Option(False, "--control-flow", "-c", help="Enable control flow check"),
):
    """
    Scan a path for security vulnerabilities.
    """
    setup_logging(verbose)
    
    if not path.exists():
        rprint(f"[red]Error: Path {path} does not exist[/red]")
        raise typer.Exit(1)
    
    rprint(f"[cyan]Scanning path:[/cyan] {path}")
    
    # Connect to Neo4j
    db = Neo4jDB(uri=settings.neo4j_uri, user=settings.neo4j_user, password=settings.neo4j_password)
    
    if not db.connect():
        rprint("[red]Failed to connect to Neo4j database[/red]")
        raise typer.Exit(1)
    
    try:
        scanner = VulnerabilityScanner(db)
        
        if prepare_db:
            rprint("[yellow]Preparing database...[/yellow]")
            scanner.prepare_database(str(path))
        
        rprint("[yellow]Scanning for vulnerabilities...[/yellow]")
        results = scanner.scan(str(path), specific_patterns=specific_pattern or [])
        
        # Display results
        if output:
            display_results(results)
        
        rprint(f"[green]Scan complete. Found {len(results)} potential issues.[/green]")
        
    finally:
        db.close()


@app.command()
def connect_test(
    uri: str = typer.Option(settings.neo4j_uri, "--uri", help="Neo4j connection URI"),
    user: str = typer.Option(settings.neo4j_user, "--user", help="Neo4j username"),
    password: str = typer.Option(settings.neo4j_password, "--password", help="Neo4j password"),
):
    """
    Test connection to Neo4j database.
    """
    rprint(f"[cyan]Testing connection to:[/cyan] {uri}")
    
    db = Neo4jDB(uri=uri, user=user, password=password)
    
    if db.connect():
        rprint("[green]✓ Successfully connected to Neo4j[/green]")
        db.close()
    else:
        rprint("[red]✗ Failed to connect to Neo4j[/red]")
        raise typer.Exit(1)


@app.command()
def version():
    """
    Display version information.
    """
    from insecurity_refactoring_py import __version__
    rprint(f"Insecurity Refactoring Tool v{__version__}")


def display_results(results: List[dict]) -> None:
    """
    Display scan results in a formatted table.
    
    Args:
        results: List of vulnerability findings
    """
    if not results:
        rprint("[yellow]No vulnerabilities found[/yellow]")
        return
    
    table = Table(title="Vulnerability Scan Results")
    table.add_column("Type", style="cyan")
    table.add_column("Location", style="magenta")
    table.add_column("Severity", style="red")
    table.add_column("Details", style="white")
    
    for result in results:
        table.add_row(
            result.get("type", "Unknown"),
            result.get("location", "Unknown"),
            result.get("severity", "Unknown"),
            result.get("details", "")
        )
    
    console.print(table)


if __name__ == "__main__":
    app()
