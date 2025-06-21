"""
Library Exploration Tools

A collection of tools for exploring and validating Python libraries,
including markdown-to-notebook conversion and notebook execution validation.

Usage:
    import library_exploration.convert_to_notebook
    import library_exploration.validate_notebook
    import library_exploration.test_code_blocks
    import library_exploration.test_conversion
"""

__version__ = "0.1.0"
__author__ = "Gregory Damiani"

# Import main modules for easy access
from . import convert_to_notebook
from . import validate_notebook
from . import test_code_blocks
from . import test_conversion 