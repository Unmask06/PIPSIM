from datetime import datetime, timedelta

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
                # verify=False,
            )
            return response
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "trail": trail,
            }
    # Define the start date for the trail period
    trail_start_date = datetime(2025, 2, 3).date()  # Example start date
    trail_end_date = trail_start_date + timedelta(days=7)

    if trail:
        current_date = datetime.now().date()
        if (current_date >= trail_start_date) and (current_date <= trail_end_date):
            return {
                "status": "OK",
                "message": "Access granted (trail mode)",
                "trail": True,
            }
        else:
            return {
                "status": "error",
                "message": "Trail period has ended",
                "trail": True,
            }
