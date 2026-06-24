import requests
from dotenv import load_dotenv
import os

# Create your tests here.

for i in range(10):
    response = requests.post(
        "http://127.0.0.1:8000/api/event/",
        headers={
            "X-MY-SECRET-KEY": "01b23da6-a194-4e14-81ca-6ca9b42d1202"

        },
        json={
            "organization": 4,
            "event_type": "test_looping",
            "event_data": {
                "page": "test Bulk Data"
            }
        }
    )

print("STATUS:", response.status_code)
print("TEXT:", response.text)
