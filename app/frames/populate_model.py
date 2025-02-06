"""
frames/populate_model.py
Generate the populate_model frame for the application.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Literal

from app.core import ExcelInputError, PipsimModellingError
from app.core.excel_handling import ExcelHandler
from app.core.model_populater import ModelPopulater
from app.project import (
    FRAME_STORE,
    browse_folder_or_file,
    generate_dict_from_class,
    get_string_values_from_class,
    update_optionmenu_with_excelsheets,
)
from app.widgets import DualCascadeListBox, DualSelectableCombobox

logger = logging.getLogger("app.core.model_populater")


############################################
# LAYOUT FUNCTIONS
############################################


def create_title_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    create_label = tk.Label(frame, text="Populate Model Workflow", font=("Arial", 14))
    create_label.pack()
    return frame


def create_help_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    help_text = (
        """ This workflow populates an existing model with data from the Excel file."""
    )
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


def create_mode_selection_frame(
    parent, variable: tk.StringVar, sheet_name_frame: tk.Frame, sub_frame: tk.Frame
) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)

    modes = {
        "export": "Export the entire data from the mode for the selected components",
        "bulk_import": "Bulk import data into the model from the Excel file created by the export mode",
        "simple_import": "Import data into the model from selected sheet in the Excel file",
        "import_flowline_geometry": "Import flowline geometry data into the model from the Excel file",
    }

    def on_mode_change(*args):
        if variable.get() in ["simple_import", "import_flowline_geometry"]:
            sheet_name_frame.pack(pady=5)
        else:
            sheet_name_frame.pack_forget()

        for widget in sub_frame.winfo_children():
            widget.pack_forget()

        if variable.get() == "export":
            create_export_mode_input(sub_frame)
        elif variable.get() == "simple_import":
            create_simple_import_mode_input(sub_frame)
        elif variable.get() == "import_flowline_geometry":
            create_import_flowline_geometry_mode_input(sub_frame)

    variable.trace_add("write", on_mode_change)

    for i, (mode, explanation) in enumerate(modes.items()):
        radio_button = tk.Radiobutton(frame, text=mode, variable=variable, value=mode)
        radio_button.grid(row=i, column=0, sticky=tk.W)
        explanation_label = tk.Label(
            frame, text=explanation, font=("Arial", 9, "italic")
        )
        explanation_label.grid(row=i, column=1, sticky=tk.W, padx=10)

    return frame


def create_submit_button_frame(parent, command) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    submit_button = tk.Button(frame, text="Submit", command=command)
    submit_button.pack()
    return frame


def create_scrollable_box_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    scrollable_box = tk.Listbox(frame, height=10, width=50)
    scrollable_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(frame, orient="vertical", command=scrollable_box.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollable_box.config(yscrollcommand=scrollbar.set)
    return frame, scrollable_box


def create_dual_combo_box_button_frame(parent, command) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    button = tk.Button(frame, text="Open Dual Combo Box", command=command)
    button.pack()
    return frame


############################################
# CALLBACK FUNCTIONS
############################################


def submit_populate_model(
    pipesim_file_path: str,
    excel_file_path: str,
    sheet_name: str,
    mode: Literal["bulk_import", "export", "simple_import", "import_flowline_geometry"],
    progress_bar: ttk.Progressbar,
) -> None:
    if (
        mode in ["simple_import", "import_flowline_geometry"]
        and sheet_name == "Select Sheet Name"
    ):
        messagebox.showerror("Error", "Please select a valid sheet name.")
        return

    def task():
        progress_bar.pack(pady=10)
        logger.info(f"Running {mode} mode with data from Excel")
        progress_bar.start()

        mp = ModelPopulater(
            pipesim_file=pipesim_file_path, excel_file=excel_file_path, mode=mode
        )
        mp.populate_model(sheet_name=sheet_name)

        progress_bar.stop()
        progress_bar.pack_forget()
        messagebox.showinfo("Success", f"Model {mode}ed successfully")

    threading.Thread(target=task).start()


def browse_and_update_optionmenu(
    entry_widget: tk.Entry, option_menu: tk.OptionMenu, variable: tk.StringVar
) -> None:
    file_path = browse_folder_or_file(
        entry_widget, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
    )
    update_optionmenu_with_excelsheets(option_menu, variable, file_path)


def open_dual_combo_box(scrollable_box):
    values = ["Option 1", "Option 2", "Option 3", "Option 4"]
    combobox = DualSelectableCombobox(scrollable_box, "Select Options", values)
    scrollable_box.wait_window(combobox)
    selected_values = combobox.confirm_selection()
    scrollable_box.delete(0, tk.END)
    for val in selected_values:
        scrollable_box.insert(tk.END, val)


############################################
# MODE INPUT FUNCTIONS
############################################


def create_export_mode_input(parent) -> None:
    scrollable_box_frame, scrollable_box = create_scrollable_box_frame(parent)
    create_dual_combo_box_button_frame(
        parent, lambda: open_dual_combo_box(scrollable_box)
    )


def create_simple_import_mode_input(parent) -> None:
    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_frame, sheet_name_dropdown = create_option_menu_frame(parent, sheet_name_var)
    sheet_name_frame.pack(pady=5)


def create_import_flowline_geometry_mode_input(parent) -> None:
    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_frame, sheet_name_dropdown = create_option_menu_frame(parent, sheet_name_var)
    sheet_name_frame.pack(pady=5)


############################################
# MAIN FUNCTION
############################################


def init_populate_model_frame(app: tk.Tk) -> tk.Frame:
    populate_model_frame = tk.Frame(app)
    FRAME_STORE["populate_model"] = populate_model_frame

    create_title_frame(populate_model_frame)

    create_help_frame(populate_model_frame)

    pipesim_frame, ps_file_entry = create_file_input_frame(
        populate_model_frame,
        "Pipesim File",
        lambda: browse_folder_or_file(
            ps_file_entry, file_types=[("Pipesim Files", "*.pips")]
        ),
    )
    excel_frame, excel_file_entry = create_file_input_frame(
        populate_model_frame,
        "Excel File",
        lambda: browse_and_update_optionmenu(
            excel_file_entry, sheet_name_dropdown, sheet_name_var
        ),
    )

    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_frame, sheet_name_dropdown = create_option_menu_frame(
        populate_model_frame, sheet_name_var
    )

    sub_frame = tk.Frame(populate_model_frame)
    sub_frame.pack(pady=5)

    mode_var = tk.StringVar(value="export")
    create_mode_selection_frame(populate_model_frame, mode_var, sheet_name_frame, sub_frame)

    progress_bar = ttk.Progressbar(populate_model_frame, mode="indeterminate")

    def on_submit() -> None:
        submit_populate_model(
            ps_file_entry.get(),
            excel_file_entry.get(),
            sheet_name_var.get(),
            mode_var.get(),
            progress_bar,
        )

    create_submit_button_frame(populate_model_frame, on_submit)

    return populate_model_frame
