import logging
import tkinter as tk
from tkinter import messagebox

import pandas as pd

from core.excel_handling import ExcelHandler
from project import FRAME_STORE, browse_folder_or_file, update_optionmenu

logger = logging.getLogger("multi_case")


def create_title_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    create_label = tk.Label(frame, text="Multi-Case Workflow", font=("Arial", 14))
    create_label.pack()
    return frame


def create_help_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    help_text = """ This workflow handles multiple cases using an Excel file, sheet names for well profile data and different conditions, and a base pip file."""
    help_label = tk.Label(frame, text=help_text, font=("Arial", 10, "italic"))
    help_label.pack()
    return frame


def create_file_input_frame(parent, label_text: str, browse_command) -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    label = tk.Label(frame, text=label_text)
    label.pack()
    entry = tk.Entry(frame, width=75)
    entry.pack(side=tk.LEFT)
    browse_button = tk.Button(frame, text="Browse", command=browse_command)
    browse_button.pack(padx=5, side=tk.LEFT)
    return frame, entry


def create_option_menu_frame(parent, variable: tk.StringVar) -> tuple[tk.Frame, tk.OptionMenu]:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    option_menu = tk.OptionMenu(frame, variable, "Select Sheet Name")
    option_menu.pack()
    return frame, option_menu


def create_submit_button_frame(parent, command) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    submit_button = tk.Button(frame, text="Submit", command=command)
    submit_button.pack()
    return frame


def submit_multi_case_workflow(excel_file_path: str, well_profile_sheet: str, conditions_sheet: str, base_pip_file: str) -> None:
    logger.info("Handling multi-case workflow")
    # Implement the logic for handling the multi-case workflow here
    messagebox.showinfo("Success", "Multi-case workflow handled successfully")


def init_multi_case_frame(app: tk.Tk) -> tk.Frame:
    multi_case_frame = tk.Frame(app)
    FRAME_STORE["multi_case"] = multi_case_frame

    create_title_frame(multi_case_frame)

    create_help_frame(multi_case_frame)

    excel_frame, excel_file_entry = create_file_input_frame(
        multi_case_frame,
        "Excel File",
        lambda: browse_and_update_optionmenu(
            excel_file_entry, well_profile_sheet_dropdown, well_profile_sheet_var
        ),
    )

    well_profile_sheet_var = tk.StringVar()
    well_profile_sheet_var.set("Select Sheet Name")
    well_profile_sheet_frame, well_profile_sheet_dropdown = create_option_menu_frame(
        multi_case_frame, well_profile_sheet_var
    )

    conditions_sheet_var = tk.StringVar()
    conditions_sheet_var.set("Select Sheet Name")
    conditions_sheet_frame, conditions_sheet_dropdown = create_option_menu_frame(
        multi_case_frame, conditions_sheet_var
    )

    base_pip_frame, base_pip_file_entry = create_file_input_frame(
        multi_case_frame, "Base Pip File", lambda: browse_folder_or_file(base_pip_file_entry)
    )

    def on_submit() -> None:
        submit_multi_case_workflow(
            excel_file_entry.get(),
            well_profile_sheet_var.get(),
            conditions_sheet_var.get(),
            base_pip_file_entry.get(),
        )

    create_submit_button_frame(multi_case_frame, on_submit)

    return multi_case_frame
