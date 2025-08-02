# RegexGenerator

A smart CLI tool written in Python that automatically generates minimal, readable regular expressions from positive and negative examples using advanced optimization algorithms.

## Overview

RegexGenerator uses intelligent search algorithms (starting with simulated annealing, expanding to genetic algorithms) to discover optimal regex patterns that match your positive examples while avoiding negative ones. Instead of manually crafting complex patterns, simply provide examples of what you want to match.

## Features

### Core Functionality
- **Smart Pattern Generation**: Uses simulated annealing (GA support coming soon) to find optimal regex patterns
- **Positive/Negative Examples**: Specify what should match and what shouldn't
- **Minimal Output**: Generates concise, readable patterns instead of verbose alternations
- **Multiple Input Methods**: Command-line arguments or text files (one example per line)
- **Self-Testing**: Automatically validates generated patterns against your examples

### CLI Interface
```bash
# Basic usage with positive examples
regexgen "hello" "world" "help"

# With negative examples
regexgen -p "cat" "car" "cap" -n "dog" "bird"

# From file input
regexgen --file examples.txt --negative-file counter_examples.txt

# Advanced options
regexgen --algorithm sa --max-complexity 50 --scoring balanced --timeout 30s examples.txt
```

### Optimization Algorithms
- **Simulated Annealing** (default): Good balance of speed and quality
- **Genetic Algorithm** (planned): More thorough exploration for complex patterns

### Output Formats
- **Standard**: Clean regex pattern to stdout
- **JSON**: Detailed report with metrics
- **Verbose**: Include explanation and performance data

### Configuration Options
- **Complexity Bounds**: Limit pattern length and nesting depth
- **Scoring Functions**: Choose between minimal, readable, or balanced optimization
- **Performance Tuning**: Adjust iterations, temperature, timeouts
- **Regex Dialects**: Support for PCRE, ECMAScript, etc.

## Installation

```bash
# Install from source
git clone https://github.com/Paulchenkiller/regexgenerator
cd regexgenerator

# Install Python dependencies
pip install -r requirements.txt

# Install as CLI tool
pip install -e .
```

### Requirements
- Python 3.11+
- Dependencies: click, rich, numpy, scipy (for optimization algorithms)

## Quick Start

```bash
# Generate pattern for email-like strings
regexgen "user@domain.com" "admin@site.org" "test@example.net"

# Generate pattern excluding certain formats  
regexgen -p "valid-file.txt" "data-2023.log" -n "invalid_file" "no-extension"

# Fine-tune the generation process
regexgen --max-iterations 1000 --complexity-limit 30 --scoring minimal examples.txt
```

## Use Cases

- **Data Validation**: Generate patterns for form inputs, file names, IDs
- **Log Processing**: Extract structured data from log files
- **Text Mining**: Find patterns in unstructured text
- **Code Generation**: Auto-create validation rules
- **Testing**: Generate test patterns for edge cases

## Roadmap

### Phase 1 (MVP)
- [x] Project setup and documentation
- [ ] Core simulated annealing algorithm
- [ ] Basic CLI interface
- [ ] File input/output
- [ ] Pattern validation and testing

### Phase 2 (Enhanced)
- [ ] Genetic algorithm implementation
- [ ] Advanced scoring functions
- [ ] Multiple regex dialect support
- [ ] JSON output format
- [ ] Performance optimizations

### Phase 3 (Advanced)
- [ ] Interactive mode with REPL
- [ ] Pattern explanation and visualization
- [ ] Web API service
- [ ] ML-assisted pattern suggestions
- [ ] Plugin architecture

## Contributing

[Contribution guidelines TBD]

## License

[License TBD - considering MIT or Apache 2.0]

## Examples

### Basic Pattern Generation
```bash
$ regexgen "abc123" "def456" "ghi789"
[a-z]{3}[0-9]{3}

$ regexgen --test "abc123" "def456" "ghi789"
Generated: [a-z]{3}[0-9]{3}
✔️ 3/3 positive examples matched
✔️ 0/0 negative examples matched
Pattern validation: PASSED
```

### Advanced Usage
```bash
$ regexgen --file emails.txt --negative-file not_emails.txt --scoring balanced --json
{
  "regex": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "score": 0.95,
  "complexity": 28,
  "time_ms": 1247,
  "positive_matches": 100,
  "negative_matches": 0,
  "algorithm": "simulated_annealing"
}
```