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

### Option 1: Virtual Environment (Recommended)
```bash
# Clone the repository
git clone https://github.com/Paulchenkiller/regexgenerator
cd regexgenerator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies and package
pip install -r requirements.txt
pip install -e .

# Test installation
regexgen --help
```

### Option 2: Using pipx (Alternative)
```bash
# Install pipx if you don't have it
brew install pipx  # On macOS
# or: python3 -m pip install --user pipx

# Clone and install
git clone https://github.com/Paulchenkiller/regexgenerator
cd regexgenerator
pipx install -e .
```

### Option 3: Direct Python Execution (No Installation)
```bash
# Clone the repository
git clone https://github.com/Paulchenkiller/regexgenerator
cd regexgenerator

# Install only runtime dependencies (optional for basic functionality)
python3 -m pip install --user click rich

# Run directly from source
cd src && python3 -m regexgen --help
```

### Requirements
- Python 3.11+
- **Required**: click, rich (for CLI interface)
- **Optional**: numpy, scipy (for enhanced algorithms - fallbacks implemented)

## Quick Start

```bash
# After installation (Option 1 or 2):
regexgen "abc123" "def456" "ghi789"

# Or running from source (Option 3):
cd src && python3 -m regexgen "abc123" "def456" "ghi789"

# Generate pattern excluding certain formats
regexgen "valid-file.txt" "data-2023.log" -n "invalid_file" "no-extension"

# Fine-tune the generation process
regexgen --max-iterations 1000 --max-complexity 30 --scoring minimal "abc" "def" "ghi"

# Use file input
echo -e "test123\ndata456\nfile789" > examples.txt
regexgen --file examples.txt --test --verbose
```

## Use Cases

- **Data Validation**: Generate patterns for form inputs, file names, IDs
- **Log Processing**: Extract structured data from log files
- **Text Mining**: Find patterns in unstructured text
- **Code Generation**: Auto-create validation rules
- **Testing**: Generate test patterns for edge cases

## Roadmap

### Phase 1 (MVP) ✅ COMPLETED
- [x] Project setup and documentation
- [x] Python 3.11+ project structure with modular organization  
- [x] Comprehensive Pattern AST with 7 node types
- [x] Click-based CLI interface with rich formatting
- [x] File input/output support
- [x] Core simulated annealing algorithm with 4 cooling schedules
- [x] Multi-criteria fitness scoring system (3 scoring modes)
- [x] Pattern mutation operators (7 different mutations)
- [x] Example validation and performance testing
- [x] Complete CLI integration with JSON output support

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
RegexGenerator v0.1.0
[a-z]{3}[0-9]{3}

$ regexgen --test "abc123" "def456" "ghi789"
RegexGenerator v0.1.0
┏━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Type     ┃ Count ┃ Examples                                                                                                                          ┃
┡━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Positive │     3 │ abc123, def456, ghi789                                                                                                            │
│ Negative │     0 │ None                                                                                                                              │
└──────────┴───────┴───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
[a-z]{3}[0-9]{3}

✔️ Pattern generation completed with score 0.892
✔️ 3/3 positive examples matched
✔️ 0/0 negative examples correctly rejected
Completed in 127 iterations (2.34s)
Convergence reason: perfect_solution
```

### Advanced Usage
```bash
$ regexgen --file emails.txt --negative-file not_emails.txt --scoring balanced --json
RegexGenerator v0.1.0
{
  "regex": "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}",
  "score": 0.947,
  "complexity": 28,
  "time_ms": 3421,
  "positive_matches": 98,
  "negative_matches": 47,
  "algorithm": "sa",
  "iterations": 892,
  "convergence_reason": "no_improvement",
  "validation": {
    "is_valid": true,
    "timeout_occurred": false,
    "performance_warnings": []
  }
}
```

### Current Implementation Status
**✅ FULLY FUNCTIONAL**: All core components are implemented and working:

- **Simulated Annealing**: Complete optimization engine with 4 cooling schedules
- **Pattern Mutations**: 7 different mutation operators for pattern evolution
- **Fitness Scoring**: Multi-criteria evaluation (correctness, complexity, readability, performance)
- **Validation System**: Comprehensive pattern testing with timeout protection
- **CLI Interface**: Full-featured command-line tool with rich output formatting

The tool can now generate actual regex patterns from examples using intelligent optimization!

## Troubleshooting Installation

### "externally-managed-environment" Error
If you see this error with `pip install`, use one of these solutions:

1. **Use virtual environment** (recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Use pipx** (if available):
   ```bash
   pipx install -e .
   ```

3. **Use --break-system-packages** (not recommended):
   ```bash
   pip install --break-system-packages -r requirements.txt
   ```

### "Command not found: regexgen" Error
- Make sure you activated the virtual environment: `source venv/bin/activate`
- Or use direct execution: `cd src && python3 -m regexgen`

### Testing Your Installation
Run the installation test script:
```bash
python3 test_installation.py
```

This will verify that all installation methods work correctly.