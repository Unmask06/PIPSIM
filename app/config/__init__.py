import requests

VERSION = "1.0.2"
BASE_URL = "https://sv03919.res1.rlaone.net"
URL = f"{BASE_URL}/streamline/pipesim-pilot/getAccess"


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
