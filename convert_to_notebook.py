#!/usr/bin/env python3
"""
Convert README.md to an interactive Jupyter notebook.

This script parses the README.md file and creates a Jupyter notebook where:
- Python code blocks become executable code cells
- Shell/bash code blocks become terminal cells (using %%bash magic)
- Markdown content becomes markdown cells
- Headers and structure are preserved
"""

import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any


def parse_markdown_file(file_path: str) -> List[Dict[str, Any]]:
    """Parse markdown file and extract code blocks and content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content by code blocks
    # This regex matches both ```python and ```bash blocks
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    
    cells = []
    last_end = 0
    
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        # Add markdown content before this code block
        markdown_content = content[last_end:match.start()].strip()
        if markdown_content:
            cells.append({
                'cell_type': 'markdown',
                'metadata': {},
                'source': markdown_content.split('\n')
            })
        
        # Extract code block info
        language = match.group(1) or 'text'
        code_content = match.group(2).strip()
        
        if language.lower() in ['python', 'py']:
            # Python code cell
            cells.append({
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': code_content.split('\n')
            })
        elif language.lower() in ['bash', 'shell', 'sh', 'zsh']:
            # Shell command cell using %%bash magic
            cells.append({
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {},
                'outputs': [],
                'source': ['%%bash\n'] + code_content.split('\n')
            })
        else:
            # Other language - keep as markdown with syntax highlighting
            cells.append({
                'cell_type': 'markdown',
                'metadata': {},
                'source': [f'```{language}\n{code_content}\n```']
            })
        
        last_end = match.end()
    
    # Add any remaining markdown content
    remaining_content = content[last_end:].strip()
    if remaining_content:
        cells.append({
            'cell_type': 'markdown',
            'metadata': {},
            'source': remaining_content.split('\n')
        })
    
    return cells


def create_notebook(cells: List[Dict[str, Any]], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Create a Jupyter notebook structure."""
    if metadata is None:
        metadata = {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'codemirror_mode': {
                    'name': 'ipython',
                    'version': 3
                },
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.12.0'
            }
        }
    
    return {
        'cells': cells,
        'metadata': metadata,
        'nbformat': 4,
        'nbformat_minor': 4
    }


def add_setup_cell(notebook: Dict[str, Any]) -> Dict[str, Any]:
    """Add a setup cell at the beginning with imports and configuration."""
    setup_cell = {
        'cell_type': 'code',
        'execution_count': None,
        'metadata': {},
        'outputs': [],
        'source': [
            '# Setup and Imports\n',
            'import sys\n',
            'import os\n',
            'from pathlib import Path\n',
            '\n',
            '# Enable shell magic for terminal commands\n',
            '%load_ext ipython_magic_bash\n',
            '\n',
            '# Set up display options\n',
            'from IPython.display import display, HTML\n',
            '\n',
            '# Configure notebook for better output\n',
            'import warnings\n',
            'warnings.filterwarnings(\'ignore\')\n',
            '\n',
            'print("✅ Notebook setup complete!")'
        ]
    }
    
    notebook['cells'].insert(0, setup_cell)
    return notebook


def add_toc_cell(notebook: Dict[str, Any]) -> Dict[str, Any]:
    """Add a table of contents cell after setup."""
    toc_cell = {
        'cell_type': 'markdown',
        'metadata': {},
        'source': [
            '# 📚 Mastering New Python Libraries\n',
            '\n',
            '## Interactive Notebook Version\n',
            '\n',
            'This notebook contains all the code examples from the README.md file. ',
            'You can run each cell interactively to explore Python libraries.\n',
            '\n',
            '### How to Use This Notebook:\n',
            '\n',
            '1. **Setup Cell**: Run the first cell to configure the environment\n',
            '2. **Code Cells**: Execute Python examples to see them in action\n',
            '3. **Terminal Cells**: Run shell commands with `%%bash` magic\n',
            '4. **Markdown Cells**: Read explanations and documentation\n',
            '\n',
            '---\n'
        ]
    }
    
    notebook['cells'].insert(1, toc_cell)
    return notebook


def process_shell_commands(cells: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Process and enhance shell command cells."""
    for cell in cells:
        if cell['cell_type'] == 'code' and cell['source'] and cell['source'][0].startswith('%%bash'):
            # Add comments and error handling to shell commands
            enhanced_source = ['%%bash\n']
            
            # Add a comment about what this command does
            if len(cell['source']) > 1:
                first_command = cell['source'][1].strip()
                if first_command.startswith('pip'):
                    enhanced_source.append('# Install Python package\n')
                elif first_command.startswith('git'):
                    enhanced_source.append('# Git command\n')
                elif first_command.startswith('python'):
                    enhanced_source.append('# Run Python script\n')
                else:
                    enhanced_source.append('# Shell command\n')
            
            # Add the actual commands
            enhanced_source.extend(cell['source'][1:])
            
            # Add error handling comment
            enhanced_source.append('\n# Note: If this command fails, you may need to install dependencies or adjust paths')
            
            cell['source'] = enhanced_source
    
    return cells


def main():
    parser = argparse.ArgumentParser(description='Convert README.md to Jupyter notebook')
    parser.add_argument('input', nargs='?', default='README.md', help='Input markdown file (default: README.md)')
    parser.add_argument('-o', '--output', default=None, help='Output notebook file')
    parser.add_argument('--no-setup', action='store_true', help='Skip adding setup cell')
    parser.add_argument('--no-toc', action='store_true', help='Skip adding table of contents')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output is None:
        input_path = Path(args.input)
        output_path = input_path.with_suffix('.ipynb')
    else:
        output_path = Path(args.output)
    
    print(f"Converting {args.input} to {output_path}")
    
    # Parse markdown and create notebook
    cells = parse_markdown_file(args.input)
    cells = process_shell_commands(cells)
    
    notebook = create_notebook(cells)
    
    # Add optional cells
    if not args.no_setup:
        notebook = add_setup_cell(notebook)
    
    if not args.no_toc:
        notebook = add_toc_cell(notebook)
    
    # Write notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Notebook created: {output_path}")
    print(f"📊 Statistics:")
    print(f"   - Total cells: {len(notebook['cells'])}")
    print(f"   - Code cells: {sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'code')}")
    print(f"   - Markdown cells: {sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'markdown')}")


if __name__ == '__main__':
    main() 