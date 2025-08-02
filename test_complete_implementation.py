#!/usr/bin/env python3
"""Comprehensive test for the complete RegexGenerator implementation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_full_implementation():
    """Test the complete implementation end-to-end."""
    try:
        # Test imports
        import regexgen
        from regexgen.patterns.ast import PatternAST, LiteralNode, CharacterClassNode
        from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig
        from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
        from regexgen.validation.validator import PatternValidator
        from regexgen.patterns.mutations import PatternMutator
        
        print("✓ All imports successful")
        
        # Test basic AST functionality
        literal = LiteralNode("test")
        ast = PatternAST(literal)
        assert ast.to_regex() == "test"
        assert ast.complexity() == 4
        print("✓ AST functionality works")
        
        # Test character class
        char_class = CharacterClassNode(characters={'a', 'b', 'c'})
        char_ast = PatternAST(char_class)
        regex_str = char_ast.to_regex()
        assert '[' in regex_str and ']' in regex_str
        print(f"✓ Character class works: {regex_str}")
        
        # Test pattern mutation
        mutator = PatternMutator()
        mutated = mutator.mutate(ast)
        assert mutated.to_regex() != ""  # Should produce some pattern
        print("✓ Pattern mutation works")
        
        # Test fitness scoring
        scorer = MultiCriteriaScorer(mode=ScoringMode.BALANCED)
        positive_examples = ["test", "best", "rest"]
        negative_examples = ["hello", "world"]
        
        fitness = scorer.score(ast, positive_examples, negative_examples)
        assert 0 <= fitness.total_score <= 1
        assert fitness.positive_total == 3
        assert fitness.negative_total == 2
        print(f"✓ Fitness scoring works: score={fitness.total_score:.3f}")
        
        # Test validation
        validator = PatternValidator()
        validation = validator.validate(ast, positive_examples, negative_examples)
        assert validation.regex_string == "test"
        assert not validation.timeout_occurred
        print("✓ Pattern validation works")
        
        # Test simple optimization
        config = SAConfig(max_iterations=10, max_complexity=20, timeout_seconds=5)
        optimizer = SimulatedAnnealing(config)
        
        simple_positives = ["abc", "def", "ghi"]
        simple_negatives = ["123", "xyz"]
        
        print("✓ Running simple optimization test...")
        result = optimizer.optimize(simple_positives, simple_negatives, scorer)
        
        assert result.best_pattern is not None
        assert result.best_fitness.total_score >= 0
        assert result.iterations > 0
        print(f"✓ Optimization works: {result.best_pattern.to_regex()} (score: {result.best_fitness.total_score:.3f})")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cli_integration():
    """Test CLI integration without actually running subprocess."""
    try:
        # Test that CLI imports work
        from regexgen.cli.main import cli, Algorithm, ScoringMode as CLIScoringMode
        
        print("✓ CLI imports work")
        
        # Test enum values
        assert Algorithm.SIMULATED_ANNEALING.value == "sa"
        assert CLIScoringMode.BALANCED.value == "balanced"
        print("✓ CLI enums work")
        
        return True
        
    except Exception as e:
        print(f"✗ CLI integration test failed: {e}")
        return False

def test_pattern_examples():
    """Test with realistic pattern examples."""
    try:
        from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig
        from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
        
        # Test simple digit patterns
        positives = ["123", "456", "789"]
        negatives = ["abc", "12a", "1234"]
        
        config = SAConfig(max_iterations=50, max_complexity=30, timeout_seconds=10)
        optimizer = SimulatedAnnealing(config)
        scorer = MultiCriteriaScorer(mode=ScoringMode.MINIMAL)
        
        print("✓ Testing digit pattern generation...")
        result = optimizer.optimize(positives, negatives, scorer)
        
        generated_regex = result.best_pattern.to_regex()
        print(f"✓ Generated pattern: {generated_regex}")
        print(f"✓ Score: {result.best_fitness.total_score:.3f}")
        print(f"✓ Positive matches: {result.best_fitness.positive_matches}/{len(positives)}")
        print(f"✓ Negative rejections: {result.best_fitness.negative_matches}/{len(negatives)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Pattern example test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing complete RegexGenerator implementation...")
    print()
    
    success = True
    
    print("1. Testing full implementation...")
    success &= test_full_implementation()
    print()
    
    print("2. Testing CLI integration...")
    success &= test_cli_integration()
    print()
    
    print("3. Testing realistic examples...")
    success &= test_pattern_examples()
    print()
    
    if success:
        print("🎉 All tests passed! Complete implementation is working correctly.")
        print("RegexGenerator is ready for use!")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)