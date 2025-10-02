import pytest
import pandas as pd
from fastapi.testclient import TestClient
import sys
import os
import json
import requests

# Set up paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API_DIR = os.path.join(BASE_DIR, "api")
DATA_DIR = os.path.join(BASE_DIR, "data")

if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)

# Import the FastAPI app
from main import app

# Create test client
client = TestClient(app)


def test_health_endpoint():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "Stock Market Daily Winners API"
    assert data["version"] == "1.0.0"


def load_expected_json(file_name: str) -> dict:
    """Helper function to load expected JSON output"""
    json_path = os.path.join(DATA_DIR, file_name)
    with open(json_path, "r") as f:
        return json.load(f)


def test_invalid_file_type():
    """Test that non-CSV files are rejected"""
    response = client.post(
        "/get_daily_winners_from_file",
        files={"file": ("test.txt", b"some random content", "text/plain")},
    )

    assert response.status_code == 400
    assert "File must be a CSV" in response.json()["detail"]


def test_all_data_files_parametrized():
    """Parametrized test to check all CSV files against their expected JSON outputs"""
    test_cases = [
        ("data1.csv", "winners_data1.json"),
        ("data2.csv", "winners_data2.json"),
        ("data3.csv", "winners_data3.json"),
        ("data4.csv", "winners_data4.json"),
    ]

    for csv_file, json_file in test_cases:
        csv_path = os.path.join(DATA_DIR, csv_file)
        expected_output = load_expected_json(json_file)

        with open(csv_path, "rb") as f:
            response = client.post(
                "/get_daily_winners_from_file",
                files={"file": (csv_file, f, "text/csv")},
            )

        assert response.status_code == 200, f"Failed for {csv_file}"
        actual_output = response.json()

        assert (
            actual_output == expected_output
        ), f"Output mismatch for {csv_file}:\nExpected: {expected_output}\nActual: {actual_output}"


def test_deployed_api_online():
    """Test the deployed online API on Vercel"""
    api_url = "https://stockmarket-demo.vercel.app/"

    # Test health endpoint
    health_response = requests.get(api_url + "health", timeout=10)
    assert (
        health_response.status_code == 200
    ), f"Health check failed: {health_response.status_code}"

    health_data = health_response.json()
    assert health_data["status"] == "healthy"
    assert "timestamp" in health_data

    # Test get_daily_winners endpoint (uses data1.csv on the server)
    winners_response = requests.get(api_url + "get_daily_winners", timeout=10)
    assert (
        winners_response.status_code == 200
    ), f"Get winners failed: {winners_response.status_code}"

    # Compare with expected data1 output
    expected_output = load_expected_json("winners_data1.json")
    actual_output = winners_response.json()

    assert (
        actual_output == expected_output
    ), f"Deployed API output mismatch:\nExpected: {expected_output}\nActual: {actual_output}"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
