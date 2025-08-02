"""Pattern validation and testing system."""

import re
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import threading
# import numpy as np  # Optional for now

from regexgen.patterns.ast import PatternAST


@dataclass
class ValidationResult:
    """Result of pattern validation."""
    is_valid: bool
    regex_string: str
    compilation_error: Optional[str]
    positive_matches: List[str]
    positive_failures: List[str]
    negative_matches: List[str]  # Should be empty for valid patterns
    negative_failures: List[str]  # Should contain all negative examples
    execution_time_ms: float
    pattern_length: int
    pattern_complexity: int
    timeout_occurred: bool
    performance_warnings: List[str]


class PatternValidator:
    """Validates regex patterns against examples and performance criteria."""
    
    def __init__(self, timeout_seconds: float = 2.0):
        self.timeout_seconds = timeout_seconds
    
    def validate(
        self,
        pattern: PatternAST,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> ValidationResult:
        """Validate a pattern against examples."""
        start_time = time.time()
        
        # Convert pattern to regex string
        try:
            regex_string = pattern.to_regex()
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                regex_string="",
                compilation_error=f"Pattern conversion error: {str(e)}",
                positive_matches=[],
                positive_failures=positive_examples.copy(),
                negative_matches=[],
                negative_failures=[],
                execution_time_ms=0.0,
                pattern_length=0,
                pattern_complexity=0,
                timeout_occurred=False,
                performance_warnings=[]
            )
        
        # Try to compile the regex
        try:
            compiled_pattern = re.compile(regex_string)
        except re.error as e:
            return ValidationResult(
                is_valid=False,
                regex_string=regex_string,
                compilation_error=f"Regex compilation error: {str(e)}",
                positive_matches=[],
                positive_failures=positive_examples.copy(),
                negative_matches=[],
                negative_failures=[],
                execution_time_ms=0.0,
                pattern_length=len(regex_string),
                pattern_complexity=pattern.complexity(),
                timeout_occurred=False,
                performance_warnings=[]
            )
        
        # Test the pattern
        timeout_occurred = False
        performance_warnings = []
        
        try:
            # Test with timeout
            positive_matches, positive_failures, negative_matches, negative_failures, perf_warnings = self._test_pattern_with_timeout(
                compiled_pattern, positive_examples, negative_examples
            )
            performance_warnings.extend(perf_warnings)
            
        except TimeoutError:
            timeout_occurred = True
            positive_matches = []
            positive_failures = positive_examples.copy()
            negative_matches = negative_examples.copy()  # Assume all matched due to timeout
            negative_failures = []
            performance_warnings.append("Pattern execution timed out - possible catastrophic backtracking")
        
        execution_time = (time.time() - start_time) * 1000
        
        # Check if pattern is valid
        is_valid = (
            not timeout_occurred and
            len(positive_failures) == 0 and
            len(negative_matches) == 0 and
            len(performance_warnings) == 0
        )
        
        return ValidationResult(
            is_valid=is_valid,
            regex_string=regex_string,
            compilation_error=None,
            positive_matches=positive_matches,
            positive_failures=positive_failures,
            negative_matches=negative_matches,
            negative_failures=negative_failures,
            execution_time_ms=execution_time,
            pattern_length=len(regex_string),
            pattern_complexity=pattern.complexity(),
            timeout_occurred=timeout_occurred,
            performance_warnings=performance_warnings
        )
    
    def _test_pattern_with_timeout(
        self,
        compiled_pattern: re.Pattern,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> tuple:
        """Test pattern with timeout protection."""
        result = [None]
        exception = [None]
        
        def test_function():
            try:
                result[0] = self._test_pattern(compiled_pattern, positive_examples, negative_examples)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=test_function)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout_seconds)
        
        if thread.is_alive():
            # Thread is still running, pattern likely has performance issues
            raise TimeoutError("Pattern execution timed out")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _test_pattern(
        self,
        compiled_pattern: re.Pattern,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> tuple:
        """Test pattern against examples."""
        positive_matches = []
        positive_failures = []
        negative_matches = []
        negative_failures = []
        performance_warnings = []
        
        # Test positive examples (should match)
        for example in positive_examples:
            start_time = time.time()
            
            try:
                if compiled_pattern.fullmatch(example):
                    positive_matches.append(example)
                else:
                    positive_failures.append(example)
                
                # Check for slow execution
                execution_time = time.time() - start_time
                if execution_time > 0.1:  # 100ms threshold
                    performance_warnings.append(
                        f"Slow execution on positive example '{example}': {execution_time:.3f}s"
                    )
                    
            except Exception as e:
                positive_failures.append(example)
                performance_warnings.append(f"Exception on positive example '{example}': {str(e)}")
        
        # Test negative examples (should NOT match)
        for example in negative_examples:
            start_time = time.time()
            
            try:
                if compiled_pattern.fullmatch(example):
                    negative_matches.append(example)
                else:
                    negative_failures.append(example)
                
                # Check for slow execution
                execution_time = time.time() - start_time
                if execution_time > 0.1:  # 100ms threshold
                    performance_warnings.append(
                        f"Slow execution on negative example '{example}': {execution_time:.3f}s"
                    )
                    
            except Exception as e:
                negative_failures.append(example)
                performance_warnings.append(f"Exception on negative example '{example}': {str(e)}")
        
        return positive_matches, positive_failures, negative_matches, negative_failures, performance_warnings
    
    def quick_validate(self, pattern: PatternAST) -> bool:
        """Quick validation - just check if pattern compiles."""
        try:
            regex_string = pattern.to_regex()
            re.compile(regex_string)
            return True
        except:
            return False
    
    def analyze_pattern_safety(self, pattern: PatternAST) -> Dict[str, Any]:
        """Analyze pattern for potential performance issues."""
        regex_string = pattern.to_regex()
        
        warnings = []
        risk_score = 0
        
        # Check for nested quantifiers (high risk for catastrophic backtracking)
        nested_quantifiers = self._find_nested_quantifiers(regex_string)
        if nested_quantifiers:
            warnings.append("Nested quantifiers detected - high risk of catastrophic backtracking")
            risk_score += 5
        
        # Check for alternation with overlapping branches
        if '|' in regex_string:
            warnings.append("Alternation detected - potential for backtracking")
            risk_score += 1
        
        # Check for complex character classes
        char_class_count = regex_string.count('[')
        if char_class_count > 3:
            warnings.append(f"Many character classes ({char_class_count}) - may impact performance")
            risk_score += 1
        
        # Check for unbounded quantifiers
        unbounded_count = regex_string.count('*') + regex_string.count('+')
        if unbounded_count > 2:
            warnings.append(f"Multiple unbounded quantifiers ({unbounded_count}) - potential performance issue")
            risk_score += 2
        
        # Check for very long patterns
        if len(regex_string) > 100:
            warnings.append(f"Very long pattern ({len(regex_string)} chars) - may be hard to understand")
            risk_score += 1
        
        # Determine risk level
        if risk_score == 0:
            risk_level = "low"
        elif risk_score <= 2:
            risk_level = "medium"
        elif risk_score <= 5:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "warnings": warnings,
            "pattern_length": len(regex_string),
            "pattern_complexity": pattern.complexity(),
            "nested_quantifiers": nested_quantifiers,
            "alternation_count": regex_string.count('|'),
            "quantifier_count": unbounded_count,
            "character_class_count": char_class_count
        }
    
    def _find_nested_quantifiers(self, regex_string: str) -> List[str]:
        """Find potentially problematic nested quantifier patterns."""
        nested_patterns = []
        
        # Look for patterns like (.*)+, (.*)*, (a+)+, etc.
        problematic_patterns = [
            r'\([^)]*[*+][^)]*\)[*+]',  # (stuff*)+, (stuff+)*, etc.
            r'[*+][^)]*\)',  # Quantifier followed by something and then )
        ]
        
        for pattern in problematic_patterns:
            matches = re.findall(pattern, regex_string)
            nested_patterns.extend(matches)
        
        return nested_patterns
    
    def benchmark_pattern(
        self,
        pattern: PatternAST,
        test_strings: List[str],
        iterations: int = 100
    ) -> Dict[str, float]:
        """Benchmark pattern performance."""
        try:
            compiled_pattern = re.compile(pattern.to_regex())
        except re.error:
            return {"error": "Pattern compilation failed"}
        
        if not test_strings:
            return {"error": "No test strings provided"}
        
        times = []
        successful_runs = 0
        
        for _ in range(iterations):
            start_time = time.time()
            
            try:
                for test_string in test_strings:
                    compiled_pattern.fullmatch(test_string)
                
                end_time = time.time()
                times.append(end_time - start_time)
                successful_runs += 1
                
            except Exception:
                # Skip failed runs
                continue
        
        if not times:
            return {"error": "All benchmark runs failed"}
        
        # Simple statistics without numpy
        mean_time = sum(times) / len(times)
        sorted_times = sorted(times)
        median_time = sorted_times[len(sorted_times) // 2]
        min_time = min(times)
        max_time = max(times)
        
        return {
            "successful_runs": successful_runs,
            "total_runs": iterations,
            "success_rate": successful_runs / iterations,
            "mean_time_ms": float(mean_time * 1000),
            "median_time_ms": float(median_time * 1000),
            "min_time_ms": float(min_time * 1000),
            "max_time_ms": float(max_time * 1000),
            "total_strings_tested": len(test_strings) * successful_runs
        }