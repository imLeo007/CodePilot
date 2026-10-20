import math

def multiply(a: int, b: int) -> int:
    return a * b

def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def divide(a: int, b: int) -> float:
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

def power(base: int, exponent: int) -> float:
    return base ** exponent

def cosine_degrees(angle: int) -> float:
    """Calculate the cosine of an angle in degrees."""
    return math.cos(math.radians(angle))

def sine_degrees(angle: int) -> float:
    """Calculate the sine of an angle in degrees."""
    return math.sin(math.radians(angle))

def sine_radians(angle: float) -> float:
    """Calculate the sine of an angle in radians."""
    return math.sin(angle)