# Test File with Potential Issues

## Normal Python Block
```python
import requests
print("This should work fine")
```

## Python Block with Syntax Error
```python
def broken_function(
    # Missing closing parenthesis
    print("This has a syntax error"
```

## Shell Block
```bash
echo "Hello World"
```

## Python Block with Import Error
```python
import nonexistent_module
print("This will fail")
```

## Malformed Code Block
```python
# This block is missing the closing ```
print("This block is incomplete"

## Another Normal Block
```python
print("This should work")
``` 