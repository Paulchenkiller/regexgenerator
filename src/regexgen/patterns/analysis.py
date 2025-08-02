"""Pattern analysis and domain recognition for smarter initial pattern generation."""

import re
import string
from typing import List, Set, Dict, Optional, Tuple
from collections import Counter, defaultdict
from dataclasses import dataclass

from regexgen.patterns.ast import (
    PatternAST, PatternNode, LiteralNode, CharacterClassNode, 
    QuantifierNode, GroupNode, AlternationNode, WildcardNode
)


@dataclass
class PatternAnalysis:
    """Analysis results for a set of example strings."""
    common_length: Optional[int]
    length_range: Tuple[int, int]
    character_sets: Dict[int, Set[str]]  # position -> characters
    common_prefixes: List[str]
    common_suffixes: List[str]
    pattern_type: str  # 'digits', 'letters', 'mixed', 'email', 'url', etc.
    detected_structure: List[str]  # sequence of character types at each position
    repetitive_segments: List[Tuple[str, int, int]]  # pattern, start, end


class PatternAnalyzer:
    """Analyzes example strings to understand their structure and suggest initial patterns."""
    
    def __init__(self):
        self.domain_patterns = {
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'url': re.compile(r'^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?(?:/.*)?$'),
            'phone': re.compile(r'^\+?[\d\s\-\(\)]{7,}$'),  # At least 7 chars for phone
            'date_iso': re.compile(r'^\d{4}-\d{2}-\d{2}$'),
            'date_us': re.compile(r'^\d{1,2}/\d{1,2}/\d{4}$'),
            'time': re.compile(r'^\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?$'),
            'ipv4': re.compile(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'),
            'hex_color': re.compile(r'^#[0-9a-fA-F]{6}$'),
            'uuid': re.compile(r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'),
        }
    
    def analyze_examples(self, examples: List[str]) -> PatternAnalysis:
        """Analyze a list of example strings to understand their structure."""
        if not examples:
            return PatternAnalysis(
                common_length=None,
                length_range=(0, 0),
                character_sets={},
                common_prefixes=[],
                common_suffixes=[],
                pattern_type='unknown',
                detected_structure=[],
                repetitive_segments=[]
            )
        
        # Basic length analysis
        lengths = [len(ex) for ex in examples]
        length_range = (min(lengths), max(lengths))
        common_length = lengths[0] if all(l == lengths[0] for l in lengths) else None
        
        # Character analysis by position
        character_sets = defaultdict(set)
        max_len = max(lengths)
        
        for example in examples:
            for i, char in enumerate(example):
                character_sets[i].add(char)
        
        # Detect common prefixes and suffixes
        common_prefixes = self._find_common_prefixes(examples)
        common_suffixes = self._find_common_suffixes(examples)
        
        # Detect pattern type
        pattern_type = self._detect_pattern_type(examples)
        
        # Analyze structure (sequence of character types)
        detected_structure = self._analyze_structure(examples)
        
        # Find repetitive segments
        repetitive_segments = self._find_repetitive_segments(examples)
        
        return PatternAnalysis(
            common_length=common_length,
            length_range=length_range,
            character_sets=dict(character_sets),
            common_prefixes=common_prefixes,
            common_suffixes=common_suffixes,
            pattern_type=pattern_type,
            detected_structure=detected_structure,
            repetitive_segments=repetitive_segments
        )
    
    def _detect_pattern_type(self, examples: List[str]) -> str:
        """Detect the type of pattern from examples."""
        # Test against known domain patterns
        for pattern_type, regex in self.domain_patterns.items():
            if all(regex.match(ex) for ex in examples):
                return pattern_type
        
        # Analyze character composition
        all_chars = ''.join(examples)
        
        if all(c.isdigit() for c in all_chars):
            return 'digits'
        elif all(c.isalpha() for c in all_chars):
            return 'letters'
        elif all(c.isalnum() for c in all_chars):
            return 'alphanumeric'
        elif all(c in string.ascii_letters + string.digits + '-_.' for c in all_chars):
            return 'identifier'
        else:
            return 'mixed'
    
    def _analyze_structure(self, examples: List[str]) -> List[str]:
        """Analyze the character type structure across examples."""
        if not examples:
            return []
        
        # Find the most common length or use the maximum
        lengths = [len(ex) for ex in examples]
        target_length = max(set(lengths), key=lengths.count)
        
        structure = []
        
        for pos in range(target_length):
            char_types = []
            for example in examples:
                if pos < len(example):
                    char = example[pos]
                    if char.isdigit():
                        char_types.append('digit')
                    elif char.islower():
                        char_types.append('lower')
                    elif char.isupper():
                        char_types.append('upper')
                    elif char.isalpha():
                        char_types.append('alpha')
                    elif char in string.punctuation:
                        char_types.append('punct')
                    elif char.isspace():
                        char_types.append('space')
                    else:
                        char_types.append('other')
            
            # Find most common type at this position
            if char_types:
                most_common = Counter(char_types).most_common(1)[0][0]
                structure.append(most_common)
        
        return structure
    
    def _find_common_prefixes(self, examples: List[str]) -> List[str]:
        """Find common prefixes in examples."""
        if not examples:
            return []
        
        prefixes = []
        min_len = min(len(ex) for ex in examples)
        
        for i in range(1, min_len + 1):
            prefix = examples[0][:i]
            if all(ex.startswith(prefix) for ex in examples):
                prefixes.append(prefix)
            else:
                break
        
        return prefixes
    
    def _find_common_suffixes(self, examples: List[str]) -> List[str]:
        """Find common suffixes in examples."""
        if not examples:
            return []
        
        suffixes = []
        min_len = min(len(ex) for ex in examples)
        
        for i in range(1, min_len + 1):
            suffix = examples[0][-i:]
            if all(ex.endswith(suffix) for ex in examples):
                suffixes.append(suffix)
            else:
                break
        
        return suffixes
    
    def _find_repetitive_segments(self, examples: List[str]) -> List[Tuple[str, int, int]]:
        """Find repetitive segments in examples."""
        segments = []
        
        if not examples:
            return segments
        
        # Look for repeated character patterns
        for example in examples[:3]:  # Check first few examples
            for start in range(len(example)):
                for length in range(2, min(6, len(example) - start + 1)):
                    segment = example[start:start + length]
                    
                    # Check if this segment appears multiple times
                    count = 0
                    pos = start
                    while pos + length <= len(example):
                        if example[pos:pos + length] == segment:
                            count += 1
                            pos += length
                        else:
                            break
                    
                    if count > 1:
                        segments.append((segment, start, start + length * count))
        
        return segments
    
    def generate_initial_pattern(self, analysis: PatternAnalysis) -> PatternAST:
        """Generate an initial pattern based on analysis."""
        if analysis.pattern_type in self.domain_patterns:
            return self._generate_domain_pattern(analysis.pattern_type)
        
        return self._generate_structure_based_pattern(analysis)
    
    def _generate_domain_pattern(self, pattern_type: str) -> PatternAST:
        """Generate domain-specific patterns."""
        domain_templates = {
            'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            'url': r'https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})?(?:/.*)?',
            'phone': r'\+?[\d\s\-\(\)]+',
            'date_iso': r'\d{4}-\d{2}-\d{2}',
            'date_us': r'\d{1,2}/\d{1,2}/\d{4}',
            'time': r'\d{1,2}:\d{2}(?::\d{2})?(?:\s?[AaPp][Mm])?',
            'ipv4': r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
            'hex_color': r'#[0-9a-fA-F]{6}',
            'uuid': r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            'digits': r'\d+',
            'letters': r'[a-zA-Z]+',
            'alphanumeric': r'[a-zA-Z0-9]+',
        }
        
        template = domain_templates.get(pattern_type, r'.*')
        return PatternAST.from_string(template)
    
    def _generate_structure_based_pattern(self, analysis: PatternAnalysis) -> PatternAST:
        """Generate pattern based on structural analysis."""
        if not analysis.detected_structure:
            return PatternAST(LiteralNode(""))
        
        # For simple cases, create targeted patterns
        structure = analysis.detected_structure
        
        # If all same type, create simple character class with quantifier
        if len(set(structure)) == 1:
            char_type = structure[0]
            
            if char_type == 'digit':
                char_class = CharacterClassNode(characters=set('0123456789'))
            elif char_type == 'lower':
                char_class = CharacterClassNode(characters=set(string.ascii_lowercase))
            elif char_type == 'upper':
                char_class = CharacterClassNode(characters=set(string.ascii_uppercase))
            elif char_type == 'alpha':
                char_class = CharacterClassNode(characters=set(string.ascii_letters))
            else:
                char_class = WildcardNode()
            
            # Add quantifier if there's a clear pattern
            if analysis.common_length:
                if analysis.common_length == 1:
                    return PatternAST(char_class)
                else:
                    quantifier = QuantifierNode(char_class, analysis.common_length, analysis.common_length)
                    return PatternAST(quantifier)
            else:
                quantifier = QuantifierNode(char_class, analysis.length_range[0], analysis.length_range[1])
                return PatternAST(quantifier)
        
        # For mixed patterns, start with the most common character type
        from collections import Counter
        type_counts = Counter(structure)
        most_common_type = type_counts.most_common(1)[0][0]
        
        if most_common_type == 'digit':
            base_class = CharacterClassNode(characters=set('0123456789'))
        elif most_common_type == 'lower':
            base_class = CharacterClassNode(characters=set(string.ascii_lowercase))
        elif most_common_type == 'upper':
            base_class = CharacterClassNode(characters=set(string.ascii_uppercase))
        elif most_common_type == 'alpha':
            base_class = CharacterClassNode(characters=set(string.ascii_letters))
        else:
            base_class = WildcardNode()
        
        # Add appropriate quantifier
        if analysis.common_length:
            if analysis.common_length == 1:
                return PatternAST(base_class)
            else:
                quantifier = QuantifierNode(base_class, 1, analysis.common_length)
                return PatternAST(quantifier)
        else:
            quantifier = QuantifierNode(base_class, 1, None)  # One or more
            return PatternAST(quantifier)
    
    def suggest_improvements(self, current_pattern: PatternAST, analysis: PatternAnalysis) -> List[PatternAST]:
        """Suggest improvements to a current pattern based on analysis."""
        suggestions = []
        
        # If pattern doesn't match the detected type, suggest domain-specific pattern
        if analysis.pattern_type in self.domain_patterns:
            domain_pattern = self._generate_domain_pattern(analysis.pattern_type)
            suggestions.append(domain_pattern)
        
        # Suggest quantified versions if there's length variation
        if analysis.length_range[0] != analysis.length_range[1]:
            min_len, max_len = analysis.length_range
            if min_len > 0:
                quantified = PatternAST(QuantifierNode(
                    child=current_pattern.root.clone(),
                    min_count=min_len,
                    max_count=max_len
                ))
                suggestions.append(quantified)
        
        return suggestions[:3]  # Return top 3 suggestions