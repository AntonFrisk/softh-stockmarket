#!/usr/bin/env python3
"""
Test script to verify Pydantic validation is working correctly
"""

import requests
import pandas as pd
import io

# Test with missing columns
print("=== Testing CSV Validation ===")


def test_missing_columns():
    print("\n1. Testing missing columns...")

    # Create CSV data with missing Kurs column
    csv_data = """Date;Kod
2017-01-01 12:00:00;ABB
2017-01-01 12:00:01;NCC"""

    try:
        response = requests.post(
            "http://localhost:8000/get_daily_winners_from_file",
            files={"file": ("test.csv", csv_data, "text/csv")},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")


def test_invalid_price():
    print("\n2. Testing invalid price data...")

    # Create CSV data with invalid price
    csv_data = """Date;Kod;Kurs
2017-01-01 12:00:00;ABB;not_a_number
2017-01-01 12:00:01;NCC;122"""

    try:
        response = requests.post(
            "http://localhost:8000/get_daily_winners_from_file",
            files={"file": ("test.csv", csv_data, "text/csv")},
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")


def test_valid_data():
    print("\n3. Testing valid data...")

    # Create CSV data with valid structure
    csv_data = """Date;Kod;Kurs
2017-01-01 12:00:00;ABB;217
2017-01-01 12:00:01;NCC;122
2017-01-01 12:00:02;ABB;218"""

    try:
        response = requests.post(
            "http://localhost:8000/get_daily_winners_from_file",
            files={"file": ("test.csv", csv_data, "text/csv")},
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Valid data processed successfully")
        else:
            print(f"Response: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")


if __name__ == "__main__":
    test_missing_columns()
    test_invalid_price()
    test_valid_data()

