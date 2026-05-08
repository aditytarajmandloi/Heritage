import requests
import json

url = "http://localhost:8000/api/query"

queries = [
    "Tell me about Vidhana Soudha",
    "Show me Tudor style architecture",
    "What can I see near Cubbon Park?"
]

for q in queries:
    print(f"\n--- Testing Query: '{q}' ---")
    response = requests.post(url, json={"question": q})
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Answer:", data.get("answer"))
        print("Media:", data.get("media"))
        print("Graph Data:", data.get("graph_data"))
    else:
        print("Error:", response.text)
