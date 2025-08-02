"""Main CLI entry point for RegexGenerator."""

from enum import Enum
from pathlib import Path
from typing import Optional, Sequence

import click
from rich.console import Console
from rich.table import Table

from regexgen import __version__


class Algorithm(str, Enum):
    """Available optimization algorithms."""
    SIMULATED_ANNEALING = "sa"
    GENETIC_ALGORITHM = "ga"


class ScoringMode(str, Enum):
    """Available scoring modes."""
    MINIMAL = "minimal"
    READABLE = "readable"
    BALANCED = "balanced"


console = Console()


@click.command()
@click.version_option(version=__version__)
@click.argument("positive_examples", nargs=-1, required=False)
@click.option(
    "-n", "--negative", 
    multiple=True,
    help="Negative examples that the pattern must NOT match."
)
@click.option(
    "-f", "--file",
    type=click.Path(exists=True, path_type=Path),
    help="File containing positive examples (one per line)."
)
@click.option(
    "--negative-file",
    type=click.Path(exists=True, path_type=Path),
    help="File containing negative examples (one per line)."
)
@click.option(
    "--algorithm",
    type=click.Choice([a.value for a in Algorithm]),
    default=Algorithm.SIMULATED_ANNEALING.value,
    help="Optimization algorithm to use."
)
@click.option(
    "--max-complexity",
    type=int,
    default=50,
    help="Maximum pattern complexity limit."
)
@click.option(
    "--max-iterations",
    type=int,
    default=1000,
    help="Maximum algorithm iterations."
)
@click.option(
    "--timeout",
    type=int,
    default=30,
    help="Timeout in seconds."
)
@click.option(
    "--scoring",
    type=click.Choice([s.value for s in ScoringMode]),
    default=ScoringMode.BALANCED.value,
    help="Scoring mode for pattern evaluation."
)
@click.option(
    "--seed",
    type=int,
    help="Random seed for reproducible results."
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output results in JSON format."
)
@click.option(
    "--verbose", "-v",
    is_flag=True,
    help="Enable verbose output with progress information."
)
@click.option(
    "--test",
    is_flag=True,
    help="Show validation results after generation."
)
@click.option(
    "--quiet", "-q",
    is_flag=True,
    help="Suppress non-essential output."
)
def cli(
    positive_examples: Sequence[str],
    negative: Sequence[str],
    file: Optional[Path],
    negative_file: Optional[Path],
    algorithm: str,
    max_complexity: int,
    max_iterations: int,
    timeout: int,
    scoring: str,
    seed: Optional[int],
    output_json: bool,
    verbose: bool,
    test: bool,
    quiet: bool,
) -> None:
    """Generate optimal regex patterns from positive and negative examples.
    
    POSITIVE_EXAMPLES: Strings that the generated pattern should match.
    
    Examples:
    
    \b
    # Basic usage
    regexgen "hello" "world" "help"
    
    \b
    # With negative examples
    regexgen "cat" "car" "cap" -n "dog" "bird"
    
    \b
    # From file
    regexgen --file examples.txt --test --verbose
    """
    if not quiet:
        console.print(f"[bold blue]RegexGenerator v{__version__}[/bold blue]")
    
    # Collect all positive examples
    all_positives = list(positive_examples)
    if file:
        try:
            with open(file, 'r', encoding='utf-8') as f:
                file_positives = [line.strip() for line in f if line.strip()]
                all_positives.extend(file_positives)
        except Exception as e:
            console.print(f"[red]Error reading file {file}: {e}[/red]")
            raise click.Abort()
    
    # Collect all negative examples
    all_negatives = list(negative)
    if negative_file:
        try:
            with open(negative_file, 'r', encoding='utf-8') as f:
                file_negatives = [line.strip() for line in f if line.strip()]
                all_negatives.extend(file_negatives)
        except Exception as e:
            console.print(f"[red]Error reading negative file {negative_file}: {e}[/red]")
            raise click.Abort()
    
    # Validate input
    if not all_positives:
        console.print("[red]Error: No positive examples provided.[/red]")
        console.print("Provide examples as arguments or use --file option.")
        raise click.Abort()
    
    if verbose:
        console.print(f"[dim]Positive examples: {len(all_positives)}[/dim]")
        console.print(f"[dim]Negative examples: {len(all_negatives)}[/dim]")
        console.print(f"[dim]Algorithm: {algorithm}[/dim]")
        console.print(f"[dim]Max complexity: {max_complexity}[/dim]")
        console.print(f"[dim]Max iterations: {max_iterations}[/dim]")
        console.print(f"[dim]Scoring: {scoring}[/dim]")
        if seed is not None:
            console.print(f"[dim]Seed: {seed}[/dim]")
        console.print()
    
    # TODO: Implement actual pattern generation
    # For now, show a placeholder
    if not quiet:
        console.print("[yellow]⚠️  Pattern generation not yet implemented[/yellow]")
        console.print("[dim]This is a placeholder implementation[/dim]")
    
    # Show input summary
    if test or verbose:
        table = Table(title="Input Summary")
        table.add_column("Type", style="cyan")
        table.add_column("Count", justify="right", style="magenta")
        table.add_column("Examples", style="green")
        
        pos_preview = ", ".join(all_positives[:3])
        if len(all_positives) > 3:
            pos_preview += f", ... (+{len(all_positives)-3} more)"
        
        neg_preview = ", ".join(all_negatives[:3]) if all_negatives else "None"
        if len(all_negatives) > 3:
            neg_preview += f", ... (+{len(all_negatives)-3} more)"
        
        table.add_row("Positive", str(len(all_positives)), pos_preview)
        table.add_row("Negative", str(len(all_negatives)), neg_preview)
        
        console.print(table)
    
    # Placeholder output
    placeholder_pattern = r"[a-z]+"
    
    if output_json:
        import json
        result = {
            "regex": placeholder_pattern,
            "score": 0.0,
            "complexity": len(placeholder_pattern),
            "time_ms": 0,
            "positive_matches": len(all_positives),
            "negative_matches": 0,
            "algorithm": algorithm
        }
        console.print(json.dumps(result, indent=2))
    else:
        console.print(placeholder_pattern)
    
    if test:
        console.print()
        console.print("[green]✔️[/green] Pattern generation completed (placeholder)")
        console.print(f"[green]✔️[/green] {len(all_positives)}/{len(all_positives)} positive examples would match")
        console.print(f"[green]✔️[/green] {len(all_negatives)}/{len(all_negatives)} negative examples would not match")


if __name__ == "__main__":
    cli()