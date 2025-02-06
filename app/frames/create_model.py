"""
frames/create_model.py
Generate the create_model frame for the application.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from app.core import ExcelInputError, PipsimModellingError
from app.core.model_builder import ModelBuilder
from app.project import (
    FRAME_STORE,
    browse_folder_or_file,
    update_optionmenu_with_excelsheets,
)

logger = logging.getLogger("app.core.model_builder")


############################################
# LAYOUT FUNCTIONS
############################################


def create_title_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    create_label = tk.Label(frame, text="Create Model Workflow", font=("Arial", 14))
    create_label.pack()
    return frame


def create_help_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    help_text = """ This workflow creates a model from scratch using the Excel file or
    populates an existing model with data from the Excel file."""
    help_label = tk.Label(frame, text=help_text, font=("Arial", 10, "italic"))
    help_label.pack()
    return frame


def create_file_input_frame(
    parent, label_text: str, browse_command
) -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    label = tk.Label(frame, text=label_text)
    label.pack()
    entry = tk.Entry(frame, width=75)
    entry.pack(side=tk.LEFT)
    browse_button = tk.Button(frame, text="Browse", command=browse_command)
    browse_button.pack(padx=5, side=tk.LEFT)
    return frame, entry


def create_option_menu_frame(
    parent, variable: tk.StringVar
) -> tuple[tk.Frame, tk.OptionMenu]:
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


############################################
# CALLBACK FUNCTIONS
############################################


def submit_create_model(
    pipesim_file_path: str,
    excel_file_path: str,
    sheet_name: str,
    progress_bar: ttk.Progressbar,
) -> None:
    if sheet_name == "Select Sheet Name":
        messagebox.showerror("Error", "Please select a valid sheet name.")
        return

    def task():
        progress_bar.pack(pady=10)
        logger.info("Creating model from scratch")
        progress_bar.start()

        try:
            mb = ModelBuilder(
                pipsim_file_path=pipesim_file_path,
                excel_file_path=excel_file_path,
                sheet_name=sheet_name,
            )
            mb.create_model()

        except (ExcelInputError, PipsimModellingError) as e:
            progress_bar.stop()
            progress_bar.pack_forget()
            messagebox.showerror("Error", str(e))
            return

        progress_bar.stop()
        progress_bar.pack_forget()
        messagebox.showinfo("Success", "Model created successfully")

    threading.Thread(target=task).start()


def browse_and_update_optionmenu(
    entry_widget: tk.Entry, option_menu: tk.OptionMenu, variable: tk.StringVar
) -> None:
    file_path = browse_folder_or_file(
        entry_widget, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
    )
    update_optionmenu_with_excelsheets(option_menu, variable, file_path)


############################################
# MAIN FUNCTION
############################################


def init_create_model_frame(app: tk.Tk) -> tk.Frame:
    create_model_frame = tk.Frame(app)
    FRAME_STORE["create_model"] = create_model_frame

    create_title_frame(create_model_frame)

    create_help_frame(create_model_frame)

    _, ps_file_entry = create_file_input_frame(
        create_model_frame,
        "Pipesim File",
        lambda: browse_folder_or_file(
            ps_file_entry, file_types=[("Pipesim Files", "*.pips")]
        ),
    )
    _, excel_file_entry = create_file_input_frame(
        create_model_frame,
        "Excel File",
        lambda: browse_and_update_optionmenu(
            excel_file_entry, sheet_name_dropdown, sheet_name_var
        ),
    )

    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")
    _, sheet_name_dropdown = create_option_menu_frame(
        create_model_frame, sheet_name_var
    )

    progress_bar = ttk.Progressbar(create_model_frame, mode="indeterminate")

    def on_submit() -> None:
        submit_create_model(
            ps_file_entry.get(),
            excel_file_entry.get(),
            sheet_name_var.get(),
            progress_bar,
        )

    create_submit_button_frame(create_model_frame, on_submit)

    return create_model_frame
