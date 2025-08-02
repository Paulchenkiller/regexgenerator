#!/usr/bin/env python3
"""Quick test to see if algorithm improvements work."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_simple_digit_case():
    """Test the simplest possible case."""
    try:
        from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig
        from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
        
        positives = ["123", "456", "789"]
        negatives = ["abc", "12a"]
        
        config = SAConfig(
            max_iterations=50,
            max_complexity=20,
            timeout_seconds=3,
            random_seed=42,
            max_no_improvement=20
        )
        
        optimizer = SimulatedAnnealing(config)
        scorer = MultiCriteriaScorer(mode=ScoringMode.BALANCED)
        
        print("🔬 Simple Digit Test:")
        print(f"  Positives: {positives}")
        print(f"  Negatives: {negatives}")
        
        result = optimizer.optimize(positives, negatives, scorer)
        
        pattern = result.best_pattern.to_regex()
        score = result.best_fitness.total_score
        pos_matches = result.best_fitness.positive_matches
        neg_matches = result.best_fitness.negative_matches
        
        print(f"  Generated: {pattern}")
        print(f"  Score: {score:.3f}")
        print(f"  Positive matches: {pos_matches}/{len(positives)}")
        print(f"  Negative rejections: {neg_matches}/{len(negatives)}")
        print(f"  Time: {result.time_seconds:.2f}s")
        print(f"  Iterations: {result.iterations}")
        
        # Success if we match all positives and reject all negatives
        success = pos_matches == len(positives) and neg_matches == len(negatives)
        
        if success:
            print("  ✅ SUCCESS")
        else:
            print("  ❌ FAILED")
            
        return success
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_pattern_generation():
    """Test just the pattern generation."""
    try:
        from regexgen.patterns.mutations import PatternMutator
        from regexgen.patterns.analysis import PatternAnalyzer
        
        print("\n🧬 Pattern Generation Test:")
        
        # Test digit analysis
        examples = ["123", "456", "789"]
        analyzer = PatternAnalyzer()
        analysis = analyzer.analyze_examples(examples)
        
        print(f"  Examples: {examples}")
        print(f"  Detected type: {analysis.pattern_type}")
        print(f"  Structure: {analysis.detected_structure}")
        
        # Generate initial pattern
        initial_pattern = analyzer.generate_initial_pattern(analysis)
        print(f"  Initial pattern: {initial_pattern.to_regex()}")
        
        # Test mutation
        mutator = PatternMutator()
        guided_pattern = mutator.generate_random_pattern(max_complexity=20, examples=examples)
        print(f"  Guided pattern: {guided_pattern.to_regex()}")
        
        print("  ✅ Pattern generation working")
        return True
        
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("⚡ Quick Algorithm Improvement Test")
    print("=" * 40)
    
    success1 = test_pattern_generation()
    success2 = test_simple_digit_case()
    
    print("\n" + "=" * 40)
    if success1 and success2:
        print("🎉 Quick tests passed!")
    else:
        print("❌ Tests failed")
        sys.exit(1)