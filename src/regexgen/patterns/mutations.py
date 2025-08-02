"""Pattern mutation operators for evolutionary regex generation."""

import random
import string
from typing import List, Set, Optional, Union
from abc import ABC, abstractmethod

from regexgen.patterns.ast import (
    PatternAST, PatternNode, LiteralNode, CharacterClassNode, 
    QuantifierNode, GroupNode, AlternationNode, WildcardNode, AnchorNode
)


class MutationOperator(ABC):
    """Abstract base class for pattern mutation operators."""
    
    @abstractmethod
    def can_apply(self, node: PatternNode) -> bool:
        """Check if this mutation can be applied to the given node."""
        pass
    
    @abstractmethod
    def apply(self, node: PatternNode) -> PatternNode:
        """Apply the mutation to the node and return the mutated version."""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the mutation operator."""
        pass


class LiteralToCharClassMutation(MutationOperator):
    """Convert a literal character to a character class."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return isinstance(node, LiteralNode) and len(node.value) == 1 and node.value.isalpha()
    
    def apply(self, node: PatternNode) -> PatternNode:
        if not isinstance(node, LiteralNode):
            return node
        
        char = node.value
        if char.islower():
            # Create lowercase character class
            return CharacterClassNode(characters={'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'})
        elif char.isupper():
            # Create uppercase character class
            return CharacterClassNode(characters={'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'})
        elif char.isdigit():
            # Create digit character class
            return CharacterClassNode(characters={'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'})
        else:
            return node
    
    @property
    def name(self) -> str:
        return "literal_to_char_class"


class CharClassToRangeMutation(MutationOperator):
    """Convert character class with consecutive characters to ranges."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return isinstance(node, CharacterClassNode) and len(node.characters) > 3
    
    def apply(self, node: PatternNode) -> PatternNode:
        if not isinstance(node, CharacterClassNode):
            return node
        
        chars = sorted(node.characters)
        ranges = []
        remaining_chars = set(node.characters)
        
        # Find consecutive sequences
        i = 0
        while i < len(chars):
            start_char = chars[i]
            end_char = start_char
            
            # Find end of consecutive sequence
            j = i + 1
            while j < len(chars) and ord(chars[j]) == ord(chars[j-1]) + 1:
                end_char = chars[j]
                j += 1
            
            # If we have 3+ consecutive chars, make it a range
            if j - i >= 3:
                ranges.append((start_char, end_char))
                for k in range(i, j):
                    remaining_chars.discard(chars[k])
            
            i = j if j > i + 1 else i + 1
        
        return CharacterClassNode(
            characters=remaining_chars,
            negated=node.negated,
            ranges=ranges + node.ranges
        )
    
    @property
    def name(self) -> str:
        return "char_class_to_range"


class AddQuantifierMutation(MutationOperator):
    """Add a quantifier to a node."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return not isinstance(node, (QuantifierNode, AnchorNode))
    
    def apply(self, node: PatternNode) -> PatternNode:
        quantifier_types = [
            (0, 1),      # ?
            (0, None),   # *
            (1, None),   # +
            (2, 4),      # {2,4}
            (1, 3),      # {1,3}
        ]
        
        min_count, max_count = random.choice(quantifier_types)
        return QuantifierNode(child=node.clone(), min_count=min_count, max_count=max_count)
    
    @property
    def name(self) -> str:
        return "add_quantifier"


class ModifyQuantifierMutation(MutationOperator):
    """Modify an existing quantifier."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return isinstance(node, QuantifierNode)
    
    def apply(self, node: PatternNode) -> PatternNode:
        if not isinstance(node, QuantifierNode):
            return node
        
        mutation_type = random.choice(['bounds', 'laziness'])
        
        if mutation_type == 'bounds':
            # Modify quantifier bounds
            new_min = max(0, node.min_count + random.choice([-1, 0, 1]))
            if node.max_count is None:
                new_max = None if random.random() < 0.7 else random.randint(new_min + 1, new_min + 5)
            else:
                new_max = max(new_min, node.max_count + random.choice([-1, 0, 1]))
                if new_max == new_min and random.random() < 0.3:
                    new_max = None
            
            return QuantifierNode(
                child=node.child.clone(),
                min_count=new_min,
                max_count=new_max,
                lazy=node.lazy
            )
        
        else:  # laziness
            return QuantifierNode(
                child=node.child.clone(),
                min_count=node.min_count,
                max_count=node.max_count,
                lazy=not node.lazy
            )
    
    @property
    def name(self) -> str:
        return "modify_quantifier"


class GroupingMutation(MutationOperator):
    """Add or remove grouping."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return True
    
    def apply(self, node: PatternNode) -> PatternNode:
        if isinstance(node, GroupNode):
            # Remove grouping
            return node.child.clone()
        else:
            # Add grouping
            capturing = random.choice([True, False])
            return GroupNode(child=node.clone(), capturing=capturing)
    
    @property
    def name(self) -> str:
        return "grouping"


class AlternationMutation(MutationOperator):
    """Create or modify alternations."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return True
    
    def apply(self, node: PatternNode) -> PatternNode:
        if isinstance(node, AlternationNode):
            # Modify existing alternation
            if len(node.alternatives) > 1 and random.random() < 0.3:
                # Remove one alternative
                new_alternatives = node.alternatives.copy()
                new_alternatives.pop(random.randint(0, len(new_alternatives) - 1))
                return AlternationNode(alternatives=[alt.clone() for alt in new_alternatives])
            else:
                # Add new alternative
                new_alt = self._generate_similar_pattern(node.alternatives[0])
                new_alternatives = [alt.clone() for alt in node.alternatives] + [new_alt]
                return AlternationNode(alternatives=new_alternatives)
        else:
            # Create new alternation
            similar_pattern = self._generate_similar_pattern(node)
            return AlternationNode(alternatives=[node.clone(), similar_pattern])
    
    def _generate_similar_pattern(self, node: PatternNode) -> PatternNode:
        """Generate a pattern similar to the given node."""
        if isinstance(node, LiteralNode):
            # Create similar literal
            if node.value.isalpha():
                new_char = random.choice(string.ascii_letters)
                return LiteralNode(new_char)
            elif node.value.isdigit():
                new_char = random.choice(string.digits)
                return LiteralNode(new_char)
            else:
                return LiteralNode(random.choice(string.printable[:62]))
        
        elif isinstance(node, CharacterClassNode):
            # Create similar character class with some overlap
            new_chars = set(random.sample(list(node.characters), min(3, len(node.characters))))
            new_chars.add(random.choice(string.ascii_letters))
            return CharacterClassNode(characters=new_chars)
        
        else:
            # For complex nodes, just create a simple literal
            return LiteralNode(random.choice(string.ascii_lowercase))
    
    @property
    def name(self) -> str:
        return "alternation"


class WildcardMutation(MutationOperator):
    """Convert between wildcard and character classes."""
    
    def can_apply(self, node: PatternNode) -> bool:
        return isinstance(node, (WildcardNode, CharacterClassNode, LiteralNode))
    
    def apply(self, node: PatternNode) -> PatternNode:
        if isinstance(node, WildcardNode):
            # Convert wildcard to character class
            char_sets = [
                set(string.ascii_lowercase),
                set(string.ascii_uppercase),
                set(string.digits),
                set(string.ascii_letters),
                set(string.printable[:62])
            ]
            return CharacterClassNode(characters=random.choice(char_sets))
        
        elif isinstance(node, CharacterClassNode):
            # Sometimes convert to wildcard
            if random.random() < 0.2:
                return WildcardNode()
            else:
                return node
        
        elif isinstance(node, LiteralNode):
            # Convert literal to wildcard
            return WildcardNode()
        
        return node
    
    @property
    def name(self) -> str:
        return "wildcard"


class PatternMutator:
    """Main class for applying mutations to patterns."""
    
    def __init__(self, mutation_rate: float = 0.1):
        self.mutation_rate = mutation_rate
        self.operators = [
            LiteralToCharClassMutation(),
            CharClassToRangeMutation(),
            AddQuantifierMutation(),
            ModifyQuantifierMutation(),
            GroupingMutation(),
            AlternationMutation(),
            WildcardMutation(),
        ]
    
    def mutate(self, pattern: PatternAST) -> PatternAST:
        """Apply random mutations to a pattern."""
        new_pattern = pattern.clone()
        
        # Collect all nodes in the pattern
        nodes = self._collect_nodes(new_pattern.root)
        
        # Apply mutations with the given probability
        for i, node in enumerate(nodes):
            if random.random() < self.mutation_rate:
                applicable_ops = [op for op in self.operators if op.can_apply(node)]
                if applicable_ops:
                    chosen_op = random.choice(applicable_ops)
                    mutated_node = chosen_op.apply(node)
                    nodes[i] = mutated_node
        
        # Rebuild pattern from mutated nodes
        # For simplicity, if we mutated the root, use that
        if nodes and len(nodes) > 0:
            new_pattern.root = nodes[0]
        
        return new_pattern
    
    def _collect_nodes(self, root: PatternNode) -> List[PatternNode]:
        """Collect all nodes in the pattern tree."""
        nodes = [root]
        
        if isinstance(root, (QuantifierNode, GroupNode)):
            nodes.extend(self._collect_nodes(root.child))
        elif isinstance(root, AlternationNode):
            for alt in root.alternatives:
                nodes.extend(self._collect_nodes(alt))
        
        return nodes
    
    def generate_random_pattern(self, max_complexity: int = 20) -> PatternAST:
        """Generate a completely random pattern."""
        complexity_budget = max_complexity
        root = self._generate_random_node(complexity_budget)
        return PatternAST(root)
    
    def _generate_random_node(self, complexity_budget: int) -> PatternNode:
        """Generate a random pattern node within complexity budget."""
        if complexity_budget <= 1:
            # Generate simple node
            node_type = random.choice(['literal', 'char_class', 'wildcard'])
            
            if node_type == 'literal':
                char = random.choice(string.ascii_letters + string.digits)
                return LiteralNode(char)
            elif node_type == 'char_class':
                chars = set(random.sample(string.ascii_lowercase, random.randint(2, 5)))
                return CharacterClassNode(characters=chars)
            else:  # wildcard
                return WildcardNode()
        
        else:
            # Generate complex node
            node_type = random.choice(['quantifier', 'group', 'alternation', 'simple'])
            
            if node_type == 'quantifier':
                child = self._generate_random_node(complexity_budget - 2)
                min_count = random.randint(0, 3)
                max_count = None if random.random() < 0.3 else random.randint(min_count, min_count + 5)
                return QuantifierNode(child=child, min_count=min_count, max_count=max_count)
            
            elif node_type == 'group':
                child = self._generate_random_node(complexity_budget - 2)
                return GroupNode(child=child, capturing=random.choice([True, False]))
            
            elif node_type == 'alternation':
                max_alts = max(2, min(4, complexity_budget // 2))
                num_alts = random.randint(2, max_alts) if max_alts > 2 else 2
                alt_budget = max(1, (complexity_budget - 1) // num_alts)
                alternatives = [
                    self._generate_random_node(alt_budget) 
                    for _ in range(num_alts)
                ]
                return AlternationNode(alternatives=alternatives)
            
            else:  # simple
                return self._generate_random_node(1)