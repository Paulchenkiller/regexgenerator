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
    
    # Import required components
    from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig, CoolingSchedule
    from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
    from regexgen.validation.validator import PatternValidator
    
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
    
    # Configure optimization
    scoring_mode = ScoringMode(scoring)
    sa_config = SAConfig(
        max_iterations=max_iterations,
        max_complexity=max_complexity,
        random_seed=seed,
        timeout_seconds=timeout
    )
    
    # Create components
    fitness_scorer = MultiCriteriaScorer(mode=scoring_mode, timeout_seconds=1.0)
    optimizer = SimulatedAnnealing(config=sa_config)
    validator = PatternValidator(timeout_seconds=2.0)
    
    if verbose:
        console.print("[dim]Starting pattern optimization...[/dim]")
        
        with console.status("[bold green]Optimizing pattern...") as status:
            # Run optimization
            result = optimizer.optimize(all_positives, all_negatives, fitness_scorer)
            
            if verbose:
                status.update("[bold green]Validating result...")
                validation = validator.validate(result.best_pattern, all_positives, all_negatives)
    else:
        # Run optimization without progress indicator
        result = optimizer.optimize(all_positives, all_negatives, fitness_scorer)
        validation = validator.validate(result.best_pattern, all_positives, all_negatives)
    
    # Generate output
    generated_pattern = result.best_pattern.to_regex()
    
    if output_json:
        import json
        output_data = {
            "regex": generated_pattern,
            "score": float(result.best_fitness.total_score),
            "complexity": result.best_pattern.complexity(),
            "time_ms": int(result.time_seconds * 1000),
            "positive_matches": result.best_fitness.positive_matches,
            "negative_matches": result.best_fitness.negative_matches,
            "algorithm": algorithm,
            "iterations": result.iterations,
            "convergence_reason": result.convergence_reason,
            "validation": {
                "is_valid": validation.is_valid,
                "timeout_occurred": validation.timeout_occurred,
                "performance_warnings": validation.performance_warnings
            }
        }
        console.print(json.dumps(output_data, indent=2))
    else:
        console.print(generated_pattern)
    
    if test:
        console.print()
        
        # Show optimization results
        if result.best_fitness.total_score > 0.9:
            console.print(f"[green]✔️[/green] Pattern generation completed with score {result.best_fitness.total_score:.3f}")
        elif result.best_fitness.total_score > 0.7:
            console.print(f"[yellow]⚠️[/yellow] Pattern generation completed with score {result.best_fitness.total_score:.3f}")
        else:
            console.print(f"[red]❌[/red] Pattern generation completed with low score {result.best_fitness.total_score:.3f}")
        
        console.print(f"[green]✔️[/green] {result.best_fitness.positive_matches}/{len(all_positives)} positive examples matched")
        console.print(f"[green]✔️[/green] {result.best_fitness.negative_matches}/{len(all_negatives)} negative examples correctly rejected")
        
        # Show performance info
        console.print(f"[dim]Completed in {result.iterations} iterations ({result.time_seconds:.2f}s)[/dim]")
        console.print(f"[dim]Convergence reason: {result.convergence_reason}[/dim]")
        
        # Show validation warnings if any
        if validation.performance_warnings:
            console.print("[yellow]Performance warnings:[/yellow]")
            for warning in validation.performance_warnings:
                console.print(f"  [yellow]⚠️[/yellow] {warning}")


if __name__ == "__main__":
    cli()