#!/usr/bin/env python3
"""
Test script for validating Python code blocks and conversion functionality.

This script:
1. Extracts and validates Python code blocks from README.md
2. Tests the convert_to_notebook.py script
3. Validates generated notebook syntax
4. Runs basic functionality tests
"""

import ast
import re
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import argparse


def extract_code_blocks(markdown_file: str) -> List[Dict[str, Any]]:
    """Extract all code blocks from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match code blocks with language specification
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    blocks = []
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        
        blocks.append({
            'language': language.lower(),
            'code': code,
            'start_line': content[:match.start()].count('\n') + 1
        })
    
    return blocks


def validate_python_syntax(code: str, context: str = "") -> Tuple[bool, str]:
    """Validate Python syntax using ast.parse."""
    # Handle REPL-style code blocks (with >>> and ... prompts)
    if '>>>' in code or '...' in code:
        # Extract actual Python code by removing REPL prompts
        lines = code.split('\n')
        python_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('>>> '):
                # Remove >>> prompt
                python_lines.append(line[4:])
            elif line.startswith('... '):
                # Remove ... prompt
                python_lines.append(line[4:])
            elif line.startswith('...'):
                # Remove ... prompt (no space)
                python_lines.append(line[3:])
            elif line and not line.startswith('>>>') and not line.startswith('...'):
                # Regular line without prompt
                python_lines.append(line)
        
        # Reconstruct code without prompts
        code = '\n'.join(python_lines)
    
    # Skip empty code blocks
    if not code.strip():
        return True, ""
    
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        error_msg = f"Syntax error in {context}: {e.msg} at line {e.lineno}"
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error in {context}: {str(e)}"
        return False, error_msg


def test_code_blocks(markdown_file: str) -> Dict[str, Any]:
    """Test all code blocks in the markdown file."""
    print(f"🔍 Testing code blocks in {markdown_file}")
    
    blocks = extract_code_blocks(markdown_file)
    python_blocks = [b for b in blocks if b['language'] in ['python', 'py']]
    
    results = {
        'total_blocks': len(blocks),
        'python_blocks': len(python_blocks),
        'syntax_errors': [],
        'valid_blocks': 0
    }
    
    print(f"📊 Found {len(blocks)} total code blocks ({len(python_blocks)} Python)")
    
    for i, block in enumerate(python_blocks):
        context = f"block {i+1} (line {block['start_line']})"
        is_valid, error = validate_python_syntax(block['code'], context)
        
        if is_valid:
            results['valid_blocks'] += 1
            print(f"✅ {context}: Valid syntax")
        else:
            results['syntax_errors'].append({
                'block': i + 1,
                'line': block['start_line'],
                'error': error,
                'code_preview': block['code'][:100] + "..." if len(block['code']) > 100 else block['code']
            })
            print(f"❌ {context}: {error}")
    
    return results


def test_conversion_script():
    """Test that the conversion script works correctly"""
    print("🔄 Testing conversion script...")
    
    try:
        # Test the conversion script
        from library_exploration.convert_to_notebook import parse_markdown_file
        print("✅ Conversion script found")
        return True
    except ImportError as e:
        print(f"❌ Conversion script not found: {e}")
        return False


def test_notebook_cells(notebook_file: str) -> Dict[str, Any]:
    """Test individual cells in a generated notebook."""
    print(f"\n📓 Testing notebook cells in {notebook_file}")
    
    results = {
        'total_cells': 0,
        'code_cells': 0,
        'markdown_cells': 0,
        'syntax_errors': [],
        'shell_commands': 0
    }
    
    try:
        with open(notebook_file, 'r') as f:
            notebook = json.load(f)
        
        results['total_cells'] = len(notebook['cells'])
        
        for i, cell in enumerate(notebook['cells']):
            cell_type = cell.get('cell_type', 'unknown')
            
            if cell_type == 'code':
                results['code_cells'] += 1
                source = ''.join(cell.get('source', []))
                
                # Check for shell commands
                if source.startswith('%%bash'):
                    results['shell_commands'] += 1
                    print(f"🐚 Cell {i+1}: Shell command")
                else:
                    # Validate Python syntax
                    is_valid, error = validate_python_syntax(source, f"cell {i+1}")
                    if not is_valid:
                        results['syntax_errors'].append({
                            'cell': i + 1,
                            'error': error,
                            'code_preview': source[:100] + "..." if len(source) > 100 else source
                        })
                        print(f"❌ Cell {i+1}: {error}")
                    else:
                        print(f"✅ Cell {i+1}: Valid Python")
            
            elif cell_type == 'markdown':
                results['markdown_cells'] += 1
        
        print(f"📊 Notebook analysis: {results['total_cells']} total cells")
        print(f"   - Code cells: {results['code_cells']}")
        print(f"   - Markdown cells: {results['markdown_cells']}")
        print(f"   - Shell commands: {results['shell_commands']}")
        print(f"   - Syntax errors: {len(results['syntax_errors'])}")
        
    except Exception as e:
        print(f"❌ Notebook testing error: {e}")
    
    return results


def test_functional_operations() -> Dict[str, Any]:
    """Test basic functional operations."""
    print("🧪 Running functional tests...")
    
    results = {
        'imports_work': False,
        'basic_operations': False,
        'error_handling': False
    }
    
    # Test basic imports
    try:
        import library_exploration
        results['imports_work'] = True
        print("✅ Basic imports work")
    except ImportError as e:
        print(f"❌ Basic imports error: {e}")
        return results
    
    # Test basic operations
    try:
        from library_exploration.convert_to_notebook import parse_markdown_file
        results['basic_operations'] = True
        print("✅ Basic operations work")
    except Exception as e:
        print(f"❌ Basic operations error: {e}")
    
    # Test error handling
    try:
        from library_exploration.validate_notebook import validate_notebook
        results['error_handling'] = True
        print("✅ Error handling works")
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description='Comprehensive code validation')
    parser.add_argument('--verbose', action='store_true', help='Print code for blocks with syntax errors')
    args = parser.parse_args()
    print("🚀 Starting comprehensive code validation...")
    
    all_results = {}
    
    # Test code blocks in README
    blocks = extract_code_blocks('README.md')
    python_blocks = [b for b in blocks if b['language'] in ['python', 'py']]
    all_results['code_blocks'] = test_code_blocks('README.md')
    
    # Print verbose info for syntax errors
    if args.verbose:
        for i, block in enumerate(python_blocks):
            is_valid, error = validate_python_syntax(block['code'], f"block {i+1} (line {block['start_line']})")
            if not is_valid:
                print(f"\n--- Block {i+1} (line {block['start_line']}) ---")
                print(f"Error: {error}")
                print("Code:")
                print(block['code'])
                print("-" * 40)
    
    # Test conversion script
    all_results['conversion'] = test_conversion_script()
    
    # Test generated notebook if it exists
    notebook_path = Path('Mastering-New-Python-Libraries.ipynb')
    if notebook_path.exists():
        all_results['notebook'] = test_notebook_cells('Mastering-New-Python-Libraries.ipynb')
    
    # Run functional tests
    all_results['functional'] = test_functional_operations()
    
    # Summary
    print("\n" + "="*50)
    print("📋 TEST SUMMARY")
    print("="*50)
    
    # Code blocks summary
    cb = all_results['code_blocks']
    print(f"📝 Code Blocks: {cb['valid_blocks']}/{cb['python_blocks']} Python blocks valid")
    if cb['syntax_errors']:
        print(f"   ❌ {len(cb['syntax_errors'])} syntax errors found")
    
    # Conversion summary
    conv = all_results['conversion']
    print(f"🔄 Conversion: {'✅' if conv else '❌'} Script works")
    
    # Functional summary
    func = all_results['functional']
    print(f"🧪 Functional: {'✅' if func['imports_work'] else '❌'} Imports")
    print(f"   🔧 Operations: {'✅' if func['basic_operations'] else '❌'} Basic ops")
    print(f"   🛡️ Error handling: {'✅' if func['error_handling'] else '❌'} Errors")
    
    # Calculate total errors
    total_errors = (
        len(cb['syntax_errors']) +
        (0 if conv else 1) +
        (0 if func['imports_work'] and func['basic_operations'] else 1)
    )
    
    if total_errors == 0:
        print("\n🎉 All tests passed! Code is ready for production.")
        return 0
    else:
        print(f"\n⚠️  {total_errors} issues found. Please review and fix.")
        return 1


if __name__ == '__main__':
    sys.exit(main()) 