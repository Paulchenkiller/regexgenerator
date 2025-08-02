"""Fitness scoring system for evaluating regex patterns."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any
import re
import time
# import numpy as np  # Optional for now

from regexgen.patterns.ast import PatternAST


class ScoringMode(Enum):
    """Different scoring modes for pattern evaluation."""
    MINIMAL = "minimal"      # Prioritize shortest patterns
    READABLE = "readable"    # Prioritize human-readable patterns
    BALANCED = "balanced"    # Balance between minimal and readable


@dataclass
class FitnessResult:
    """Result of fitness evaluation."""
    total_score: float
    correctness_score: float
    complexity_score: float
    readability_score: float
    performance_score: float
    positive_matches: int
    negative_matches: int
    positive_total: int
    negative_total: int
    evaluation_time_ms: float
    timeout_occurred: bool = False
    compilation_error: Optional[str] = None


class FitnessScorer(ABC):
    """Abstract base class for fitness scoring strategies."""
    
    @abstractmethod
    def score(
        self,
        pattern: PatternAST,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> FitnessResult:
        """Evaluate the fitness of a pattern against examples."""
        pass


class MultiCriteriaScorer(FitnessScorer):
    """Multi-criteria fitness scorer with configurable weights."""
    
    def __init__(
        self,
        mode: ScoringMode = ScoringMode.BALANCED,
        correctness_weight: float = None,
        complexity_weight: float = None,
        readability_weight: float = None,
        performance_weight: float = None,
        timeout_seconds: float = 1.0
    ):
        self.mode = mode
        self.timeout_seconds = timeout_seconds
        
        # Set weights based on mode if not explicitly provided
        if mode == ScoringMode.MINIMAL:
            self.correctness_weight = correctness_weight or 0.6
            self.complexity_weight = complexity_weight or 0.3
            self.readability_weight = readability_weight or 0.05
            self.performance_weight = performance_weight or 0.05
        elif mode == ScoringMode.READABLE:
            self.correctness_weight = correctness_weight or 0.5
            self.complexity_weight = complexity_weight or 0.1
            self.readability_weight = readability_weight or 0.3
            self.performance_weight = performance_weight or 0.1
        else:  # BALANCED
            self.correctness_weight = correctness_weight or 0.5
            self.complexity_weight = complexity_weight or 0.2
            self.readability_weight = readability_weight or 0.2
            self.performance_weight = performance_weight or 0.1
        
        # Normalize weights
        total_weight = (
            self.correctness_weight + self.complexity_weight +
            self.readability_weight + self.performance_weight
        )
        self.correctness_weight /= total_weight
        self.complexity_weight /= total_weight
        self.readability_weight /= total_weight
        self.performance_weight /= total_weight
    
    def score(
        self,
        pattern: PatternAST,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> FitnessResult:
        """Evaluate pattern fitness using multiple criteria."""
        start_time = time.time()
        
        # Try to compile the pattern
        try:
            regex_str = pattern.to_regex()
            compiled_pattern = re.compile(regex_str)
        except re.error as e:
            return FitnessResult(
                total_score=0.0,
                correctness_score=0.0,
                complexity_score=0.0,
                readability_score=0.0,
                performance_score=0.0,
                positive_matches=0,
                negative_matches=0,
                positive_total=len(positive_examples),
                negative_total=len(negative_examples),
                evaluation_time_ms=0.0,
                compilation_error=str(e)
            )
        
        # Evaluate correctness
        correctness_result = self._evaluate_correctness(
            compiled_pattern, positive_examples, negative_examples
        )
        
        # Evaluate complexity
        complexity_score = self._evaluate_complexity(pattern)
        
        # Evaluate readability
        readability_score = self._evaluate_readability(pattern, regex_str)
        
        # Evaluate performance
        performance_result = self._evaluate_performance(
            compiled_pattern, positive_examples + negative_examples
        )
        
        # Calculate total score
        total_score = (
            self.correctness_weight * correctness_result['score'] +
            self.complexity_weight * complexity_score +
            self.readability_weight * readability_score +
            self.performance_weight * performance_result['score']
        )
        
        evaluation_time = (time.time() - start_time) * 1000
        
        return FitnessResult(
            total_score=total_score,
            correctness_score=correctness_result['score'],
            complexity_score=complexity_score,
            readability_score=readability_score,
            performance_score=performance_result['score'],
            positive_matches=correctness_result['positive_matches'],
            negative_matches=correctness_result['negative_matches'],
            positive_total=len(positive_examples),
            negative_total=len(negative_examples),
            evaluation_time_ms=evaluation_time,
            timeout_occurred=performance_result['timeout_occurred']
        )
    
    def _evaluate_correctness(
        self,
        compiled_pattern: re.Pattern,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> Dict[str, Any]:
        """Evaluate how well the pattern matches the examples."""
        positive_matches = 0
        negative_matches = 0
        
        # Test positive examples (should match)
        for example in positive_examples:
            if compiled_pattern.fullmatch(example):
                positive_matches += 1
        
        # Test negative examples (should NOT match)
        for example in negative_examples:
            if not compiled_pattern.fullmatch(example):
                negative_matches += 1
        
        # Calculate correctness score with heavy emphasis on positive matches
        total_positive = len(positive_examples)
        total_negative = len(negative_examples)
        
        if total_positive == 0 and total_negative == 0:
            score = 1.0
        elif total_positive == 0:
            score = negative_matches / total_negative if total_negative > 0 else 1.0
        elif total_negative == 0:
            score = positive_matches / total_positive
        else:
            positive_ratio = positive_matches / total_positive
            negative_ratio = negative_matches / total_negative if total_negative > 0 else 1.0
            
            # Weight positive matches much more heavily (80% vs 20%)
            score = 0.8 * positive_ratio + 0.2 * negative_ratio
            
            # If no positive matches, severely penalize
            if positive_matches == 0:
                score *= 0.1
        
        return {
            'score': score,
            'positive_matches': positive_matches,
            'negative_matches': negative_matches
        }
    
    def _evaluate_complexity(self, pattern: PatternAST) -> float:
        """Evaluate pattern complexity (lower is better)."""
        complexity = pattern.complexity()
        
        # Normalize complexity score (inverse relationship)
        # Use sigmoid-like function to map complexity to [0, 1]
        max_reasonable_complexity = 100
        normalized_complexity = complexity / max_reasonable_complexity
        score = 1.0 / (1.0 + normalized_complexity)
        
        return score
    
    def _evaluate_readability(self, pattern: PatternAST, regex_str: str) -> float:
        """Evaluate pattern readability."""
        readability_score = 1.0
        
        # Penalize deeply nested structures
        nesting_depth = self._calculate_nesting_depth(pattern)
        if nesting_depth > 3:
            readability_score *= 0.8 ** (nesting_depth - 3)
        
        # Penalize very long patterns
        if len(regex_str) > 50:
            readability_score *= 0.9 ** ((len(regex_str) - 50) / 10)
        
        # Penalize complex quantifiers
        complex_quantifier_count = regex_str.count('{')
        if complex_quantifier_count > 2:
            readability_score *= 0.95 ** (complex_quantifier_count - 2)
        
        # Penalize excessive alternations
        alternation_count = regex_str.count('|')
        if alternation_count > 3:
            readability_score *= 0.9 ** (alternation_count - 3)
        
        return max(0.0, min(1.0, readability_score))
    
    def _evaluate_performance(
        self,
        compiled_pattern: re.Pattern,
        test_strings: List[str]
    ) -> Dict[str, Any]:
        """Evaluate pattern performance (execution speed)."""
        if not test_strings:
            return {'score': 1.0, 'timeout_occurred': False}
        
        start_time = time.time()
        timeout_occurred = False
        
        try:
            # Test pattern against a subset of strings
            test_sample = test_strings[:min(100, len(test_strings))]
            
            for test_string in test_sample:
                if time.time() - start_time > self.timeout_seconds:
                    timeout_occurred = True
                    break
                
                # Test both fullmatch and search to detect potential backtracking
                compiled_pattern.fullmatch(test_string)
                compiled_pattern.search(test_string)
            
            execution_time = time.time() - start_time
            
            # Score based on execution time
            if timeout_occurred:
                score = 0.0
            else:
                # Normalize execution time (lower is better)
                max_acceptable_time = self.timeout_seconds / 2
                normalized_time = execution_time / max_acceptable_time
                score = 1.0 / (1.0 + normalized_time)
            
        except Exception:
            # Pattern caused an error during execution
            score = 0.0
            timeout_occurred = True
        
        return {
            'score': score,
            'timeout_occurred': timeout_occurred
        }
    
    def _calculate_nesting_depth(self, pattern: PatternAST) -> int:
        """Calculate the maximum nesting depth of the pattern."""
        from regexgen.patterns.ast import GroupNode, QuantifierNode
        
        def _depth(node, current_depth=0):
            if isinstance(node, (GroupNode, QuantifierNode)):
                return _depth(node.child, current_depth + 1)
            elif hasattr(node, 'alternatives'):  # AlternationNode
                return max(_depth(alt, current_depth) for alt in node.alternatives)
            else:
                return current_depth
        
        return _depth(pattern.root)


class SimpleFitnessScorer(FitnessScorer):
    """Simple fitness scorer that only considers correctness."""
    
    def score(
        self,
        pattern: PatternAST,
        positive_examples: List[str],
        negative_examples: List[str]
    ) -> FitnessResult:
        """Simple scoring based only on correctness."""
        start_time = time.time()
        
        try:
            regex_str = pattern.to_regex()
            compiled_pattern = re.compile(regex_str)
        except re.error as e:
            return FitnessResult(
                total_score=0.0,
                correctness_score=0.0,
                complexity_score=0.0,
                readability_score=0.0,
                performance_score=0.0,
                positive_matches=0,
                negative_matches=0,
                positive_total=len(positive_examples),
                negative_total=len(negative_examples),
                evaluation_time_ms=0.0,
                compilation_error=str(e)
            )
        
        positive_matches = sum(
            1 for ex in positive_examples 
            if compiled_pattern.fullmatch(ex)
        )
        
        negative_matches = sum(
            1 for ex in negative_examples 
            if not compiled_pattern.fullmatch(ex)
        )
        
        total_correct = positive_matches + negative_matches
        total_examples = len(positive_examples) + len(negative_examples)
        
        score = total_correct / total_examples if total_examples > 0 else 1.0
        
        evaluation_time = (time.time() - start_time) * 1000
        
        return FitnessResult(
            total_score=score,
            correctness_score=score,
            complexity_score=0.0,
            readability_score=0.0,
            performance_score=0.0,
            positive_matches=positive_matches,
            negative_matches=negative_matches,
            positive_total=len(positive_examples),
            negative_total=len(negative_examples),
            evaluation_time_ms=evaluation_time
        )