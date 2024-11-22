import requests

response = requests.post(
    "https://emc-san-mateo.com/api/validate_qrCODE",
    json={"qr_code": ""},
    timeout=10,
    # headers={'Content-type': 'application/json'}
)

print(f"Response status code: {response.status_code}")
print(f"Response text: {response.text}")