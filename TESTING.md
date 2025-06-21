# 🧪 Testing and Validation Guide

This document describes the testing strategy, test scripts, and test files used to ensure the reliability and correctness of the automation and code conversion tools in this project.

## Overview

The project includes several layers of testing:
- **Code block validation**: Ensures all Python code blocks in the README are syntactically valid.
- **Conversion script testing**: Verifies that `convert_to_notebook.py` correctly converts Markdown to Jupyter notebooks, even with edge cases and problematic code blocks.
- **Functional and integration tests**: Checks that generated notebooks are valid and that the automation pipeline works end-to-end.

## Test Scripts

### 1. `test_code_blocks.py`
- **Purpose**: Extracts all Python code blocks from `README.md` and checks their syntax using Python's AST parser.
- **How to run**:
  ```bash
  python test_code_blocks.py
  ```
- **What it does**:
  - Reports the line number and content of any code block with syntax errors.
  - Validates that all code blocks are parseable Python.
  - Also tests the conversion script and generated notebook structure.

### 2. `test_conversion.py`
- **Purpose**: Runs the conversion script on a suite of test Markdown files with various edge cases and validates the output.
- **How to run**:
  ```bash
  python test_conversion.py
  # or with verbose output:
  python test_conversion.py --verbose
  ```
- **What it does**:
  - Converts each test file to a notebook.
  - Checks that the notebook is valid JSON and has the expected number of cells.
  - Reports detailed output and errors for each test file.

### 3. Makefile Targets
- **test**: Runs `test_code_blocks.py`.
- **test-conversion**: Runs `test_conversion.py` on all test files.
- **test-conversion-verbose**: Runs `test_conversion.py` in verbose mode.
- **validate**: Runs both code block validation and a conversion of the README to a notebook.
- **ci**: Runs the full suite (test, test-conversion, validate, notebook, pdf).

Example usage:
```bash
make test
make test-conversion
make test-conversion-verbose
make validate
make ci
```

## Test Files

### `test_problematic.md`
Contains code blocks with:
- Valid Python
- Syntax errors
- Import errors
- Malformed/incomplete code blocks
- Shell and Python code

### `test_severe_issue.md`
Contains code blocks with:
- Unicode and null bytes
- Extremely long lines
- Valid and edge-case Python

### `test_edge_cases.md`
Contains code blocks with:
- Empty blocks
- Only comments
- Mixed languages (Python, Bash, JavaScript)
- Special characters
- Nested code blocks (as text)
- Trailing spaces

These files are tracked in git for regression testing and are ignored in notebook output via `.gitignore`.

## How to Add New Tests
- Add a new `test_*.md` file with your edge cases or scenarios.
- Add the filename to the `test_files` list in `test_conversion.py` if you want it included in the automated suite.
- Run `make test-conversion` to validate.

## CI and Automation
- All tests are run automatically in GitHub Actions workflows on push and pull request.
- The workflow will fail if any code block or conversion test fails.
- Artifacts (notebooks, PDFs) are uploaded for inspection.

## Troubleshooting
- If a test fails, check the output for the exact code block and error.
- Use verbose mode for more context:
  ```bash
  make test-conversion-verbose
  ```
- Fix the code block or script, then re-run the tests.

---

**Maintainer tip:** Always run `make ci` before pushing to ensure all automation and tests pass locally!

```python
def minimal():
    pass
``` 