# Test Edge Cases

## Empty Code Block
```python

```

## Code Block with Only Comments
```python
# This is just a comment
# Another comment
```

## Mixed Language Blocks
```javascript
console.log("JavaScript code");
```

```bash
echo "Bash command"
```

```python
print("Python code")
```

## Code Block with Special Characters
```python
# Test special characters
print("Quotes: 'single' and \"double\"")
print("Backslashes: \\n\\t\\r")
print("Unicode: 🐍📚🔍")
```

## Nested Code Blocks (should be treated as text)
```python
# This contains a nested block:
# ```python
# print("nested")
# ```
print("outer block")
```

## Very Short Code Block
```python
x=1
```

## Code Block with Trailing Spaces
```python
print("Hello")    
# Note the trailing spaces above
``` 