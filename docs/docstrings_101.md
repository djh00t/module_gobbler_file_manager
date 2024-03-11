# Docstrings 101: A Beginner's Guide

## What Are Docstrings?

Docstrings, short for "documentation strings," are literal string literals that appear right after the definition of a function, method, class, or module. They are used to explain what the block of code does and how it works. Python automatically assigns these strings to the `__doc__` attribute of the respective object.

## How to Write Docstrings?

Docstrings are enclosed within triple quotes (`"""`). This allows for multi-line strings, which means you can write detailed documentation right inside your code.

### Function Docstrings

Here's an example of a simple function with a docstring:

```python
def add(a, b):
    """
    Add two numbers and return the result.
    
    Parameters:
    a (int): The first number to add.
    b (int): The second number to add.

    Returns:
    int: The sum of the two numbers.
    """
    return a + b
```

### Class Docstrings

Classes should have a docstring below the class definition describing the class:

```python
class Greeter:
    """
    A simple class for greeting people.
    
    Attributes:
    name (str): The name of the person to greet.

    Methods:
    greet(): Output a greeting message.
    """
    
    def __init__(self, name):
        self.name = name
    
    def greet(self):
        """Output a greeting message."""
        print(f"Hello, {self.name}!")
```

### Module Docstrings

At the beginning of a Python file (module), you can include a docstring to describe the purpose of the module:

```python
"""
This module provides basic mathematical operations like addition and subtraction.
"""
```

## Best Practices

1. **Consistency**: Stick to a consistent style for all your docstrings in your project.
2. **Clarity**: Write clear and concise docstrings that are easily understandable.
3. **Completeness**: Cover all important aspects like parameters, return values, and possible errors.
4. **Convention**: Follow established conventions like the [PEP 257](https://www.python.org/dev/peps/pep-0257/) docstring conventions.

## Benefits of Using Docstrings

- **Introspection**: They can be accessed using the `help()` function and `.__doc__` attribute, providing an easy way to understand what the code is supposed to do.
- **Documentation**: Tools like [Sphinx](https://www.sphinx-doc.org/en/master/) can automatically generate documentation from docstrings.
- **Readability**: Docstrings improve the readability of your code by providing developers with a quick way to understand the purpose of a function or class.

