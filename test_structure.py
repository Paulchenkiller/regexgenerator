#!/usr/bin/env python3
"""Simple test to verify the project structure works."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that basic imports work."""
    try:
        # Test basic package import
        import regexgen
        print(f"✓ Package import works: regexgen v{regexgen.__version__}")
        
        # Test AST module
        from regexgen.patterns.ast import PatternAST, LiteralNode
        print("✓ PatternAST import works")
        
        # Test basic AST functionality
        literal = LiteralNode("test")
        ast = PatternAST(literal)
        regex_str = ast.to_regex()
        print(f"✓ AST functionality works: '{regex_str}'")
        
        # Test complexity calculation
        complexity = ast.complexity()
        print(f"✓ Complexity calculation works: {complexity}")
        
        return True
        
    except Exception as e:
        print(f"✗ Import test failed: {e}")
        return False

def test_ast_nodes():
    """Test various AST node types."""
    try:
        from regexgen.patterns.ast import (
            LiteralNode, CharacterClassNode, QuantifierNode, 
            GroupNode, AlternationNode, WildcardNode
        )
        
        # Test literal
        lit = LiteralNode("hello")
        assert lit.to_regex() == "hello"
        print("✓ LiteralNode works")
        
        # Test character class
        char_class = CharacterClassNode(characters={'a', 'b', 'c'})
        result = char_class.to_regex()
        assert '[' in result and ']' in result
        print(f"✓ CharacterClassNode works: {result}")
        
        # Test quantifier
        quant = QuantifierNode(child=lit, min_count=1, max_count=3)
        result = quant.to_regex()
        assert '{1,3}' in result
        print(f"✓ QuantifierNode works: {result}")
        
        # Test wildcard
        wild = WildcardNode()
        assert wild.to_regex() == "."
        print("✓ WildcardNode works")
        
        return True
        
    except Exception as e:
        print(f"✗ AST node test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing RegexGenerator project structure...")
    print()
    
    success = True
    success &= test_imports()
    success &= test_ast_nodes()
    
    print()
    if success:
        print("🎉 All tests passed! Project structure is working correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
        sys.exit(1)