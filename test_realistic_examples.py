#!/usr/bin/env python3
"""Test RegexGenerator with realistic examples that users might actually want."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_scenario(name, positives, negatives, expected_features=None):
    """Test a realistic scenario."""
    try:
        from regexgen.algorithms.simulated_annealing import SimulatedAnnealing, SAConfig
        from regexgen.scoring.fitness import MultiCriteriaScorer, ScoringMode
        from regexgen.validation.validator import PatternValidator
        
        print(f"\n📋 Testing: {name}")
        print(f"   Positives: {positives}")
        print(f"   Negatives: {negatives}")
        
        config = SAConfig(
            max_iterations=100,  # Faster testing
            max_complexity=30,   # Simpler patterns
            timeout_seconds=5,   # Quick timeout
            random_seed=42,
            max_no_improvement=50  # Faster convergence
        )
        
        optimizer = SimulatedAnnealing(config)
        scorer = MultiCriteriaScorer(mode=ScoringMode.BALANCED)
        validator = PatternValidator()
        
        result = optimizer.optimize(positives, negatives, scorer)
        validation = validator.validate(result.best_pattern, positives, negatives)
        
        pattern = result.best_pattern.to_regex()
        score = result.best_fitness.total_score
        pos_matches = result.best_fitness.positive_matches
        neg_matches = result.best_fitness.negative_matches
        
        print(f"   Generated: {pattern}")
        print(f"   Score: {score:.3f}")
        print(f"   Positive matches: {pos_matches}/{len(positives)}")
        print(f"   Negative rejections: {neg_matches}/{len(negatives)}")
        print(f"   Valid: {validation.is_valid}")
        print(f"   Time: {result.time_seconds:.2f}s")
        
        # Check if expected features are present
        if expected_features:
            for feature in expected_features:
                if feature not in pattern:
                    print(f"   ⚠️  Expected feature '{feature}' not found in pattern")
        
        # Success criteria
        success = (
            score > 0.6 and  # Reasonable score
            pos_matches >= len(positives) * 0.8 and  # Most positives match
            neg_matches >= len(negatives) * 0.8 and  # Most negatives rejected
            validation.is_valid  # Pattern is valid
        )
        
        if success:
            print("   ✅ PASSED")
        else:
            print("   ❌ FAILED")
            
        return success
        
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return False

def run_realistic_tests():
    """Run a suite of realistic test scenarios."""
    
    success_count = 0
    total_tests = 0
    
    # Test 1: Simple ID patterns
    total_tests += 1
    if test_scenario(
        "Simple ID Patterns",
        ["ID001", "ID002", "ID003", "ID999"],
        ["001", "ID", "ID1234", "id001"],
        expected_features=["ID", "[0-9]"]
    ):
        success_count += 1
    
    # Test 2: Phone numbers
    total_tests += 1
    if test_scenario(
        "US Phone Numbers",
        ["123-456-7890", "555-123-4567", "999-888-7777"],
        ["123-45-6789", "12345678901", "123.456.7890"],
        expected_features=["-", "[0-9]"]
    ):
        success_count += 1
    
    # Test 3: Simple codes
    total_tests += 1
    if test_scenario(
        "Product Codes",
        ["ABC123", "DEF456", "GHI789"],
        ["ABC12", "ABCD123", "abc123", "123ABC"],
        expected_features=["[A-Z]", "[0-9]"]
    ):
        success_count += 1
    
    # Test 4: Version numbers
    total_tests += 1
    if test_scenario(
        "Version Numbers",
        ["1.0.0", "2.1.3", "10.15.7"],
        ["1.0", "1.0.0.1", "v1.0.0", "1-0-0"],
        expected_features=["\\.", "[0-9]"]
    ):
        success_count += 1
    
    # Test 5: Simple file names
    total_tests += 1
    if test_scenario(
        "Log File Names",
        ["app.log", "error.log", "debug.log"],
        ["app.txt", "log", "app.log.1", "App.log"],
        expected_features=[".log"]
    ):
        success_count += 1
    
    # Test 6: Date patterns
    total_tests += 1
    if test_scenario(
        "ISO Dates",
        ["2023-01-15", "2023-12-31", "2024-06-01"],
        ["23-01-15", "2023/01/15", "2023-1-15", "2023-01-1"],
        expected_features=["-", "[0-9]"]
    ):
        success_count += 1
    
    # Test 7: Simple email patterns (basic)
    total_tests += 1
    if test_scenario(
        "Simple Email Addresses",
        ["user@test.com", "admin@site.org", "info@company.net"],
        ["user@test", "user.test.com", "@test.com", "user@"],
        expected_features=["@", "\\.", "[a-z]"]
    ):
        success_count += 1
    
    return success_count, total_tests

if __name__ == "__main__":
    print("🎯 RegexGenerator Realistic Examples Test")
    print("=" * 60)
    
    success_count, total_tests = run_realistic_tests()
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{total_tests} scenarios passed")
    
    if success_count == total_tests:
        print("🎉 All realistic scenarios passed!")
        print("RegexGenerator is working well for practical use cases!")
    elif success_count >= total_tests * 0.7:
        print("✅ Most scenarios passed - RegexGenerator is functional")
        print("Some edge cases may need refinement")
    else:
        print("⚠️  Many scenarios failed - algorithm needs more work")
        sys.exit(1)