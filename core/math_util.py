def add(a, b):
    """Adds two numbers and returns the sum."""
    return a + b

def subtract(a, b):
    """Subtracts the second number from the first and returns the difference."""
    return a - b

def multiply(a, b):
    """Multiplies two numbers and returns the product."""
    return a * b

def divide(a, b):
    """Divides the first number by the second and returns the quotient.
    Raises ValueError if the divisor is zero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
