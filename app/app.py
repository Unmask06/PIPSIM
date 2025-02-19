"""
Main application file for the PANDORA Pipesim Pilot.
"""

import logging
import logging.config
import os
import sys
import tkinter as tk
from pathlib import Path

# import traceback
from tkinter import messagebox

import yaml

from app.config import fetch_response
from app.frames import (
    CreateModelFrame,
    HomeFrame,
    MultiCaseFrame,
    PopulateModelFrame,
    RunSimulationFrame,
    init_summarize_frame,
    init_update_conditions_frame,
)
from app.project import (
    FRAME_STORE,
    download_sample_excel,
    open_component_param_box,
    open_documentation,
    switch_frame,
)

logger = logging.getLogger(__name__)


def load_logging_config():
    """Load the logging configuration from the YAML file."""
    try:
        base_dir = Path(__file__).resolve().parent
        log_file = base_dir / "logging.yml"
        with open(log_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except ValueError as e:
        logger.warning(
            f"Failed to load logging configuration: {e} --- Using basic config."
        )
        logging.basicConfig(level=logging.DEBUG)  # Fallback to basic config


def show_menu(app: tk.Tk):
    menu_bar = tk.Menu(app)

    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(
        label="Home", command=lambda: switch_frame(FRAME_STORE["home"])
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: sys.exit(0))
    menu_bar.add_cascade(label="File", menu=file_menu)
    app.config(menu=menu_bar)

    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(
        label="Component Parameters", command=lambda: open_component_param_box(app)
    )
    help_menu.add_command(label="Documentation", command=lambda: open_documentation())
    help_menu.add_separator()
    help_menu.add_command(
        label="Sample Import File",
        command=lambda: download_sample_excel(),
    )
    menu_bar.add_cascade(label="Help", menu=help_menu)
    app.config(menu=menu_bar)


def check_access(app: tk.Tk, trail=True):  #! trail=False in production
    """Check access and display the appropriate frame with flexibility for trail mode."""
    response = fetch_response(trail)

    if isinstance(response, dict):
        # Mock or error response already in dictionary format
        status = response.get("status")
    else:
        # Convert actual `Response` object to dictionary
        try:
            response_json = response.json()
            status = response_json.get("status")
        except ValueError:
            status = "error"

    if status == "OK":
        # Access granted
        switch_frame(FRAME_STORE["home"])
    elif status == "error":
        # Connection error occurred
        messagebox.showerror(
            "Connection Error",
            f"Failed to connect to the server: {response.get('message', 'Unknown error')}",
        )
        access_denied(app)
        switch_frame(FRAME_STORE["access_denied"])
    else:
        # Access denied
        messagebox.showwarning(
            "Access Denied",
            "You do not have permission to access this feature.",
        )
        access_denied(app)
        switch_frame(FRAME_STORE["access_denied"])


def access_denied(app: tk.Tk):
    """Create and display the access denied frame."""
    access_frame = tk.Frame(app)
    FRAME_STORE["access_denied"] = access_frame
    access_label = tk.Label(access_frame, text="Access Denied", font=("Arial", 14))
    access_label.pack(pady=10)
    reason_label = tk.Label(
        access_frame,
        text="You are using outdated software. Please contact the administrator.",
    )
    reason_label.pack(pady=5)
    exit_button = tk.Button(access_frame, text="Exit", command=app.destroy)
    exit_button.pack(pady=5)


def create_app_data() -> Path:
    """Create the application data directory if it doesn't exist."""

    appdata_dir = os.getenv("APPDATA")
    if appdata_dir is None:
        logger.error("APPDATA environment variable is not set.")
        return Path(".")

    appdata = Path(appdata_dir) / "Pandora" / "Pipesim Pilot"
    appdata.mkdir(parents=True, exist_ok=True)
    return appdata


def launch_application():

    load_logging_config()
    # Tkinter GUI setup
    app = tk.Tk()
    app.title("PANDORA - Pipesim Pilot")
    app.geometry("700x550")

    show_menu(app)

    # Initialize frames
    HomeFrame(app)
    CreateModelFrame(app)
    PopulateModelFrame(app)
    init_update_conditions_frame(app)
    RunSimulationFrame(app)
    init_summarize_frame(app)
    MultiCaseFrame(app)

    # Check access
    check_access(app)

    app.mainloop()


if __name__ == "__main__":
    launch_application()
