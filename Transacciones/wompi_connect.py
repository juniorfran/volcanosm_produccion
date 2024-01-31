# wompi_connection.py

import requests

def authenticate_wompi(client_id, client_secret):
    url = "https://id.wompi.sv/connect/token"
    payload = {
        "grant_type": "client_credentials",
        "audience": "wompi_api",
        "client_id": client_id,
        "client_secret": client_secret
    }
    headers = {"content-type": "application/x-www-form-urlencoded"}

    try:
        response = requests.post(url, data=payload, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        return response.json()["access_token"]
    except requests.exceptions.RequestException as e:
        print(f"Error during authentication: {e}")
        return None
