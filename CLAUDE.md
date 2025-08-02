# RegexGenerator - Claude Development Context

This file contains essential context for Claude Code to effectively assist with the RegexGenerator project development.

## Project Overview

RegexGenerator is a CLI tool that automatically generates optimal regular expressions from positive and negative examples using advanced optimization algorithms. The goal is to produce minimal, readable regex patterns that are far more concise than manual alternations.

## Architecture Decisions

### Language Selection
- **Status**: ✅ **DECIDED - Python 3.11+**
- **Rationale**: Best balance of algorithm libraries, development speed, and future ML integration
- **Key Dependencies**: click (CLI), rich (output), numpy/scipy (algorithms), regex (advanced patterns)

### Core Algorithm Strategy
- **Phase 1**: Simulated Annealing (easier to implement, good results)
- **Phase 2**: Genetic Algorithm (more thorough exploration)
- **Future**: Support algorithm selection via CLI flag

### Input/Output Design
- **Input**: Command-line args or text files (one example per line)
- **Output**: Clean regex to stdout, optional JSON format with metadata
- **Validation**: Self-testing against provided examples with exit codes

## Key Components (Python Implementation)

### 1. Pattern Generator (Core)
```python
# regexgen/algorithms/simulated_annealing.py
- SA engine with scipy.optimize integration
- Pattern AST representation and mutation operators
- Multi-criteria fitness scoring with numpy arrays
- Convergence detection and early stopping
```

### 2. CLI Interface  
```python
# regexgen/cli/main.py
- Click-based argument parsing with rich help formatting
- Configuration dataclasses for type safety
- File I/O with pathlib and proper encoding handling
- Rich progress bars and formatted output
```

### 3. Pattern Validation
```python
# regexgen/validation/
- Regex compilation with multiple engines (re, regex module)
- Backtracking detection via timeout mechanisms
- Batch example validation with efficient matching
- Performance profiling and scoring
```

### 4. Optimization Features
```python  
# regexgen/scoring/
- Pluggable scoring functions with abstract base classes
- NumPy-based complexity calculations
- Timeout controls with threading/multiprocessing
- Random seed management for reproducibility
```

## Development Standards

### Testing Strategy
- **Unit Tests**: Algorithm components, pattern mutations, scoring functions
- **Integration Tests**: End-to-end CLI workflows, file processing
- **Performance Tests**: Algorithm efficiency, pattern execution speed
- **Example Tests**: Common use cases (emails, URLs, IDs)

### Code Quality (Python-Specific)
- Follow PEP 8 style guide with black formatter
- Use type hints with mypy validation
- Comprehensive error handling with helpful messages
- Clear separation of concerns (algorithm, CLI, I/O)
- Use dataclasses for configuration and results
- Leverage Python 3.11+ features (match statements, improved typing)

### Documentation Requirements
- Inline code documentation for complex algorithms
- CLI help text with examples
- Algorithm explanation in README
- API documentation for extensibility

## Important Implementation Notes

### Regex Pattern Representation
- Use AST/tree structure for pattern manipulation
- Support incremental mutations (character classes, quantifiers, groups)
- Maintain pattern validity during mutations
- Track complexity metrics during generation

### Scoring Function Design
```python
def score_pattern(pattern, positive_examples, negative_examples, weights):
    """
    Multi-criteria scoring:
    - Correctness: matches all positive, none negative
    - Minimality: shorter patterns preferred
    - Readability: avoid deep nesting, complex constructs
    - Performance: avoid backtracking patterns
    """
```

### CLI Flag Design
```bash
# Core functionality
regexgen [positive_examples...] 
  -n, --negative [negative_examples...]
  -f, --file [input_file]
  --negative-file [negative_file]

# Algorithm control
  --algorithm {sa,ga}
  --max-iterations N
  --max-complexity N
  --timeout DURATION
  --seed N

# Output control
  --json
  --verbose
  --test
  --quiet

# Scoring weights
  --scoring {minimal,readable,balanced}
  --complexity-weight FLOAT
  --readability-weight FLOAT
```

### Error Handling Strategy
1. **Input Validation**: Check examples, files, parameters
2. **Algorithm Failures**: Timeout, no solution found, resource limits
3. **Pattern Errors**: Invalid regex, compilation failures
4. **Graceful Degradation**: Partial solutions, fallback strategies

## Performance Considerations

### Algorithm Efficiency
- Lazy evaluation where possible
- Early termination on perfect solutions
- Efficient pattern mutation operations
- Memory-conscious data structures

### Pattern Quality
- Avoid catastrophic backtracking patterns
- Optimize character classes and quantifiers
- Detect and eliminate redundant constructs
- Balance minimality with readability

## Testing Commands

Once implemented, run these for quality assurance:
```bash
# Unit tests with pytest
pytest tests/ -v --cov=regexgen

# Type checking
mypy regexgen/

# Code formatting
black regexgen/ tests/
flake8 regexgen/ tests/

# Integration test examples
regexgen "test@email.com" "user@domain.org" -n "invalid-email" "no-at-sign"
regexgen --file examples/emails.txt --test --json

# Performance testing
regexgen --max-iterations 10000 --timeout 30s complex_examples.txt
```

## Future Extension Points

### Plugin Architecture
- Custom scoring functions
- Domain-specific pattern templates  
- Pre/post-processing hooks
- External optimization algorithms

### Machine Learning Integration
- Pattern suggestion models
- Learning from user feedback
- Domain-specific trained models
- Hybrid ML + search approaches

### Web Service Potential
- REST API endpoints
- Pattern generation service
- Batch processing capabilities
- Integration with development tools

## Development Workflow

1. **Phase 1**: Implement core SA algorithm with basic CLI
2. **Phase 2**: Add advanced features, GA algorithm, multiple scoring
3. **Phase 3**: Interactive mode, web service, ML integration

### Commit Message Format
```
feat: add simulated annealing core algorithm
fix: handle empty input examples gracefully  
docs: update CLI usage examples
test: add integration tests for file input
refactor: optimize pattern mutation operators
```

## Known Challenges

### Algorithm Challenges
- Balancing exploration vs exploitation
- Defining effective mutation operators
- Handling impossible constraint sets
- Scaling to large example sets

### Pattern Quality Challenges
- Quantifying readability objectively
- Detecting performance anti-patterns
- Handling edge cases and unicode
- Cross-dialect compatibility

### Usability Challenges
- Intuitive CLI design for complex options
- Meaningful progress reporting
- Clear error messages and suggestions
- Balancing power with simplicity

## Resources and References

### Algorithms
- Simulated Annealing: Kirkpatrick et al. (1983)
- Genetic Algorithms: Holland (1975), Goldberg (1989)
- Regex optimization: Academic papers on automatic regex synthesis

### Regex References
- PCRE documentation and behavior
- ECMAScript regex specification
- Performance best practices
- Cross-engine compatibility guides

This context file should be updated as development progresses and new insights are gained.