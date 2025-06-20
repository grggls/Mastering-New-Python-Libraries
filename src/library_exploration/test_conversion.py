#!/usr/bin/env python3
"""
Test script for the convert_to_notebook.py script.

This script runs the conversion on various test files to ensure
the conversion process works correctly with different edge cases.
"""

import subprocess
import json
import sys
from pathlib import Path


def test_conversion(test_file: str, verbose: bool = False) -> bool:
    """Test conversion of a single file."""
    print(f"\n{'='*60}")
    print(f"Testing: {test_file}")
    print(f"{'='*60}")
    
    try:
        # Run the conversion using the module path
        cmd = ['python', '-m', 'library_exploration.convert_to_notebook', test_file]
        if verbose:
            cmd.append('-v')
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Check if conversion was successful
        if result.returncode == 0:
            # Verify the generated notebook
            notebook_file = Path(test_file).with_suffix('.ipynb')
            if notebook_file.exists():
                try:
                    with open(notebook_file, 'r') as f:
                        notebook = json.load(f)
                    
                    cell_count = len(notebook['cells'])
                    code_cells = sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'code')
                    markdown_cells = sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'markdown')
                    
                    print(f"✅ SUCCESS: {notebook_file}")
                    print(f"   - Total cells: {cell_count}")
                    print(f"   - Code cells: {code_cells}")
                    print(f"   - Markdown cells: {markdown_cells}")
                    return True
                    
                except json.JSONDecodeError as e:
                    print(f"❌ FAILED: Invalid JSON in {notebook_file}: {e}")
                    return False
            else:
                print(f"❌ FAILED: Notebook file {notebook_file} was not created")
                return False
        else:
            print(f"❌ FAILED: Conversion returned exit code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def main():
    """Run all test files."""
    test_files = [
        'test_problematic.md',
        'test_severe_issue.md', 
        'test_edge_cases.md'
    ]
    
    verbose = '--verbose' in sys.argv or '-v' in sys.argv
    
    print("🧪 Testing convert_to_notebook.py")
    print(f"Verbose mode: {'ON' if verbose else 'OFF'}")
    
    results = []
    for test_file in test_files:
        if Path(test_file).exists():
            success = test_conversion(test_file, verbose)
            results.append((test_file, success))
        else:
            print(f"⚠️  WARNING: Test file {test_file} not found")
            results.append((test_file, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    for test_file, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_file}")
        if success:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed!")
        return 0
    else:
        print("💥 Some tests failed!")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 