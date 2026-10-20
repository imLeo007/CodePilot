from app.calculator import multiply, add, subtract, divide, power, cosine_degrees, sine_degrees, sine_radians
import pytest

def test_multiply_pos() -> None:
    assert multiply(2, 3) == 6

def test_multiply_neg() -> None:
    assert multiply(2, 4) == 8

def test_add_pos() -> None:
    assert add(2, 3) == 5

def test_add_neg() -> None:
    assert add(-1, -1) == -2

def test_subtract_pos() -> None:
    assert subtract(3, 2) == 1

def test_subtract_neg() -> None:
    assert subtract(1, 2) == -1

def test_divide_pos() -> None:
    assert divide(10, 2) == 5.0

def test_divide_by_zero() -> None:
    with pytest.raises(ValueError):
        divide(10, 0)

def test_power_pos() -> None:
    assert power(2, 3) == 8

def test_power_zero() -> None:
    assert power(5, 0) == 1

def test_power_one() -> None:
    assert power(1, 100) == 1

def test_power_negative_exponent() -> None:
    assert power(2, -3) == 0.125

def test_cosine_degrees_zero() -> None:
    assert cosine_degrees(0) == 1.0

def test_cosine_degrees_90() -> None:
    # Cosine of 90 degrees should be 0, but due to floating-point precision,
    # we check if it's very close to 0
    result = cosine_degrees(90)
    assert abs(result) < 1e-10

def test_sine_degrees_zero() -> None:
    assert sine_degrees(0) == 0.0

def test_sine_degrees_90() -> None:
    # Sine of 90 degrees should be 1
    assert sine_degrees(90) == 1.0

def test_sine_degrees_180() -> None:
    # Sine of 180 degrees should be 0
    result = sine_degrees(180)
    assert abs(result) < 1e-10

def test_sine_radians_zero() -> None:
    assert sine_radians(0) == 0.0

def test_sine_radians_pi_over_two() -> None:
    # Sine of π/2 should be 1
    import math
    assert sine_radians(math.pi / 2) == 1.0