import pytest
import pandas as pd
from fastapi import HTTPException
import sys
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE_DIR, "api")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

from validation import validate_csv_structure


def test_csv_with_invalid_column_names():
    """Test validation fails when CSV has incorrect column names."""
    # Load CSV with wrong column names (Company, Price instead of Kod, Kurs)
    df = pd.read_csv("data/test_invalid_cols.csv", sep=";")

    # Should raise HTTPException due to missing required columns
    with pytest.raises(HTTPException) as exc_info:
        validate_csv_structure(df)

    # Check that the error mentions missing columns
    assert exc_info.value.status_code == 400
    assert "Missing required columns" in str(exc_info.value.detail)
    assert "Kod" in str(exc_info.value.detail)
    assert "Kurs" in str(exc_info.value.detail)


def test_csv_with_missing_columns():
    """Test validation fails when CSV is missing required columns."""
    # Load CSV missing the Kurs column
    df = pd.read_csv("data/test_missing_columns.csv", sep=";")

    # Should raise HTTPException due to missing Kurs column
    with pytest.raises(HTTPException) as exc_info:
        validate_csv_structure(df)

    # Check that the error specifically mentions the missing Kurs column
    assert exc_info.value.status_code == 400
    assert "Missing required columns" in str(exc_info.value.detail)
    assert "Kurs" in str(exc_info.value.detail)


def test_csv_with_invalid_kurs_values():
    """Test validation fails when CSV has non-numeric values in Kurs column."""
    # Load CSV with invalid data in Kurs column
    df = pd.read_csv("data/test_nan_in_kurs.csv", sep=";")

    # Should raise HTTPException due to invalid data format
    with pytest.raises(HTTPException) as exc_info:
        validate_csv_structure(df)

    # Check that the error mentions invalid data format and the specific value
    assert exc_info.value.status_code == 400
    assert "Invalid data format in CSV" in str(exc_info.value.detail)
    assert "not_a_number" in str(exc_info.value.detail)
    assert "Row 1" in str(exc_info.value.detail)
