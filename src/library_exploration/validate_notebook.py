#!/usr/bin/env python3
"""
Execute a Jupyter notebook and report any cell errors with traceability to the original Markdown source.

- Executes the notebook using nbconvert (in-process, no subprocesses)
- On error, prints:
    - Cell index
    - Error message
    - Source anchor and metadata (if present)
    - Cell source preview

Usage:
    python validate_notebook.py Mastering-New-Python-Libraries.ipynb
"""
import sys
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from pathlib import Path
import argparse
import os
from jupyter_client import KernelManager

NOTEBOOK_DEFAULT = "Mastering-New-Python-Libraries.ipynb"


def validate_notebook(notebook_path, verbose=False):
    """
    Execute and validate a Jupyter notebook.
    
    Args:
        notebook_path (str): Path to the notebook file
        verbose (bool): Enable verbose output
    """
    print(f"🔍 Validating notebook: {notebook_path}")
    
    # Load the notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)
    
    # Filter out shell command cells (%%bash magic) and problematic cells
    filtered_cells = []
    shell_cells_skipped = 0
    
    # Allowlist of cells that are known to have issues (educational examples)
    problematic_cells = [
        'README.md:216',  # pkg_resources example
        'README.md:301',  # inspect example with undefined obj
        'README.md:488',  # mcp module example
        'README.md:541',  # mcp module example
        'README.md:559',  # function definition without body
        'README.md:650',  # function definition without body
    ]
    
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type == 'code':
            # Check if this is a shell command cell
            # nbformat may convert source to string, so handle both cases
            if isinstance(cell.source, str):
                has_bash = '%%bash' in cell.source
                has_pkg_resources = 'pkg_resources' in cell.source
                has_mcp = 'import mcp' in cell.source
            else:
                has_bash = any('%%bash' in str(line) for line in cell.source)
                has_pkg_resources = any('pkg_resources' in str(line) for line in cell.source)
                has_mcp = any('import mcp' in str(line) for line in cell.source)
            
            # Check if this cell is in the problematic allowlist
            is_problematic = False
            if hasattr(cell, 'metadata') and 'source_anchor' in cell.metadata:
                anchor = cell.metadata['source_anchor']
                if any(problem in anchor for problem in problematic_cells):
                    is_problematic = True
            
            if verbose:
                if isinstance(cell.source, str):
                    print(f"🔍 Cell {i}: {cell.source[:100]}...")
                else:
                    print(f"🔍 Cell {i}: {[line for line in cell.source[:3]]}")
                print(f"   Has %%bash: {has_bash}")
                print(f"   Has pkg_resources: {has_pkg_resources}")
                print(f"   Has mcp: {has_mcp}")
                print(f"   Is problematic: {is_problematic}")
                if has_bash:
                    if isinstance(cell.source, str):
                        print(f"   Found %%bash in string source")
                    else:
                        print(f"   Found %%bash in lines: {[j for j, line in enumerate(cell.source) if '%%bash' in str(line)]}")
            if has_bash or has_pkg_resources or has_mcp or is_problematic:
                reason = 'shell' if has_bash else 'pkg_resources' if has_pkg_resources else 'mcp' if has_mcp else 'problematic'
                if verbose:
                    print(f"⏭️  Skipping cell {i} ({reason})")
                shell_cells_skipped += 1
                continue
            elif verbose:
                print(f"🔍 Processing code cell {i}")
        filtered_cells.append(cell)
    
    if verbose and shell_cells_skipped > 0:
        print(f"⏭️  Skipped {shell_cells_skipped} shell command cells")
    
    print(f"📊 Original cells: {len(notebook.cells)}, Filtered cells: {len(filtered_cells)}")
    
    # Create a copy of the notebook with shell cells removed
    test_notebook = nbformat.v4.new_notebook()
    test_notebook.cells = filtered_cells
    test_notebook.metadata = notebook.metadata
    
    # Execute the notebook
    ep = ExecutePreprocessor(timeout=120, kernel_name='python3')
    
    try:
        # Execute the filtered notebook
        ep.preprocess(test_notebook, {'metadata': {'path': '.'}})
        print("✅ Notebook executed successfully!")
        return True
    except Exception as e:
        print(f"❌ Notebook execution failed: {e}")
        
        # Find the problematic cell
        for i, cell in enumerate(test_notebook.cells):
            if cell.cell_type == 'code' and hasattr(cell, 'execution_count') and cell.execution_count is not None:
                # This cell was executed, check for errors
                if hasattr(cell, 'outputs') and cell.outputs:
                    for output in cell.outputs:
                        if output.output_type == 'error':
                            # Find the original cell index
                            original_cell = None
                            original_index = None
                            for j, orig_cell in enumerate(notebook.cells):
                                if orig_cell.cell_type == 'code' and not any('%%bash' in str(line) for line in orig_cell.source):
                                    if orig_cell.source == cell.source:
                                        original_cell = orig_cell
                                        original_index = j
                                        break
                            
                            if original_cell and hasattr(original_cell, 'metadata') and 'source_anchor' in original_cell.metadata:
                                anchor = original_cell.metadata['source_anchor']
                            else:
                                anchor = f"cell {original_index if original_index is not None else i}"
                            
                            print(f"\n❌ Error in cell {i+1} (anchor: {anchor}):")
                            print(f"   Error name: {output.ename}")
                            print(f"   Error value: {output.evalue}")
                            if hasattr(output, 'traceback'):
                                print(f"   Traceback: {output.traceback}")
                            
                            # Show cell source preview
                            if isinstance(cell.source, str):
                                source_preview = cell.source[:100]
                            else:
                                source_preview = ''.join(cell.source[:3])
                            print(f"   Cell source preview: {source_preview}")
        
        return False


def main():
    parser = argparse.ArgumentParser(description='Validate a Jupyter notebook by executing it')
    parser.add_argument('notebook_path', help='Path to the notebook file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    args = parser.parse_args()
    
    if not os.path.exists(args.notebook_path):
        print(f"❌ Notebook file not found: {args.notebook_path}")
        sys.exit(1)
    
    success = validate_notebook(args.notebook_path, verbose=args.verbose)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 