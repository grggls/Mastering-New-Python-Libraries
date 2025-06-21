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
import sys
from pathlib import Path
from typing import List, Dict, Any


def parse_markdown_file(file_path: str, verbose: bool = False) -> List[Dict[str, Any]]:
    """Parse markdown file and extract code blocks and content, adding source anchors and metadata for traceability."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ Error: File '{file_path}' not found")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reading file '{file_path}': {e}")
        sys.exit(1)
    
    code_block_pattern = r'```(\w+)?\n(.*?)```'
    cells = []
    last_end = 0
    block_count = 0
    processed_count = 0
    for match in re.finditer(code_block_pattern, content, re.DOTALL):
        block_count += 1
        start_line = content[:match.start()].count('\n') + 1
        # Extract language and content
        language = match.group(1) or ''
        code_content = match.group(2).strip()
        
        if verbose:
            print(f"🔍 Processing code block at line {start_line}:")
            print(f"   Language: '{language}'")
            print(f"   Content preview: {code_content[:100]}...")
            print(f"   Contains $: {'$' in code_content}")
            print(f"   Is shell: {language.lower() in ['bash', 'shell', 'sh', 'zsh'] or '$' in code_content}")
        anchor = f"{file_path}:{start_line}"
        # Add markdown content before this code block
        markdown_content = content[last_end:match.start()].strip()
        if markdown_content:
            md_start_line = content[:last_end].count('\n') + 1
            md_anchor = f"{file_path}:{md_start_line}"
            # Add anchor as HTML comment at the top of the markdown cell
            md_cell = {
                'cell_type': 'markdown',
                'metadata': {
                    'source_file': file_path,
                    'source_line': md_start_line,
                    'source_anchor': md_anchor
                },
                'source': [f'<!-- source:{md_anchor} -->\n'] + [line + '\n' for line in markdown_content.split('\n')]
            }
            cells.append(md_cell)
        # Code or other block
        if language.lower() in ['python', 'py']:
            # If the code block contains REPL prompts (>>>), treat as markdown for readability
            if '>>>' in code_content:
                # Add anchor as HTML comment at the top of the markdown cell
                md_cell = {
                    'cell_type': 'markdown',
                    'metadata': {
                        'source_file': file_path,
                        'source_line': start_line,
                        'source_anchor': anchor
                    },
                    'source': [f'<!-- source:{anchor} -->\n', f'```python\n{code_content}\n```']
                }
                cells.append(md_cell)
            else:
                # Add necessary imports for common modules
                import_lines = []
                if 'os.' in code_content and 'import os' not in code_content:
                    import_lines.append('import os\n')
                if 'sys.' in code_content and 'import sys' not in code_content:
                    import_lines.append('import sys\n')
                if 'requests.' in code_content and 'import requests' not in code_content:
                    import_lines.append('import requests\n')
                if 'inspect.' in code_content and 'import inspect' not in code_content:
                    import_lines.append('import inspect\n')
                
                # Add variable definitions for commonly used but undefined variables
                if 'obj.' in code_content and 'obj =' not in code_content and 'obj=' not in code_content:
                    import_lines.append('obj = requests  # Example object for inspection\n')
                
                # Add try-except wrapper for pkg_resources if it's used
                if 'pkg_resources' in code_content:
                    import_lines.append('try:\n')
                    import_lines.append('    import pkg_resources\n')
                    import_lines.append('except ImportError:\n')
                    import_lines.append('    print("pkg_resources not available - skipping package introspection")\n')
                    import_lines.append('    pkg_resources = None\n')
                
                # Add anchor as a comment at the top of the code cell
                code_cell = {
                    'cell_type': 'code',
                    'execution_count': None,
                    'metadata': {
                        'source_file': file_path,
                        'source_line': start_line,
                        'source_anchor': anchor
                    },
                    'outputs': [],
                    'source': [f'# [source:{anchor}]\n'] + import_lines + [line + '\n' for line in code_content.split('\n')]
                }
                
                # If pkg_resources is used, wrap the code in conditional checks
                if 'pkg_resources' in code_content:
                    # Find lines that use pkg_resources and wrap them
                    modified_lines = []
                    in_pkg_block = False
                    for line in code_content.split('\n'):
                        if 'pkg_resources.' in line:
                            # Indent the line and add a conditional check
                            modified_lines.append(f'if pkg_resources is not None:\n')
                            modified_lines.append(f'    {line}\n')
                            in_pkg_block = True
                        elif line.strip().startswith('import pkg_resources'):
                            # Skip the original import since we already added the try-except wrapper
                            continue
                        elif in_pkg_block and ('print(' in line or 'dist.' in line or 'entry_points' in line):
                            # Wrap print statements that use variables from pkg_resources
                            modified_lines.append(f'if pkg_resources is not None:\n')
                            modified_lines.append(f'    {line}\n')
                            in_pkg_block = False
                        else:
                            modified_lines.append(line + '\n')
                            in_pkg_block = False
                    
                    # Update the cell source with modified lines
                    code_cell['source'] = [f'# [source:{anchor}]\n'] + import_lines + modified_lines
                else:
                    code_cell['source'] = [f'# [source:{anchor}]\n'] + import_lines + [line + '\n' for line in code_content.split('\n')]
                
                cells.append(code_cell)
        elif language.lower() in ['bash', 'shell', 'sh', 'zsh'] or '$' in code_content:
            # Add anchor as a comment at the top of the shell code cell
            code_cell = {
                'cell_type': 'code',
                'execution_count': None,
                'metadata': {
                    'source_file': file_path,
                    'source_line': start_line,
                    'source_anchor': anchor
                },
                'outputs': [],
                'source': [f'# [source:{anchor}]\n', '%%bash\n'] + [line + '\n' for line in code_content.split('\n')]
            }
            cells.append(code_cell)
            processed_count += 1
        else:
            # Add anchor as HTML comment at the top of the markdown cell
            md_cell = {
                'cell_type': 'markdown',
                'metadata': {
                    'source_file': file_path,
                    'source_line': start_line,
                    'source_anchor': anchor
                },
                'source': [f'<!-- source:{anchor} -->\n', f'```{language}\n{code_content}\n```']
            }
            cells.append(md_cell)
        last_end = match.end()
    # Add any remaining markdown content
    remaining_content = content[last_end:].strip()
    if remaining_content:
        md_start_line = content[:last_end].count('\n') + 1
        md_anchor = f"{file_path}:{md_start_line}"
        md_cell = {
            'cell_type': 'markdown',
            'metadata': {
                'source_file': file_path,
                'source_line': md_start_line,
                'source_anchor': md_anchor
            },
            'source': [f'<!-- source:{md_anchor} -->\n'] + [line + '\n' for line in remaining_content.split('\n')]
        }
        cells.append(md_cell)
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
            '# Note: %%bash magic is built into IPython/Jupyter\n',
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


def process_shell_commands(cells: List[Dict[str, Any]], verbose: bool = False) -> List[Dict[str, Any]]:
    """Process and enhance shell command cells."""
    processed_count = 0
    
    for i, cell in enumerate(cells):
        try:
            if cell['cell_type'] == 'code' and cell['source'] and cell['source'][0].startswith('%%bash'):
                processed_count += 1
                
                if verbose:
                    print(f"🔧 Processing shell command cell #{i+1}")
                
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
                
        except Exception as e:
            print(f"❌ Error processing shell command cell #{i+1}: {e}")
            if verbose:
                print(f"   Cell content:")
                print(f"   {'='*30}")
                try:
                    for j, line in enumerate(cell.get('source', []), 1):
                        print(f"   {j:2d}: {line}")
                except Exception as print_error:
                    print(f"   Could not print cell content: {print_error}")
                print(f"   {'='*30}")
            continue
    
    if verbose:
        print(f"✅ Processed {processed_count} shell command cells")
    
    return cells


def main():
    parser = argparse.ArgumentParser(description='Convert README.md to Jupyter notebook')
    parser.add_argument('input', nargs='?', default='README.md', help='Input markdown file (default: README.md)')
    parser.add_argument('-o', '--output', default=None, help='Output notebook file')
    parser.add_argument('--no-setup', action='store_true', help='Skip adding setup cell')
    parser.add_argument('--no-toc', action='store_true', help='Skip adding table of contents')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output with code block details')
    
    args = parser.parse_args()
    
    # Determine output filename
    if args.output is None:
        input_path = Path(args.input)
        output_path = input_path.with_suffix('.ipynb')
    else:
        output_path = Path(args.output)
    
    print(f"Converting {args.input} to {output_path}")
    if args.verbose:
        print("🔍 Verbose mode enabled - will show detailed processing information")
    
    try:
        # Parse markdown and create notebook
        cells = parse_markdown_file(args.input, verbose=args.verbose)
        cells = process_shell_commands(cells, verbose=args.verbose)
        
        notebook = create_notebook(cells)
        
        # Add optional cells
        if not args.no_setup:
            notebook = add_setup_cell(notebook)
            if args.verbose:
                print("✅ Added setup cell")
        
        if not args.no_toc:
            notebook = add_toc_cell(notebook)
            if args.verbose:
                print("✅ Added table of contents cell")
        
        # Write notebook
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(notebook, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Notebook created: {output_path}")
        print(f"📊 Statistics:")
        print(f"   - Total cells: {len(notebook['cells'])}")
        print(f"   - Code cells: {sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'code')}")
        print(f"   - Markdown cells: {sum(1 for cell in notebook['cells'] if cell['cell_type'] == 'markdown')}")
        
    except Exception as e:
        print(f"❌ Fatal error during conversion: {e}")
        if args.verbose:
            import traceback
            print("Full traceback:")
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main() 