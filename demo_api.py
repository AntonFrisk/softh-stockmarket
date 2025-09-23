import requests

with open("data1.csv", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/get_daily_winners", files=files)
    print(response.json())
