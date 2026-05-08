"""
tests/test_calculator.py — Unit tests for core BMI calculation logic.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.core.calculator import (
    calculate_bmi, get_category, ideal_weight_range,
    lbs_to_kg, kg_to_lbs, inches_to_cm, cm_to_inches,
    feet_inches_to_cm, compute_stats, BMIRecord,
)


# ── calculate_bmi ─────────────────────────────────────────────────────────────

class TestCalculateBMI:
    def test_normal_values(self):
        bmi = calculate_bmi(70, 175)
        assert bmi == pytest.approx(22.86, abs=0.01)

    def test_underweight(self):
        bmi = calculate_bmi(45, 170)
        assert bmi < 18.5

    def test_obese(self):
        bmi = calculate_bmi(120, 170)
        assert bmi > 30

    def test_zero_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70, 0)

    def test_negative_height_raises(self):
        with pytest.raises(ValueError):
            calculate_bmi(70, -5)

    def test_returns_float(self):
        result = calculate_bmi(80, 180)
        assert isinstance(result, float)

    def test_rounded_to_two_decimals(self):
        result = calculate_bmi(73, 178)
        assert result == round(result, 2)


# ── get_category ──────────────────────────────────────────────────────────────

class TestGetCategory:
    def test_severely_underweight(self):
        label, colour, emoji = get_category(14.0)
        assert label == "Severely Underweight"

    def test_underweight(self):
        label, _, _ = get_category(17.0)
        assert label == "Underweight"

    def test_normal(self):
        label, colour, _ = get_category(22.5)
        assert label == "Normal Weight"
        assert colour == "#2ecc71"

    def test_overweight(self):
        label, _, _ = get_category(27.0)
        assert label == "Overweight"

    def test_obese_class_1(self):
        label, _, _ = get_category(32.0)
        assert label == "Obese Class I"

    def test_obese_class_3(self):
        label, _, _ = get_category(45.0)
        assert label == "Obese Class III"

    def test_boundary_normal_lower(self):
        label, _, _ = get_category(18.5)
        assert label == "Normal Weight"

    def test_boundary_overweight(self):
        label, _, _ = get_category(25.0)
        assert label == "Overweight"


# ── ideal_weight_range ────────────────────────────────────────────────────────

class TestIdealWeightRange:
    def test_returns_tuple(self):
        lo, hi = ideal_weight_range(170)
        assert isinstance(lo, float) and isinstance(hi, float)

    def test_lo_less_than_hi(self):
        lo, hi = ideal_weight_range(170)
        assert lo < hi

    def test_known_value(self):
        lo, hi = ideal_weight_range(175)
        assert lo == pytest.approx(56.6, abs=0.2)
        assert hi == pytest.approx(76.3, abs=0.2)


# ── Unit conversions ──────────────────────────────────────────────────────────

class TestConversions:
    def test_lbs_to_kg(self):
        assert lbs_to_kg(154) == pytest.approx(69.85, abs=0.1)

    def test_kg_to_lbs_roundtrip(self):
        assert kg_to_lbs(lbs_to_kg(200)) == pytest.approx(200, abs=0.1)

    def test_inches_to_cm(self):
        assert inches_to_cm(70) == pytest.approx(177.8, abs=0.1)

    def test_cm_to_inches_roundtrip(self):
        assert cm_to_inches(inches_to_cm(68)) == pytest.approx(68, abs=0.1)

    def test_feet_inches_to_cm(self):
        # 5 ft 10 in = 177.8 cm
        assert feet_inches_to_cm(5, 10) == pytest.approx(177.8, abs=0.1)

    def test_feet_only(self):
        assert feet_inches_to_cm(6, 0) == pytest.approx(182.88, abs=0.1)


# ── compute_stats ─────────────────────────────────────────────────────────────

def _make_record(bmi_val: float, category: str = "Normal Weight") -> BMIRecord:
    return BMIRecord(
        user="Test", weight_kg=70, height_cm=175,
        bmi=bmi_val, category=category,
    )


class TestComputeStats:
    def test_empty_returns_none(self):
        assert compute_stats([]) is None

    def test_count(self):
        records = [_make_record(22.0), _make_record(24.0)]
        stats = compute_stats(records)
        assert stats["count"] == 2

    def test_average(self):
        records = [_make_record(20.0), _make_record(24.0)]
        stats = compute_stats(records)
        assert stats["average"] == pytest.approx(22.0, abs=0.01)

    def test_lowest_highest(self):
        records = [_make_record(18.0), _make_record(28.0), _make_record(23.0)]
        stats = compute_stats(records)
        assert stats["lowest"] == 18.0
        assert stats["highest"] == 28.0

    def test_trend_positive(self):
        records = [_make_record(22.0), _make_record(24.0)]
        stats = compute_stats(records)
        assert stats["trend"] == pytest.approx(2.0, abs=0.01)

    def test_trend_negative(self):
        records = [_make_record(26.0), _make_record(23.0)]
        stats = compute_stats(records)
        assert stats["trend"] == pytest.approx(-3.0, abs=0.01)

    def test_single_record_trend_none(self):
        stats = compute_stats([_make_record(22.0)])
        assert stats["trend"] is None

    def test_category_counts(self):
        records = [
            _make_record(22.0, "Normal Weight"),
            _make_record(22.5, "Normal Weight"),
            _make_record(27.0, "Overweight"),
        ]
        stats = compute_stats(records)
        assert stats["categories"]["Normal Weight"] == 2
        assert stats["categories"]["Overweight"] == 1
