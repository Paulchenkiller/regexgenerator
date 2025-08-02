"""Abstract Syntax Tree representation for regex patterns."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Set, Union, Optional
import re


class PatternType(Enum):
    """Types of regex pattern nodes."""
    LITERAL = "literal"
    CHARACTER_CLASS = "character_class"
    QUANTIFIER = "quantifier"
    GROUP = "group"
    ALTERNATION = "alternation"
    ANCHOR = "anchor"
    WILDCARD = "wildcard"


@dataclass
class PatternNode(ABC):
    """Base class for all pattern AST nodes."""
    
    @abstractmethod
    def to_regex(self) -> str:
        """Convert this node to a regex string."""
        pass
    
    @abstractmethod
    def complexity(self) -> int:
        """Calculate the complexity score of this node."""
        pass
    
    @abstractmethod
    def clone(self) -> 'PatternNode':
        """Create a deep copy of this node."""
        pass


@dataclass
class LiteralNode(PatternNode):
    """Represents a literal string in the pattern."""
    value: str
    
    def to_regex(self) -> str:
        return re.escape(self.value)
    
    def complexity(self) -> int:
        return len(self.value)
    
    def clone(self) -> 'LiteralNode':
        return LiteralNode(self.value)


@dataclass
class CharacterClassNode(PatternNode):
    """Represents a character class like [abc] or [a-z]."""
    characters: Set[str]
    negated: bool = False
    ranges: List[tuple[str, str]] = None
    
    def __post_init__(self):
        if self.ranges is None:
            self.ranges = []
    
    def to_regex(self) -> str:
        if not self.characters and not self.ranges:
            return ""
        
        bracket_content = ""
        
        # Add individual characters
        if self.characters:
            # Sort for consistency and escape special characters
            chars = sorted(self.characters)
            escaped_chars = []
            for char in chars:
                if char in "\\^-]":
                    escaped_chars.append("\\" + char)
                else:
                    escaped_chars.append(char)
            bracket_content += "".join(escaped_chars)
        
        # Add ranges
        for start, end in self.ranges:
            bracket_content += f"{start}-{end}"
        
        # Handle negation
        prefix = "^" if self.negated else ""
        
        return f"[{prefix}{bracket_content}]"
    
    def complexity(self) -> int:
        return 2 + len(self.characters) + len(self.ranges)  # Base cost for brackets
    
    def clone(self) -> 'CharacterClassNode':
        return CharacterClassNode(
            characters=self.characters.copy(),
            negated=self.negated,
            ranges=self.ranges.copy()
        )


@dataclass 
class QuantifierNode(PatternNode):
    """Represents quantifiers like *, +, ?, {n,m}."""
    child: PatternNode
    min_count: int
    max_count: Optional[int]  # None means unlimited
    lazy: bool = False
    
    def to_regex(self) -> str:
        child_regex = self.child.to_regex()
        
        # Wrap child in non-capturing group if necessary
        if isinstance(self.child, (AlternationNode, GroupNode)):
            child_regex = f"(?:{child_regex})"
        
        # Generate quantifier suffix
        if self.min_count == 0 and self.max_count == 1:
            suffix = "?"
        elif self.min_count == 0 and self.max_count is None:
            suffix = "*"
        elif self.min_count == 1 and self.max_count is None:
            suffix = "+"
        elif self.min_count == self.max_count:
            suffix = f"{{{self.min_count}}}"
        elif self.max_count is None:
            suffix = f"{{{self.min_count},}}"
        else:
            suffix = f"{{{self.min_count},{self.max_count}}}"
        
        # Add lazy modifier if needed
        if self.lazy and suffix in ["?", "*", "+"]:
            suffix += "?"
        
        return child_regex + suffix
    
    def complexity(self) -> int:
        base_complexity = self.child.complexity()
        quantifier_complexity = 2  # Base cost for quantifier
        
        # Higher complexity for unbounded quantifiers
        if self.max_count is None:
            quantifier_complexity += 2
        
        return base_complexity + quantifier_complexity
    
    def clone(self) -> 'QuantifierNode':
        return QuantifierNode(
            child=self.child.clone(),
            min_count=self.min_count,
            max_count=self.max_count,
            lazy=self.lazy
        )


@dataclass
class GroupNode(PatternNode):
    """Represents grouped patterns like (abc) or (?:abc)."""
    child: PatternNode
    capturing: bool = True
    name: Optional[str] = None
    
    def to_regex(self) -> str:
        child_regex = self.child.to_regex()
        
        if not self.capturing:
            return f"(?:{child_regex})"
        elif self.name:
            return f"(?P<{self.name}>{child_regex})"
        else:
            return f"({child_regex})"
    
    def complexity(self) -> int:
        return self.child.complexity() + 2  # Base cost for grouping
    
    def clone(self) -> 'GroupNode':
        return GroupNode(
            child=self.child.clone(),
            capturing=self.capturing,
            name=self.name
        )


@dataclass
class AlternationNode(PatternNode):
    """Represents alternation patterns like abc|def|ghi."""
    alternatives: List[PatternNode]
    
    def to_regex(self) -> str:
        if not self.alternatives:
            return ""
        
        alt_strings = [alt.to_regex() for alt in self.alternatives]
        return "|".join(alt_strings)
    
    def complexity(self) -> int:
        if not self.alternatives:
            return 0
        
        base_complexity = sum(alt.complexity() for alt in self.alternatives)
        alternation_complexity = len(self.alternatives) - 1  # Cost for | operators
        
        return base_complexity + alternation_complexity
    
    def clone(self) -> 'AlternationNode':
        return AlternationNode(
            alternatives=[alt.clone() for alt in self.alternatives]
        )


@dataclass
class AnchorNode(PatternNode):
    """Represents anchors like ^, $, \\b, \\B."""
    anchor_type: str  # '^', '$', '\\b', '\\B'
    
    def to_regex(self) -> str:
        return self.anchor_type
    
    def complexity(self) -> int:
        return 1
    
    def clone(self) -> 'AnchorNode':
        return AnchorNode(self.anchor_type)


@dataclass
class WildcardNode(PatternNode):
    """Represents the . wildcard."""
    
    def to_regex(self) -> str:
        return "."
    
    def complexity(self) -> int:
        return 1
    
    def clone(self) -> 'WildcardNode':
        return WildcardNode()


class PatternAST:
    """Main class for representing and manipulating regex patterns as ASTs."""
    
    def __init__(self, root: PatternNode):
        self.root = root
    
    def to_regex(self) -> str:
        """Convert the entire AST to a regex string."""
        return self.root.to_regex()
    
    def complexity(self) -> int:
        """Calculate the total complexity of the pattern."""
        return self.root.complexity()
    
    def clone(self) -> 'PatternAST':
        """Create a deep copy of this AST."""
        return PatternAST(self.root.clone())
    
    def validate(self) -> bool:
        """Check if the pattern compiles to a valid regex."""
        try:
            re.compile(self.to_regex())
            return True
        except re.error:
            return False
    
    @classmethod
    def from_string(cls, pattern: str) -> 'PatternAST':
        """Create a PatternAST from a regex string (simplified parser)."""
        # This is a very basic implementation - a full parser would be more complex
        if not pattern:
            return cls(LiteralNode(""))
        
        # For now, just wrap the entire pattern as a literal
        # TODO: Implement proper regex parsing
        return cls(LiteralNode(pattern))
    
    def __str__(self) -> str:
        return self.to_regex()
    
    def __repr__(self) -> str:
        return f"PatternAST({self.root!r})"