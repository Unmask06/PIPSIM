import requests

VERSION = "1.0"
URL = "http://127.0.0.1:5000/pipesim/post"

# fetch response from http://127.0.0.1:5000/pipesim/post this POST request


def fetch_response(trail=False):
    """Fetches the response from the server or returns a mock response in trail mode."""
    if not trail:
        try:
            response = requests.post(
                URL,
                json={"version": VERSION},
                timeout=10,
            )
            return response
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "trail": trail,
            }
    else:
        # Mock response for trail mode
        return {"status": "OK", "message": "Access granted (trail mode)", "trail": True}
