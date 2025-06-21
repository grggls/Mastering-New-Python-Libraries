#!/usr/bin/env python3
"""
Debug script to extract and display a specific problematic code block with syntax errors.
"""

import re
import ast
from pathlib import Path

def extract_code_blocks(markdown_file: str):
    """Extract all code blocks from markdown file."""
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match code blocks with language specification
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    blocks = []
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        start_line = content[:match.start()].count('\n') + 1
        
        blocks.append({
            'language': language.lower(),
            'code': code,
            'start_line': start_line,
            'full_match': match.group(0)
        })
    
    return blocks

def validate_python_syntax(code: str):
    try:
        ast.parse(code)
        return True, ""
    except SyntaxError as e:
        return False, f"Syntax error: {e.msg} at line {e.lineno}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"

def main():
    blocks = extract_code_blocks('README.md')
    python_blocks = [b for b in blocks if b['language'] in ['python', 'py']]
    
    idx = 19  # block 20 (0-based index)
    if idx < len(python_blocks):
        block = python_blocks[idx]
        is_valid, error = validate_python_syntax(block['code'])
        print(f"\n--- Block {idx+1} (line {block['start_line']}) ---")
        print(f"Language: {block['language']}")
        print(f"Error: {error}")
        print("Code:")
        print(block['code'])
        print("-" * 40)
    else:
        print(f"Block {idx+1} not found.")

if __name__ == '__main__':
    main() 