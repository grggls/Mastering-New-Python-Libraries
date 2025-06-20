# 🐍 Mastering Python Libraries: An Interactive Exploration Guide
*From first import to production-ready code: a systematic approach to understanding any Python package*

**Author**: Gregory Damiani / [https://github.com/grggls](https://github.com/grggls)


**License**: CC BY-NC-SA (Attribution-NonCommercial-ShareAlike)

---

When you encounter a new Python library, interactive exploration becomes your most powerful learning tool. Whether you're using a Python REPL, IPython shell, or Jupyter notebook, the ability to experiment, inspect, and iterate in real-time transforms how quickly you can become productive with unfamiliar code.

The REPL (Read-Eval-Print Loop) excels at rapid experimentation and immediate feedback - perfect for testing hypotheses about how a library works. Jupyter notebooks complement this by serving as living documents where you can capture your exploration journey, document discoveries, and build reusable examples that become references for your team.

This guide provides a systematic approach to library exploration that goes beyond basic `help()` commands. You'll learn to understand the domain model, discover usage patterns, and write defensive, idiomatic code. The key insight is working backwards from your end goal: you want to understand not just *what* the library does, but *how* it thinks about the problem domain and *how* you should interact with it safely and efficiently.

---

## 📝 Language and Conventions

Before we dive into exploration techniques, let's clarify some terminology that often causes confusion, even among experienced Python developers.

**Module**: A single Python file (`.py`) containing Python code. For example, `math.py` is a module you can import with `import math`. Modules are the basic building blocks of Python code organization.

**Package**: A collection of modules organized in a directory structure with an `__init__.py` file. The `__init__.py` file tells Python to treat the directory as a package. Most third-party code you install with `pip` is technically a package, even if it feels like a single unit.

**Library**: A conceptual term referring to a collection of code that provides specific functionality. It could be a single module, multiple modules, or a complex package structure. In everyday conversation, "library" and "package" are often used interchangeably when referring to third-party code.

**Examples in practice:**
- `requests` - Technically a package with multiple internal modules, but everyone calls it a "library"
- `json` - A single module in Python's standard library
- `numpy` - A complex package structure, commonly called a "library"

**Throughout this guide**, we'll use these terms somewhat interchangeably as they appear in real-world usage, but when precision matters, we'll be specific. The exploration techniques work the same regardless of whether you're examining a simple module or a complex package.

**Import conventions**: When exploring, you'll often see different import styles:
```python
import requests                        # Import the whole package
from requests import Session           # Import specific items into the local namespace
import requests as req                 # Import with alias
```

Each style affects what's available in your namespace and how you access the library's functionality, which influences your exploration approach.

---

## 🔍 Basic Introspection

Start your exploration with these fundamental introspection techniques. These commands give you the essential structure of any Python object - whether it's a module, class, or function. Think of this as taking an X-ray of the library to see its skeleton.

```python
type(requests)     # Check if it's a module, class, etc.
dir(requests)      # List all attributes (functions, classes, constants)
vars(requests)     # Dictionary of module's namespace
```
The `dir()` function is particularly valuable because it shows you everything available in the namespace, while `vars()` gives you the underlying dictionary representation. Use `type()` to understand what kind of object you're dealing with - this affects how you can interact with it.

We imported both the whole package (`import requests`) as well as one module from it (`from requests import Session`). Therefore the last two statements here are functionally the same. 
```python
>>> type(requests)
<class 'module'>
>>> type(requests.Session)
<class 'type'>
>>> type(Session)
<class 'type'>
```

This show how we can keep our python code clean while keeping our namespace tidy. If we only need one class or function, then the `from module_name import class_name` style of importing will also keep your binaries small. 
---

## 📚 Documentation & Help

Good documentation is your roadmap to understanding a library's intended usage patterns. Python's built-in help system, combined with IPython's enhanced introspection, can reveal not just what functions do, but how the library authors expect you to use them.

```python
help(requests)             # View top-level docstring
help(requests.get)         # View docstring for function/class

# In IPython / Jupyter:
requests?                  # Show documentation
requests.get??             # Show source code (if available)

# Rich documentation exploration
import webbrowser
webbrowser.open(f"https://pypi.org/project/{requests.__name__}/")
```

The top-level module docstring often contains the library's philosophy and high-level usage patterns. Individual function and class docstrings reveal the expected interfaces and common gotchas. IPython's `??` operator is particularly powerful because it shows you the actual implementation, helping you understand performance characteristics and edge cases.

---

## 🔧 Essential Dunder Attributes

Dunder (double underscore) attributes are Python's way of exposing metadata about objects. These attributes tell you about the object's identity, location, and interface contracts - essential information for understanding how to work with the library safely.

```python
requests.__doc__      # Docstring
requests.__file__     # Path to module file
requests.__name__     # Module name
requests.__version__  # Version (if available)
```

The `__all__` dunder lists all shared public strings of a module, function, library, etc. If you're writing your own module and sharing it, it's good practice to declare and export an `__all__` for your project. However, not all well-used community libraries do this unfortunately.

```python
os.__all__           # All exported strings of a function, module, etc.
```

# For classes - understand the interface contract
requests.Response.__init__        # Constructor signature
requests.Response.__dict__        # Instance attributes
```

`__all__` is particularly important because it defines the public API - what the library authors consider safe and stable for external use. `__file__` helps you understand the library's structure and locate additional resources. For classes, `__slots__` tells you if the class uses memory optimization, which affects how you can dynamically add attributes.

## `__slots__` are unique interface detail that some packages use to optimize memory usage

`__slots__` is a special class attribute that tells Python to use a fixed-size array for storing instance attributes instead of a dynamic dictionary (`__dict__`). This optimization can significantly reduce memory usage and improve attribute access speed, especially for classes with many instances.

### Why Libraries Use `__slots__`

**Memory Optimization**: Classes with `__slots__` use 40-50% less memory per instance because they don't need to store a dictionary for each object.

**Performance**: Attribute access is faster since Python can directly access the slot instead of doing a dictionary lookup.

**Immutability**: Prevents adding new attributes after object creation, which can be useful for data classes and immutable objects.

### How to Explore `__slots__`

```python
# Check if a class uses __slots__
if hasattr(requests.Response, '__slots__'):
    print(f"Response uses __slots__: {requests.Response.__slots__}")
else:
    print("Response uses __dict__ for attributes")

# Compare memory usage (example with dataclasses)
from dataclasses import dataclass

@dataclass
class RegularPoint:
    x: int
    y: int

@dataclass(slots=True)
class SlottedPoint:
    x: int
    y: int

# RegularPoint.__slots__ -> AttributeError (uses __dict__)
# SlottedPoint.__slots__ -> ('x', 'y')

# Test attribute creation
regular = RegularPoint(1, 2)
regular.z = 3  # ✅ Works

slotted = SlottedPoint(1, 2)
# slotted.z = 3  # ❌ AttributeError: 'SlottedPoint' object has no attribute 'z'
```

### Common Libraries That Use `__slots__`

**Standard Library Examples:**
- `collections.namedtuple` - Uses empty `__slots__ = ()` to prevent new attributes
- `dataclasses` with `slots=True` - Modern way to create memory-efficient data classes
- `inspect.Signature` - Uses `__slots__ = ('_return_annotation', '_parameters')`

**Third-Party Libraries:**
- Many data science libraries (pandas, numpy) use `__slots__` for performance-critical classes
- ORM libraries often use `__slots__` for model classes
- Game engines and scientific computing libraries for memory efficiency

### Trade-offs of `__slots__`

**Advantages:**
- Reduced memory usage
- Faster attribute access
- Prevents accidental attribute creation

**Disadvantages:**
- Can't add new attributes dynamically
- More complex inheritance (can't easily mix with classes that don't use `__slots__`)
- No `__dict__` attribute (unless explicitly included in `__slots__`)

### When to Look for `__slots__`

Check for `__slots__` when:
- Working with data classes or immutable objects
- Performance is critical (many instances)
- You need to understand memory usage patterns
- Exploring libraries that handle large datasets

---

## 📦 Package Metadata & Dependencies

Understanding a package's metadata helps you assess its maturity, compatibility, and ecosystem integration. This information is crucial for making architectural decisions and understanding potential conflicts.

```bash
# Shell commands
$ pip show requests              # Basic package info
$ pip show --verbose requests    # Detailed info including dependencies
```

Python's package metadata system provides programmatic access to the same information you get from `pip show`, but with much more detail and flexibility. The `pkg_resources` and `importlib.metadata` modules let you inspect package versions, dependencies, entry points, and other metadata that can reveal a library's architecture and integration points.

This metadata exploration is particularly valuable for understanding dependency chains, identifying potential version conflicts, and discovering hidden functionality like command-line tools or plugin systems that might not be obvious from the main API.

```python
# Python introspection
import pkg_resources
import importlib.metadata

# Version info
dist = pkg_resources.get_distribution("requests")
print(f"Version: {dist.version}")
print(f"Location: {dist.location}")

# Dependencies
try:
    metadata = importlib.metadata.metadata("requests")
    print("Dependencies:", metadata.get_all("Requires-Dist"))
except importlib.metadata.PackageNotFoundError:
    print("Package metadata not found")

# Find all entry points (CLI commands, plugins, etc.)
entry_points = pkg_resources.get_entry_map("requests")
print("Entry points:", entry_points)
```

Dependencies reveal the library's ecosystem and potential version conflicts. Entry points show you if the package provides command-line tools or plugin interfaces - valuable for understanding the full scope of functionality.

---

## 🎨 Pretty-Print & Visualization

Complex data structures and nested objects can be overwhelming when printed with default Python formatting. These techniques help you visualize library structures and data in human-readable formats, making patterns and relationships more obvious.

```python
from pprint import pprint
import json

# Create some example data to pretty-print
data = {
    'requests': {
        'classes': ['Session', 'Response', 'Request'],
        'functions': ['get', 'post', 'put', 'delete'],
        'config': {
            'timeout': 30,
            'verify': True,
            'allow_redirects': True
        }
    }
}

# Pretty print complex structures
pprint(data, width=80, depth=3)
```

The `json.dumps()` function converts Python objects to a JSON string representation, making complex data structures readable and portable. The `indent=2` parameter creates nicely formatted, human-readable output, while `default=str` handles non-serializable objects by converting them to strings. The `print_module_tree()` function creates a hierarchical tree view of a module's structure, showing classes, functions, and their methods in an organized format. This visualization helps you quickly understand the library's architecture, identify the main components, and spot patterns in naming conventions that reveal the library's design principles.

```python
# JSON formatting for serializable data
print(json.dumps(data, indent=2, default=str))

# Tree-like visualization of module structure
def print_module_tree(module, max_depth=2, current_depth=0):
    """Print a tree view of module structure"""
    if current_depth >= max_depth:
        return
    
    indent = "  " * current_depth
    for name, obj in inspect.getmembers(requests):
        if not name.startswith('_'):
            obj_type = type(obj).__name__
            print(f"{indent}├── {name} ({obj_type})")
            
            if inspect.isclass(obj) and current_depth < max_depth - 1:
                for method_name, method in inspect.getmembers(obj, inspect.ismethod):
                    if not method_name.startswith('_'):
                        print(f"{indent}│   ├── {method_name}()")

print_module_tree(requests)
```

The tree visualization is particularly valuable for understanding hierarchical relationships and spotting naming patterns that reveal the library's organizational principles.

---

## 🧠 Deep Inspection

The `inspect` module is your Swiss Army knife for understanding Python objects at a deeper level. It reveals function signatures, source code, and type information that helps you write more robust code and understand performance implications.

```python
import inspect

# Get all members with their types
inspect.getmembers(requests)          # List all members
inspect.getsource(requests.get)       # Get source code
inspect.signature(requests.get)       # Show function signature

# Type checking for defensive programming. Like most/all *.isXYZ functions, these return a boolean
inspect.isfunction(obj)                   # Check if object is a function
inspect.isclass(obj)                      # Check if object is a class
inspect.ismodule(obj)                     # Check if object is a module
inspect.ismethod(obj)                     # Check if object is a method

# Parameter introspection for safe calling
sig = inspect.signature(requests.get)
for param_name, param in sig.parameters.items():
    print(f"{param_name}: {param.annotation}, default={param.default}")
```

Function signatures are particularly valuable because they show you not just what parameters are required, but also type hints and default values. This information is essential for writing defensive code that handles edge cases gracefully.

### Adding Deep Inspection To Your Own Code

To make your own functions work with `inspect.signature()` and other introspection tools, you need to understand how Python's signature system works. Here are the key approaches:

#### 1. Automatic Signature Detection (Most Common)

Python automatically detects signatures for most functions with type hints:

```python
import inspect

def my_library_function(name: str, age: int = 25, city: str = "NYC") -> str:
    """A function with type hints and defaults"""
    return f"{name} is {age} from {city}"

# inspect.signature() works automatically
sig = inspect.signature(my_library_function)
print(sig)  # (name: str, age: int = 25, city: str = "NYC") -> str

# Get parameter details
for param_name, param in sig.parameters.items():
    print(f"{param_name}: {param.annotation}, default={param.default}")
```

#### 2. Using `__annotations__` for Type Hints

```python
def my_dynamic_function(x, y, z):
    """Function without type hints in signature"""
    pass

# Add type hints after definition
my_dynamic_function.__annotations__ = {
    'x': int,
    'y': str, 
    'z': list,
    'return': bool
}

# Now inspect.signature() will show the types
sig = inspect.signature(my_dynamic_function)
print(sig)  # (x: int, y: str, z: list) -> bool
```

#### 3. Using `functools.wraps` for Decorators

```python
import functools
import inspect

def my_decorator(func):
    @functools.wraps(func)  # This preserves the original signature
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@my_decorator
def decorated_function(name: str, count: int = 1) -> str:
    return name * count

# inspect.signature() works correctly
sig = inspect.signature(decorated_function)
print(sig)  # (name: str, count: int = 1) -> str
```

#### 4. Custom Signature with `inspect.Signature`

For advanced cases, you can create custom signatures:

```python
import inspect
from inspect import Parameter

def my_dynamic_function(*args, **kwargs):
    """Function with dynamic behavior"""
    pass

# Create a custom signature
params = [
    Parameter('name', Parameter.POSITIONAL_OR_KEYWORD, annotation=str),
    Parameter('age', Parameter.POSITIONAL_OR_KEYWORD, default=25, annotation=int),
    Parameter('city', Parameter.KEYWORD_ONLY, default="NYC", annotation=str)
]

# Attach the signature
my_dynamic_function.__signature__ = inspect.Signature(
    parameters=params,
    return_annotation=str
)

# Now inspect.signature() works
sig = inspect.signature(my_dynamic_function)
print(sig)  # (name: str, age: int = 25, *, city: str = 'NYC') -> str
```

#### 5. Best Practices for Library Functions

```python
import inspect
from typing import Optional, List, Dict, Any

def my_library_api(
    endpoint: str,
    data: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    A well-documented library function that works great with inspect.signature()
    
    Args:
        endpoint: The API endpoint to call
        data: Optional data to send
        headers: Optional headers to include
        timeout: Request timeout in seconds
    
    Returns:
        Response data as dictionary
    """
    # Implementation here
    pass

# This automatically works with inspect.signature()
sig = inspect.signature(my_library_api)
print(sig)
# (endpoint: str, data: Optional[Dict[str, Any]] = None, 
#  headers: Optional[Dict[str, str]] = None, timeout: float = 30.0) -> Dict[str, Any]
```

#### Key Points for Your Own Code:

1. **Type hints are automatically detected** by `inspect.signature()`
2. **Default values are preserved** in the signature
3. **Return type annotations** are included
4. **`functools.wraps`** preserves signatures in decorators
5. **Custom signatures** can be created for special cases

The most common and recommended approach is to use **type hints** in your function definitions - Python will automatically make them work with `inspect.signature()` and other introspection tools.

---

## 🏗️ Domain Model Discovery

Understanding a library's domain model is crucial for writing code that aligns with the library's intended patterns. The domain model represents how the library thinks about the problem space - what are the core entities, what operations are available, and how do they relate to each other.

Domain-driven design principles apply to library exploration: you want to identify the ubiquitous language (naming conventions), bounded contexts (module boundaries), and core abstractions (main classes and interfaces). This understanding helps you write code that feels natural and maintainable.

```python
# Find the core abstractions and entities
classes = [name for name, obj in inspect.getmembers(requests, inspect.isclass)]
functions = [name for name, obj in inspect.getmembers(requests, inspect.isfunction)]
constants = [name for name in dir(requests) if name.isupper()]

print("Core Classes (Domain Entities):", classes)
print("Operations (Domain Services):", functions) 
print("Configuration/Constants:", constants)

# Explore class hierarchies to understand domain relationships
for cls_name in classes:
    cls = getattr(requests, cls_name)
    print(f"{cls_name}: {cls.__mro__}")  # Method Resolution Order shows inheritance
```

### Model Context Protocol Example:
```python
import mcp
# Discover the MCP domain abstractions
protocol_classes = [name for name, obj in inspect.getmembers(mcp, inspect.isclass) 
                    if any(term in name.lower() for term in ['server', 'client', 'transport', 'handler'])]
print("Protocol Domain Objects:", protocol_classes)

# Understand the communication patterns
transport_types = [name for name in dir(mcp) if 'transport' in name.lower()]
message_types = [name for name in dir(mcp) if 'message' in name.lower() or 'request' in name.lower()]
print("Transport mechanisms:", transport_types)
print("Message types:", message_types)
```

Class hierarchies (shown by `__mro__`) reveal inheritance relationships and help you understand which classes are specializations of others. Constants often represent configuration options or enumerated values that are important for proper usage.

---

## 🛡️ Defensive Exploration & Error Discovery

Defensive programming starts with understanding what can go wrong. By discovering a library's exception hierarchy and testing edge cases early, you can write more robust code and handle errors gracefully.

```python
# Discover what exceptions a library defines
exceptions = [name for name, obj in inspect.getmembers(requests, 
             lambda x: inspect.isclass(x) and issubclass(x, Exception))]
print("Custom Exceptions:", exceptions)

# Test parameter validation safely
def safe_explore_function(func, test_args=None):
    """Safely test a function with various inputs"""
    sig = inspect.signature(func)
    try:
        if not test_args:
            # Try calling with no args if no required params
            required_params = [p for p in sig.parameters.values() 
                             if p.default == inspect.Parameter.empty]
            if not required_params:
                result = func()
                print(f"✅ {func.__name__}() -> {type(result)}")
        else:
            result = func(*test_args)
            print(f"✅ {func.__name__}{test_args} -> {type(result)}")
    except Exception as e:
        print(f"❌ {func.__name__}: {type(e).__name__}: {e}")

# Example usage
safe_explore_function(requests.get, ("https://httpbin.org/get",))
```

Custom exceptions tell you what the library considers to be error conditions and how it expects you to handle them. The safe exploration function helps you test library functions without crashing your exploration session.

### MCP Error Handling Example:
```python
import mcp
# Discover MCP-specific error handling patterns
mcp_exceptions = [name for name, obj in inspect.getmembers(mcp, 
                 lambda x: inspect.isclass(x) and issubclass(x, Exception))]
print("MCP Error types:", mcp_exceptions)

# Look for error handling patterns
error_handlers = [name for name in dir(mcp) if 'error' in name.lower() or 'exception' in name.lower()]
print("Error handling utilities:", error_handlers)
```

---

## 🎯 Usage Pattern Discovery

Libraries often follow common patterns that aren't immediately obvious from their API documentation. By analyzing naming conventions, method patterns, and docstring examples, you can discover the idiomatic ways to use the library.

```python
# Find example usage in docstrings
import re

def find_usage_examples(module):
    """Extract code examples from docstrings"""
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, '__doc__') and obj.__doc__:
            # Look for >>> patterns (doctest style)
            examples = re.findall(r'>>> .*(?:\n.*)*?', obj.__doc__)
            if examples:
                print(f"\n{name} examples:")
                for example in examples:
                    print(example)

find_usage_examples(requests)

# Discover common patterns by analyzing method names
def analyze_api_patterns(module):
    """Identify common API patterns"""
    methods = [name for name, obj in inspect.getmembers(module, inspect.isfunction)]
    
    # CRUD operations
    crud_ops = {'create': [], 'read': [], 'update': [], 'delete': []}
    for method in methods:
        for op in crud_ops:
            if op in method.lower():
                crud_ops[op].append(method)
    
    # Async patterns
    async_methods = [m for m in methods if m.startswith('a') or 'async' in m]
    
    print("CRUD Operations:", crud_ops)
    print("Async Methods:", async_methods)

analyze_api_patterns(requests)
```

CRUD pattern analysis helps you understand how the library handles data operations, while async pattern discovery reveals whether the library supports concurrent operations and how to use them properly.

---

## ⚡ Performance Introspection

Understanding the performance characteristics of library functions helps you make informed decisions about when and how to use them. Simple profiling during exploration can reveal performance bottlenecks before they become problems in production.

```python
import timeit
import sys
import tracemalloc

# Quick performance check
def profile_function(func, *args, **kwargs):
    """Quick performance profiling of a function"""
    # Time it
    time_taken = timeit.timeit(lambda: func(*args, **kwargs), number=1000)
    print(f"⏱️ {func.__name__}: {time_taken:.4f}s for 1000 calls")
    
    # Memory usage
    tracemalloc.start()
    result = func(*args, **kwargs)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"🧠 Memory: {current / 1024:.2f} KB current, {peak / 1024:.2f} KB peak")
    
    return result

# Check object sizes
def object_size_analysis(obj):
    """Analyze memory footprint of objects"""
    print(f"Object size: {sys.getsizeof(obj)} bytes")
    if hasattr(obj, '__dict__'):
        print(f"Dict size: {sys.getsizeof(obj.__dict__)} bytes")
        print(f"Attributes: {len(obj.__dict__)}")

# Example usage
# profile_function(requests.get, "https://httpbin.org/get")
```

Memory profiling is particularly important for libraries that create large objects or process significant amounts of data. Object size analysis helps you understand the memory overhead of different approaches.

---

## 🧪 Interactive Exploration Workflow

Having a systematic workflow for exploration ensures you don't miss important aspects of a library and helps you build understanding progressively from high-level concepts to specific implementation details.

```python
# Complete exploration template
def explore_package(package_name):
    """Complete package exploration workflow"""
    print(f"🔍 Exploring {package_name}")
    print("=" * 50)
    
    # 1. Import and basic info
    try:
        package = __import__(package_name)
        print(f"✅ Successfully imported {package_name}")
        print(f"📁 Location: {package.__file__}")
        print(f"📋 Type: {type(package)}")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return
    
    # 2. High-level structure
    public_api = [name for name in dir(package) if not name.startswith('_')]
    print(f"\n🏗️ Public API ({len(public_api)} items):")
    print(", ".join(public_api[:10]), "..." if len(public_api) > 10 else "")
    
    # 3. Domain model discovery
    classes = [name for name, obj in inspect.getmembers(package, inspect.isclass)]
    functions = [name for name, obj in inspect.getmembers(package, inspect.isfunction)]
    
    print(f"\n🎯 Domain Model:")
    print(f"  Classes: {len(classes)} - {', '.join(classes[:5])}")
    print(f"  Functions: {len(functions)} - {', '.join(functions[:5])}")
    
    # 4. Quick help
    if hasattr(package, '__doc__') and package.__doc__:
        print(f"\n📚 Description:")
        print(package.__doc__[:200] + "..." if len(package.__doc__) > 200 else package.__doc__)
    
    print(f"\n💡 Next steps:")
    print(f"  - help({package_name}) for detailed docs")
    print(f"  - explore main classes: {classes[:3]}")
    print(f"  - try key functions: {functions[:3]}")

# Usage examples
# explore_package('requests')
# explore_package('json')
# explore_package('webbrowser')
```

This workflow template provides a consistent starting point for any library exploration. It builds understanding progressively and gives you concrete next steps for deeper investigation.

---

## 🚀 Pro Tips for Productive Exploration

### Use IPython Magic
```bash
pip install ipython rich
ipython
```

IPython transforms your exploration experience with enhanced introspection capabilities, tab completion, and rich formatting. The `%timeit` magic command is particularly useful for quick performance testing, while `%pdb` drops you into the debugger when exceptions occur.

### Quick Testing Patterns
```python
# Create a sandbox namespace for safe experimentation
import types
sandbox = types.ModuleType('sandbox')

# Test configurations safely
test_configs = [
    {'timeout': 5},
    {'timeout': 10, 'verify': False},
    {}  # Empty config
]

for config in test_configs:
    try:
        session = requests.Session()
        # Test session configuration
        for key, value in config.items():
            setattr(session, key, value)
        print(f"✅ Config {config} -> Session configured")
    except Exception as e:
        print(f"❌ Config {config} -> {type(e).__name__}: {e}")
```

The sandbox pattern is particularly useful when you're not sure if library functions have side effects. Testing multiple configurations quickly reveals the flexibility and constraints of the library's interfaces.

### MCP Specific Exploration
```python
# Discover MCP server/client patterns
import mcp

# Find builder/factory patterns for MCP components
builders = [name for name in dir(mcp) if any(term in name.lower() 
           for term in ['builder', 'factory', 'create'])]
print("MCP builders:", builders)

# Explore server and client abstractions
server_types = [name for name in dir(mcp) if 'server' in name.lower()]
client_types = [name for name in dir(mcp) if 'client' in name.lower()]
print("Server types:", server_types)
print("Client types:", client_types)

# Understand transport and protocol layers
transport_classes = [name for name, obj in inspect.getmembers(mcp, inspect.isclass)
                    if 'transport' in name.lower()]
protocol_classes = [name for name, obj in inspect.getmembers(mcp, inspect.isclass)
                   if 'protocol' in name.lower()]
print("Transport layer:", transport_classes)
print("Protocol layer:", protocol_classes)
```

---

## 🎯 Conclusion

Effective library exploration is about building understanding systematically, from high-level domain concepts to specific implementation details. By following this guide, you've learned to:

**Understand the Structure**: Basic introspection and documentation exploration give you the lay of the land, while dunder attributes reveal the object's identity and contracts.

**Map the Domain**: Domain model discovery helps you understand how the library thinks about the problem space, enabling you to write code that aligns with the library's intended patterns.

**Explore Safely**: Defensive exploration techniques help you understand error conditions and edge cases without breaking your exploration session.

**Discover Patterns**: Usage pattern analysis reveals idiomatic approaches and common workflows that may not be obvious from documentation alone.

**Assess Performance**: Performance introspection helps you make informed decisions about when and how to use different library features.

**Work Systematically**: The interactive exploration workflow ensures comprehensive coverage and gives you a repeatable process for any new library.

The key insight is that library exploration is not just about learning the API - it's about understanding the library's mental model and design philosophy. When you understand how a library thinks about the problem domain, you can write code that feels natural, performs well, and handles edge cases gracefully.

Remember to start broad with the exploration workflow, then dive deep into the specific classes and functions that map to your domain needs. The REPL is your laboratory for understanding not just what the library can do, but how it expects to be used.

**Happy exploring!** 🐍✨

---

## 🛠️ Automation Tools

This project includes several automation tools to convert the README into different formats for enhanced learning and documentation.

### 📓 Interactive Jupyter Notebook

The README can be automatically converted to an interactive Jupyter notebook where:
- **Python code blocks** become executable code cells
- **Shell/bash commands** become terminal cells using `%%bash` magic
- **Markdown content** becomes documentation cells
- **Headers and structure** are preserved

#### Quick Start

```bash
# Convert README to notebook
python3 convert_to_notebook.py README.md -o Mastering-New-Python-Libraries.ipynb

# Or use the Makefile
make notebook

# Open the notebook
jupyter notebook Mastering-New-Python-Libraries.ipynb
```

#### Features

- **Automatic Setup Cell**: Includes imports and configuration
- **Shell Command Support**: Uses `%%bash` magic for terminal commands
- **Enhanced Comments**: Adds context to shell commands
- **Error Handling**: Includes helpful comments for troubleshooting

#### Notebook Structure

```python
# Setup cell (auto-generated)
import sys
import os
from pathlib import Path
%load_ext ipython_magic_bash
from IPython.display import display, HTML
import warnings
warnings.filterwarnings('ignore')

# Example shell command cell
%%bash
# Install Python package
pip install requests
# Note: If this command fails, you may need to install dependencies or adjust paths

# Example Python code cell
import requests
response = requests.get('https://httpbin.org/get')
print(response.json())
```

### 📄 PDF Generation

Generate a professional PDF version of the README:

```bash
# Build PDF
make pdf

# Or manually with pandoc
pandoc README.md \
  --pdf-engine=xelatex \
  --variable=geometry:margin=1in \
  --variable=fontsize:11pt \
  --variable=mainfont:"DejaVu Sans" \
  --variable=monofont:"DejaVu Sans Mono" \
  --variable=colorlinks:true \
  --toc \
  --number-sections \
  --output=Mastering-New-Python-Libraries.pdf
```

### 🔄 Automation Options

#### Pre-commit Hook

A Git pre-commit hook automatically converts the README to a notebook when you commit changes:

```bash
# The hook is already installed at .git/hooks/pre-commit
# It will automatically run when you commit changes to README.md
git add README.md
git commit -m "feat: add new exploration techniques"
# Notebook is automatically generated and added to commit
```

#### GitHub Actions

Two GitHub Actions workflows automatically build artifacts:

1. **PDF Build** (`.github/workflows/build-pdf.yml`):
   - Triggers on tags and README changes
   - Creates semantic versions from commit messages
   - Generates PDF with professional formatting
   - Creates GitHub releases on tags
   - Comments on PRs with artifact information

2. **Notebook Build** (`.github/workflows/build-notebook.yml`):
   - Triggers on README changes
   - Converts README to interactive notebook
   - Uploads notebook as artifact
   - Comments on PRs with notebook statistics

#### Makefile Commands

```bash
make help          # Show all available commands
make notebook      # Convert README to notebook
make pdf           # Build PDF from README
make all           # Build both notebook and PDF
make clean         # Remove generated files
make install       # Install dependencies with Rye
make sync          # Sync Rye environment
```

#### VS Code Tasks

VS Code tasks are configured in `.vscode/tasks.json`:

- **Build Notebook**: Convert README to Jupyter notebook
- **Build PDF**: Generate PDF from README
- **Build All**: Run both notebook and PDF builds
- **Open Notebook**: Launch Jupyter notebook

Access via `Cmd+Shift+P` → "Tasks: Run Task"

### 🎯 Use Cases

#### For Learners
- **Interactive Exploration**: Run all code examples directly in the notebook
- **Shell Commands**: Execute `pip install` and other commands without leaving the notebook
- **Progressive Learning**: Work through examples step-by-step with immediate feedback

#### For Educators
- **Live Demonstrations**: Use the notebook for live coding sessions
- **Student Assignments**: Distribute the notebook for hands-on learning
- **Version Control**: Track changes to examples and explanations

#### For Documentation
- **Living Documentation**: Keep code examples synchronized with documentation
- **Multiple Formats**: Maintain both markdown and notebook versions
- **Automated Updates**: Ensure consistency across all formats

### 🔧 Configuration

#### Customizing the Conversion

```python
# Modify convert_to_notebook.py for custom behavior
python3 convert_to_notebook.py README.md \
  --output custom-notebook.ipynb \
  --no-setup \
  --no-toc
```

#### Dependencies

The conversion requires:
- `ipython_magic_bash` for shell command execution
- `jupyter` for notebook viewing
- `pandoc` for PDF generation

Install with:
```bash
rye sync  # Installs all dependencies including ipython_magic_bash
```

#### Environment Setup

For optimal notebook experience:
```bash
# Install Jupyter extensions
pip install jupyter_contrib_nbextensions
jupyter contrib nbextension install --user

# Enable useful extensions
jupyter nbextension enable toc2/main  # Table of contents
jupyter nbextension enable codefolding/main  # Code folding
```

### 🚀 Advanced Features

#### Custom Cell Processing

The conversion script can be extended to:
- Add custom imports based on code content
- Generate test cells for code examples
- Add performance profiling cells
- Include interactive visualizations

#### Integration with Other Tools

- **nbconvert**: Convert notebooks to other formats (HTML, slides, etc.)
- **papermill**: Parameterize notebooks for batch processing
- **jupytext**: Sync notebooks with markdown files

#### Continuous Integration

The automation works seamlessly with:
- **GitHub Actions**: Automated builds on every change
- **GitLab CI**: Similar workflows for GitLab repositories
- **Local Development**: Pre-commit hooks for immediate feedback

This automation system ensures that your documentation stays current, interactive, and accessible in multiple formats while maintaining the quality and consistency of your learning materials.