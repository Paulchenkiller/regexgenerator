#!/usr/bin/env python3
"""Test script to verify RegexGenerator installation works correctly."""

import sys
import subprocess
import os
from pathlib import Path

def test_virtual_env_installation():
    """Test virtual environment installation process."""
    print("🧪 Testing virtual environment installation...")
    
    # Check if we're in the right directory
    if not Path("pyproject.toml").exists():
        print("❌ Run this script from the regexgenerator root directory")
        return False
    
    # Test virtual environment creation and activation
    try:
        print("1. Testing virtual environment creation...")
        result = subprocess.run([sys.executable, "-m", "venv", "test_venv"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Virtual environment creation failed: {result.stderr}")
            return False
        print("✓ Virtual environment created successfully")
        
        # Determine activation script path
        if os.name == 'nt':  # Windows
            pip_path = Path("test_venv/Scripts/pip")
            python_path = Path("test_venv/Scripts/python")
        else:  # Unix/Linux/macOS
            pip_path = Path("test_venv/bin/pip")
            python_path = Path("test_venv/bin/python")
        
        # Test dependency installation
        print("2. Testing dependency installation...")
        result = subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Dependency installation failed: {result.stderr}")
            return False
        print("✓ Dependencies installed successfully")
        
        # Test package installation
        print("3. Testing package installation...")
        result = subprocess.run([str(pip_path), "install", "-e", "."], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Package installation failed: {result.stderr}")
            return False
        print("✓ Package installed successfully")
        
        # Test CLI functionality
        print("4. Testing CLI functionality...")
        if os.name == 'nt':
            regexgen_path = Path("test_venv/Scripts/regexgen")
        else:
            regexgen_path = Path("test_venv/bin/regexgen")
        
        result = subprocess.run([str(regexgen_path), "--help"], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print(f"❌ CLI test failed: {result.stderr}")
            return False
        
        if "RegexGenerator" not in result.stdout:
            print(f"❌ CLI output doesn't contain expected text: {result.stdout}")
            return False
        print("✓ CLI working correctly")
        
        return True
        
    except Exception as e:
        print(f"❌ Installation test failed with exception: {e}")
        return False
    
    finally:
        # Cleanup
        if Path("test_venv").exists():
            import shutil
            shutil.rmtree("test_venv")
            print("🧹 Cleaned up test environment")

def test_direct_execution():
    """Test direct execution without installation."""
    print("\n🧪 Testing direct execution...")
    
    try:
        # Test module execution
        result = subprocess.run([sys.executable, "-m", "regexgen", "--help"], 
                              cwd="src", capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Direct execution failed: {result.stderr}")
            return False
        
        if "RegexGenerator" not in result.stdout:
            print(f"❌ Direct execution output doesn't contain expected text")
            return False
            
        print("✓ Direct execution working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Direct execution test failed: {e}")
        return False

def test_basic_functionality():
    """Test basic pattern generation functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test basic pattern generation
        result = subprocess.run([
            sys.executable, "-m", "regexgen", 
            "--max-iterations", "10",  # Quick test
            "--seed", "42",  # Reproducible
            "test", "best", "rest"
        ], cwd="src", capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            print(f"❌ Basic functionality test failed: {result.stderr}")
            return False
        
        # Check that some pattern was generated
        if not result.stdout.strip() or "Error" in result.stdout:
            print(f"❌ No valid pattern generated: {result.stdout}")
            return False
            
        print("✓ Basic functionality working")
        print(f"  Generated pattern: {result.stdout.strip().split()[-1]}")
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 RegexGenerator Installation Test Suite")
    print("=" * 50)
    
    success = True
    
    # Test 1: Virtual environment installation
    success &= test_virtual_env_installation()
    
    # Test 2: Direct execution
    success &= test_direct_execution()
    
    # Test 3: Basic functionality
    success &= test_basic_functionality()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 All installation tests passed!")
        print("RegexGenerator is ready for use!")
    else:
        print("❌ Some installation tests failed.")
        print("Check the error messages above for details.")
        sys.exit(1)