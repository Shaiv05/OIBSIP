"""
tests/test_validators.py — Unit tests for input validation.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.core.validators import (
    ValidationError, validate_name,
    validate_weight_kg, validate_weight_lbs,
    validate_height_cm, validate_height_feet,
)


class TestValidateName:
    def test_valid(self):
        assert validate_name("alice") == "Alice"

    def test_title_case(self):
        assert validate_name("john doe") == "John Doe"

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_name("")

    def test_single_char_raises(self):
        with pytest.raises(ValidationError):
            validate_name("a")

    def test_too_long_raises(self):
        with pytest.raises(ValidationError):
            validate_name("x" * 51)

    def test_strips_whitespace(self):
        assert validate_name("  Bob  ") == "Bob"


class TestValidateWeightKg:
    def test_valid(self):
        assert validate_weight_kg("70") == 70.0

    def test_float_string(self):
        assert validate_weight_kg("72.5") == pytest.approx(72.5)

    def test_zero_raises(self):
        with pytest.raises(ValidationError):
            validate_weight_kg("0")

    def test_too_heavy_raises(self):
        with pytest.raises(ValidationError):
            validate_weight_kg("601")

    def test_non_numeric_raises(self):
        with pytest.raises(ValidationError):
            validate_weight_kg("abc")


class TestValidateHeightCm:
    def test_valid(self):
        assert validate_height_cm("175") == 175.0

    def test_below_min_raises(self):
        with pytest.raises(ValidationError):
            validate_height_cm("49")

    def test_above_max_raises(self):
        with pytest.raises(ValidationError):
            validate_height_cm("301")

    def test_non_numeric_raises(self):
        with pytest.raises(ValidationError):
            validate_height_cm("tall")


class TestValidateHeightFeet:
    def test_valid(self):
        ft, ins = validate_height_feet("5", "10")
        assert ft == 5.0 and ins == 10.0

    def test_no_inches_defaults_zero(self):
        ft, ins = validate_height_feet("6", "")
        assert ins == 0.0

    def test_bad_feet_raises(self):
        with pytest.raises(ValidationError):
            validate_height_feet("10", "0")

    def test_bad_inches_raises(self):
        with pytest.raises(ValidationError):
            validate_height_feet("5", "12")

    def test_non_numeric_feet_raises(self):
        with pytest.raises(ValidationError):
            validate_height_feet("five", "0")
