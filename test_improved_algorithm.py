#!/usr/bin/env python3
"""Test the improved algorithm with domain-specific pattern recognition."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_pattern_analysis():
    """Test pattern analysis and domain recognition."""
    try:
        from regexgen.patterns.analysis import PatternAnalyzer
        
        analyzer = PatternAnalyzer()
        
        # Test digit recognition
        digit_examples = ["123", "456", "789", "000"]
        analysis = analyzer.analyze_examples(digit_examples)
        
        print("🔍 Digit Pattern Analysis:")
        print(f"  Pattern type: {analysis.pattern_type}")
        print(f"  Structure: {analysis.detected_structure}")
        print(f"  Length range: {analysis.length_range}")
        
        assert analysis.pattern_type == 'digits'
        assert all(ct == 'digit' for ct in analysis.detected_structure)
        
        # Test email recognition
        email_examples = ["user@domain.com", "admin@site.org", "test@example.net"]
        analysis = analyzer.analyze_examples(email_examples)
        
        print("\n📧 Email Pattern Analysis:")
        print(f"  Pattern type: {analysis.pattern_type}")
        print(f"  Common suffixes: {analysis.common_suffixes}")
        
        assert analysis.pattern_type == 'email'
        
        # Test mixed pattern
        mixed_examples = ["abc123", "def456", "ghi789"]
        analysis = analyzer.analyze_examples(mixed_examples)
        
        print("\n🔤 Mixed Pattern Analysis:")
        print(f"  Pattern type: {analysis.pattern_type}")
        print(f"  Structure: {analysis.detected_structure}")
        print(f"  Length: {analysis.common_length}")
        
        assert analysis.common_length == 6
        
        print("✓ Pattern analysis working correctly")
        return True
        
    except Exception as e:
        print(f"✗ Pattern analysis test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_improved_generation():
    """Test improved pattern generation with examples."""
    try:
        from regexgen.patterns.mutations import PatternMutator
        from regexgen.patterns.analysis import PatternAnalyzer
        
        mutator = PatternMutator()
        
        # Test digit pattern generation
        digit_examples = ["123", "456", "789"]
        pattern = mutator.generate_random_pattern(max_complexity=20, examples=digit_examples)
        
        print("\n🎯 Improved Generation Test:")
        print(f"  Digit examples: {digit_examples}")
        print(f"  Generated pattern: {pattern.to_regex()}")
        
        # Test that generated pattern is reasonable for digits
        regex_str = pattern.to_regex()
        assert any(char in regex_str for char in "0123456789[d"), f"Generated pattern doesn't seem digit-related: {regex_str}"
        
        # Test email pattern generation
        email_examples = ["user@test.com", "admin@site.org"]
        pattern = mutator.generate_random_pattern(max_complexity=30, examples=email_examples)
        
        print(f"  Email examples: {email_examples}")
        print(f"  Generated pattern: {pattern.to_regex()}")
        
        print("✓ Improved generation working")
        return True
        
    except Exception as e:
        print(f"✗ Improved generation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_improvement():
    """Test end-to-end improvement with simulated annealing."""
    try:
        from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig
        from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
        
        # Test with simple digit patterns
        positive_examples = ["123", "456", "789", "000", "999"]
        negative_examples = ["abc", "12a", "1234", "12"]
        
        config = SAConfig(
            max_iterations=100,  # Quick test
            max_complexity=30,
            timeout_seconds=10,
            random_seed=42
        )
        
        optimizer = SimulatedAnnealing(config)
        scorer = MultiCriteriaScorer(mode=ScoringMode.BALANCED)
        
        print("\n🚀 End-to-End Improvement Test:")
        print(f"  Positive examples: {positive_examples}")
        print(f"  Negative examples: {negative_examples}")
        
        result = optimizer.optimize(positive_examples, negative_examples, scorer)
        
        print(f"  Generated pattern: {result.best_pattern.to_regex()}")
        print(f"  Score: {result.best_fitness.total_score:.3f}")
        print(f"  Positive matches: {result.best_fitness.positive_matches}/{len(positive_examples)}")
        print(f"  Negative rejections: {result.best_fitness.negative_matches}/{len(negative_examples)}")
        print(f"  Iterations: {result.iterations}")
        print(f"  Time: {result.time_seconds:.2f}s")
        
        # Test should achieve reasonable performance
        assert result.best_fitness.total_score > 0.3, f"Score too low: {result.best_fitness.total_score}"
        
        print("✓ End-to-end improvement working")
        return True
        
    except Exception as e:
        print(f"✗ End-to-end test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ast_parsing():
    """Test improved AST parsing."""
    try:
        from regexgen.patterns.ast import PatternAST
        
        print("\n📝 AST Parsing Test:")
        
        # Test digit pattern
        pattern = PatternAST.from_string("[0-9]")
        print(f"  [0-9] -> {pattern.to_regex()}")
        assert "0" in pattern.root.characters
        
        # Test quantifier
        pattern = PatternAST.from_string("\\d+")
        print(f"  \\d+ -> {pattern.to_regex()}")
        
        # Test character class
        pattern = PatternAST.from_string("[a-z]")
        print(f"  [a-z] -> {pattern.to_regex()}")
        assert "a" in pattern.root.characters
        
        print("✓ AST parsing improvements working")
        return True
        
    except Exception as e:
        print(f"✗ AST parsing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🧪 Testing Algorithm Improvements")
    print("=" * 50)
    
    success = True
    
    success &= test_pattern_analysis()
    success &= test_improved_generation()
    success &= test_ast_parsing()
    success &= test_end_to_end_improvement()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All improvement tests passed!")
        print("Algorithm quality has been enhanced!")
    else:
        print("❌ Some improvement tests failed.")
        sys.exit(1)