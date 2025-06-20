# Test with Severe Issue

## Normal Block
```python
print("Hello")
```

## Block with Unicode Issues
```python
# This block has some problematic characters
print("Hello 世界")  # Unicode characters
print("Line with \x00 null byte")  # Null byte
```

## Block with Very Long Line
```python
# This line is extremely long and might cause issues: " + "x" * 10000 + "
very_long_line = "x" * 10000
print(very_long_line)
``` 