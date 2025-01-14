import logging
import logging.config
import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

import yaml

from frames import (
    init_create_model_frame,
    init_home_frame,
    init_run_simulation_frame,
    init_summarize_frame,
    init_update_conditions_frame,
)
from project import FRAME_STORE, switch_frame
from project.documentation import show_md_from_file


def load_logging_config():
    """Load the logging configuration from the YAML file."""
    try:
        with open("logging.yml", "r") as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)
    except Exception as e:
        print(f"Failed to load logging configuration: {e}", file=sys.stderr)
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
    help_menu.add_command(label="Help", command=lambda: show_md_from_file("help.md"))
    menu_bar.add_cascade(label="Help", menu=help_menu)
    app.config(menu=menu_bar)


def main():

    load_logging_config()
    # Tkinter GUI setup
    app = tk.Tk()
    app.title("PANDORA - Pipesim Pilot")
    app.geometry("600x400")

    show_menu(app)

    # Initialize frames
    home_frame = init_home_frame(app)
    init_create_model_frame(app)
    init_update_conditions_frame(app)
    init_run_simulation_frame(app)
    init_summarize_frame(app)

    # Start with the home frame
    switch_frame(home_frame)

    app.mainloop()


if __name__ == "__main__":
    main()
