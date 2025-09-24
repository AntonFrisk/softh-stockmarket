"""
Test script for the API endpoints
"""

import requests
import json


def test_local_file_endpoint():
    """Test the local file endpoint"""
    try:
        response = requests.get("http://localhost:8000/get_daily_winners/")
        print("🏠 Local file endpoint test:")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:\n", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("API server is not running. Please start it first.")


def test_file_upload_endpoint():
    """Test the file upload endpoint"""
    try:
        file_name = "data2.csv"
        file_path = f"data/{file_name}"
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                "http://localhost:8000/get_daily_winners_from_file", files=files
            )

        print(f"🆙 File upload endpoint test, using file: {file_path}")
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Response:\n", json.dumps(response.json(), indent=2))
        else:
            print("Error:", response.text)
        print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("API server is not running. Please start it first.")
    except FileNotFoundError:
        print("data1.csv file not found")


if __name__ == "__main__":
    print("Testing API endpoints...")
    test_local_file_endpoint()
    test_file_upload_endpoint()
