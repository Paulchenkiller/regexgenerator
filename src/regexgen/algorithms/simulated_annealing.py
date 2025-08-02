"""Simulated Annealing algorithm for regex pattern optimization."""

import math
import random
import time
from dataclasses import dataclass
from typing import List, Optional, Callable, Dict, Any
from enum import Enum

# import numpy as np  # Optional for now

from regexgen.patterns.ast import PatternAST
from regexgen.patterns.mutations import PatternMutator
from regexgen.scoring.fitness import FitnessScorer, FitnessResult, ScoringMode


class CoolingSchedule(Enum):
    """Different cooling schedules for simulated annealing."""
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    ADAPTIVE = "adaptive"


@dataclass
class SAConfig:
    """Configuration for Simulated Annealing algorithm."""
    initial_temperature: float = 10.0  # Lower for more focused search
    final_temperature: float = 0.01
    max_iterations: int = 1000
    max_no_improvement: int = 150  # Allow more patience
    cooling_schedule: CoolingSchedule = CoolingSchedule.ADAPTIVE  # Better convergence
    mutation_rate: float = 0.15  # Slightly higher mutation rate
    max_complexity: int = 50
    random_seed: Optional[int] = None
    timeout_seconds: Optional[float] = None


@dataclass
class SAResult:
    """Result from simulated annealing optimization."""
    best_pattern: PatternAST
    best_fitness: FitnessResult
    iterations: int
    time_seconds: float
    temperature_history: List[float]
    fitness_history: List[float]
    accepted_moves: int
    rejected_moves: int
    convergence_reason: str
    final_temperature: float


class TemperatureScheduler:
    """Handles different cooling schedules for simulated annealing."""
    
    def __init__(self, config: SAConfig):
        self.config = config
        self.initial_temp = config.initial_temperature
        self.final_temp = config.final_temperature
        self.max_iterations = config.max_iterations
        
        # For adaptive cooling
        self.last_improvement_iteration = 0
        self.stagnation_threshold = max(50, config.max_iterations // 20)
    
    def get_temperature(self, iteration: int, last_improvement_iter: int = 0) -> float:
        """Get temperature for given iteration."""
        if self.config.cooling_schedule == CoolingSchedule.LINEAR:
            return self._linear_cooling(iteration)
        elif self.config.cooling_schedule == CoolingSchedule.EXPONENTIAL:
            return self._exponential_cooling(iteration)
        elif self.config.cooling_schedule == CoolingSchedule.LOGARITHMIC:
            return self._logarithmic_cooling(iteration)
        elif self.config.cooling_schedule == CoolingSchedule.ADAPTIVE:
            return self._adaptive_cooling(iteration, last_improvement_iter)
        else:
            return self._exponential_cooling(iteration)
    
    def _linear_cooling(self, iteration: int) -> float:
        """Linear cooling schedule."""
        progress = iteration / self.max_iterations
        return self.initial_temp * (1.0 - progress)
    
    def _exponential_cooling(self, iteration: int) -> float:
        """Exponential cooling schedule."""
        # Calculate cooling rate to reach final temperature
        cooling_rate = (self.final_temp / self.initial_temp) ** (1.0 / self.max_iterations)
        return self.initial_temp * (cooling_rate ** iteration)
    
    def _logarithmic_cooling(self, iteration: int) -> float:
        """Logarithmic cooling schedule."""
        if iteration == 0:
            return self.initial_temp
        return self.initial_temp / math.log(iteration + 1)
    
    def _adaptive_cooling(self, iteration: int, last_improvement_iter: int) -> float:
        """Adaptive cooling that slows down when not improving."""
        base_temp = self._exponential_cooling(iteration)
        
        # If we haven't improved recently, slow down cooling
        stagnation_time = iteration - last_improvement_iter
        if stagnation_time > self.stagnation_threshold:
            slowdown_factor = 1.5 + (stagnation_time - self.stagnation_threshold) / 100
            base_temp *= slowdown_factor
        
        return max(base_temp, self.final_temp)


class SimulatedAnnealing:
    """Simulated Annealing optimizer for regex patterns."""
    
    def __init__(self, config: SAConfig = None):
        self.config = config or SAConfig()
        self.mutator = PatternMutator(mutation_rate=self.config.mutation_rate)
        self.scheduler = TemperatureScheduler(self.config)
        
        if self.config.random_seed is not None:
            random.seed(self.config.random_seed)
            # np.random.seed(self.config.random_seed)  # Optional
    
    def optimize(
        self,
        positive_examples: List[str],
        negative_examples: List[str],
        fitness_scorer: FitnessScorer,
        initial_pattern: Optional[PatternAST] = None
    ) -> SAResult:
        """Run simulated annealing optimization."""
        start_time = time.time()
        
        # Initialize current solution
        if initial_pattern is None:
            current_pattern = self.mutator.generate_random_pattern(
                max_complexity=self.config.max_complexity // 2,
                examples=positive_examples
            )
        else:
            current_pattern = initial_pattern.clone()
        
        current_fitness = fitness_scorer.score(current_pattern, positive_examples, negative_examples)
        
        # Initialize best solution
        best_pattern = current_pattern.clone()
        best_fitness = current_fitness
        
        # Tracking variables
        temperature_history = []
        fitness_history = []
        accepted_moves = 0
        rejected_moves = 0
        last_improvement_iteration = 0
        no_improvement_count = 0
        
        # Main optimization loop
        for iteration in range(self.config.max_iterations):
            # Check timeout
            if self.config.timeout_seconds and (time.time() - start_time) > self.config.timeout_seconds:
                convergence_reason = "timeout"
                break
            
            # Get current temperature
            temperature = self.scheduler.get_temperature(iteration, last_improvement_iteration)
            temperature_history.append(temperature)
            
            # Generate neighbor solution
            neighbor_pattern = self.mutator.mutate(current_pattern)
            
            # Ensure pattern is within complexity limits
            if neighbor_pattern.complexity() > self.config.max_complexity:
                rejected_moves += 1
                fitness_history.append(current_fitness.total_score)
                continue
            
            # Evaluate neighbor
            neighbor_fitness = fitness_scorer.score(neighbor_pattern, positive_examples, negative_examples)
            
            # Decide whether to accept the neighbor
            accept = self._should_accept(
                current_fitness.total_score,
                neighbor_fitness.total_score,
                temperature
            )
            
            if accept:
                current_pattern = neighbor_pattern
                current_fitness = neighbor_fitness
                accepted_moves += 1
                
                # Check if this is the best solution so far
                if neighbor_fitness.total_score > best_fitness.total_score:
                    best_pattern = neighbor_pattern.clone()
                    best_fitness = neighbor_fitness
                    last_improvement_iteration = iteration
                    no_improvement_count = 0
                else:
                    no_improvement_count += 1
            else:
                rejected_moves += 1
                no_improvement_count += 1
            
            fitness_history.append(current_fitness.total_score)
            
            # Check for early convergence
            if no_improvement_count >= self.config.max_no_improvement:
                convergence_reason = "no_improvement"
                break
            
            # Check if we found a perfect solution
            if (best_fitness.total_score >= 0.999 and 
                best_fitness.positive_matches == len(positive_examples) and
                best_fitness.negative_matches == len(negative_examples)):
                convergence_reason = "perfect_solution"
                break
            
            # Check for temperature convergence
            if temperature < self.config.final_temperature:
                convergence_reason = "temperature_converged"
                break
        
        else:
            convergence_reason = "max_iterations"
        
        total_time = time.time() - start_time
        
        return SAResult(
            best_pattern=best_pattern,
            best_fitness=best_fitness,
            iterations=iteration + 1,
            time_seconds=total_time,
            temperature_history=temperature_history,
            fitness_history=fitness_history,
            accepted_moves=accepted_moves,
            rejected_moves=rejected_moves,
            convergence_reason=convergence_reason,
            final_temperature=temperature_history[-1] if temperature_history else 0.0
        )
    
    def _should_accept(self, current_score: float, neighbor_score: float, temperature: float) -> bool:
        """Decide whether to accept a neighbor solution."""
        if neighbor_score > current_score:
            # Always accept better solutions
            return True
        
        if temperature <= 0:
            # No randomness at zero temperature
            return False
        
        # Accept worse solutions with probability based on temperature
        delta = neighbor_score - current_score
        probability = math.exp(delta / temperature)
        return random.random() < probability
    
    def optimize_with_restarts(
        self,
        positive_examples: List[str],
        negative_examples: List[str],
        fitness_scorer: FitnessScorer,
        num_restarts: int = 3
    ) -> SAResult:
        """Run multiple SA optimizations and return the best result."""
        best_result = None
        
        for restart in range(num_restarts):
            # Use different random seeds for each restart if original seed was set
            if self.config.random_seed is not None:
                current_seed = self.config.random_seed + restart
                random.seed(current_seed)
                # np.random.seed(current_seed)  # Optional
            
            result = self.optimize(positive_examples, negative_examples, fitness_scorer)
            
            if best_result is None or result.best_fitness.total_score > best_result.best_fitness.total_score:
                best_result = result
                # Add restart information
                best_result.convergence_reason += f" (restart {restart + 1}/{num_restarts})"
        
        return best_result
    
    def get_optimization_stats(self, result: SAResult) -> Dict[str, Any]:
        """Get detailed statistics from optimization result."""
        return {
            "final_score": result.best_fitness.total_score,
            "correctness_score": result.best_fitness.correctness_score,
            "complexity_score": result.best_fitness.complexity_score,
            "readability_score": result.best_fitness.readability_score,
            "performance_score": result.best_fitness.performance_score,
            "pattern_complexity": result.best_pattern.complexity(),
            "pattern_regex": result.best_pattern.to_regex(),
            "iterations": result.iterations,
            "time_seconds": result.time_seconds,
            "accepted_moves": result.accepted_moves,
            "rejected_moves": result.rejected_moves,
            "acceptance_rate": result.accepted_moves / (result.accepted_moves + result.rejected_moves),
            "convergence_reason": result.convergence_reason,
            "final_temperature": result.final_temperature,
            "positive_match_rate": result.best_fitness.positive_matches / result.best_fitness.positive_total,
            "negative_match_rate": result.best_fitness.negative_matches / result.best_fitness.negative_total,
        }