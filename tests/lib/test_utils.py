import pytest

from yottaml.error import ParameterValueError
from yottaml.lib.utils import (
    none_to_zero,
    check_gpu_count
)


def test_none_to_zero():
    """Test converting None and various values to integers"""
    # Test None value
    assert none_to_zero(None, "zero_tester") == 0

    # Test integer values
    assert none_to_zero(0, "zero_tester") == 0
    assert none_to_zero(42, "zero_tester") == 42
    assert none_to_zero(-42, "zero_tester") == -42

    # Test valid string values
    assert none_to_zero("0", "zero_tester") == 0
    assert none_to_zero("42", "zero_tester") == 42
    assert none_to_zero("-42", "zero_tester") == -42
    assert none_to_zero("  42  ", "zero_tester") == 42  # Whitespace
    assert none_to_zero("", "zero_tester") == 0  # Empty string
    assert none_to_zero("  ", "zero_tester") == 0  # Whitespace only

    # Test valid float values that are effectively integers
    assert none_to_zero(42.0, "zero_tester") == 42
    assert none_to_zero(-42.0, "zero_tester") == -42

    # Test invalid values
    with pytest.raises(ValueError):
        none_to_zero(1.5, "zero_tester")  # Float with decimal part

    with pytest.raises(ValueError):
        none_to_zero("1.5", "zero_tester")  # String float

    with pytest.raises(ValueError):
        none_to_zero("abc", "zero_tester")  # Non-numeric string

    with pytest.raises(ValueError):
        none_to_zero([], "zero_tester")  # List

    with pytest.raises(ValueError):
        none_to_zero({}, "zero_tester")  # Dict

    with pytest.raises(ValueError):
        none_to_zero(True, "zero_tester")  # Boolean

    with pytest.raises(ValueError):
        none_to_zero(False, "zero_tester")  # Boolean


class TestCheckGpuCount:
    def test_valid_powers_of_two(self):
        """Test valid gpu counts that are powers of 2"""
        valid_counts = [1, 2, 4, 8, 16, 32]
        for count in valid_counts:
            check_gpu_count(count)  # Should not raise any exception

    def test_invalid_positive_numbers(self):
        """Test positive numbers that are not powers of 2"""
        invalid_counts = [3, 5, 6, 7, 9, 10, 12, 15]
        for count in invalid_counts:
            with pytest.raises(ParameterValueError) as exc_info:
                check_gpu_count(count)
            assert "must be a power of 2" in str(exc_info.value)

    def test_zero_and_negative(self):
        """Test zero and negative numbers"""
        invalid_counts = [0, -1, -2, -4]
        for count in invalid_counts:
            with pytest.raises(ParameterValueError) as exc_info:
                check_gpu_count(count)
            assert "must be greater than 0" in str(exc_info.value)

    def test_non_integer_numbers(self):
        """Test floating point numbers"""
        invalid_counts = [1.5, 2.2, 4.7]
        for count in invalid_counts:
            with pytest.raises(ParameterValueError) as exc_info:
                check_gpu_count(count)
            assert "must be an integer" in str(exc_info.value)

    def test_non_numeric_types(self):
        """Test non-numeric types"""
        invalid_values = ["abc", "123", True, False, [], {}]
        for value in invalid_values:
            with pytest.raises(ParameterValueError) as exc_info:
                check_gpu_count(value)
            assert "gpu_count" in str(exc_info.value)

    def test_large_powers_of_two(self):
        """Test large numbers that are powers of 2"""
        large_valid_counts = [64, 128, 256]
        for count in large_valid_counts:
            check_gpu_count(count)  # Should not raise any exception
