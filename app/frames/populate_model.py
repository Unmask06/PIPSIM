"""
frames/populate_model.py
Generate the populate_model frame for the application.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk
from typing import List, Literal

from sixgill.definitions import ModelComponents

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


def create_title_frame(parent) -> tk.Frame:
    frame = tk.Frame(parent)
    create_label = tk.Label(frame, text="Populate Model Workflow", font=("Arial", 14))
    create_label.pack()
    help_label = tk.Label(
        frame,
        text="This workflow populates an existing model with data from the Excel file.",
        font=("Arial", 10, "italic"),
    )
    help_label.pack()
    return frame


def create_pipesim_input_frame(parent) -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent)
    label = tk.Label(frame, text="Pipesim File")
    label.pack()
    entry = tk.Entry(frame, width=75)
    entry.pack(side=tk.LEFT)
    browse_button = tk.Button(
        frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            entry, file_types=[("Pipesim Files", "*.pips")]
        ),
    )
    browse_button.pack(padx=5, side=tk.LEFT)
    return frame, entry


def create_excel_input_frame(parent) -> tuple[tk.Frame, tk.Entry]:
    frame = tk.Frame(parent)
    label = tk.Label(frame, text="Excel File")
    label.pack()
    entry = tk.Entry(frame, width=75)
    entry.pack(side=tk.LEFT)
    browse_button = tk.Button(
        frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            entry, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
        ),
    )
    browse_button.pack(padx=5, side=tk.LEFT)
    return frame, entry


def create_mode_selection_frame(
    parent,
    modes: dict,
    variable: tk.StringVar,
) -> tk.Frame:
    frame = tk.Frame(parent)

    for i, (mode, explanation) in enumerate(modes.items()):
        radio_button = tk.Radiobutton(frame, text=mode, variable=variable, value=mode)
        radio_button.grid(row=i, column=0, sticky=tk.W)
        explanation_label = tk.Label(
            frame, text=explanation, font=("Arial", 9, "italic")
        )
        explanation_label.grid(row=i, column=1, sticky=tk.W, padx=10)

    return frame


def browse_and_update_optionmenu(
    entry_widget: tk.Entry, option_menu: tk.OptionMenu, variable: tk.StringVar
) -> None:
    file_path = browse_folder_or_file(
        entry_widget, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
    )
    update_optionmenu_with_excelsheets(option_menu, variable, file_path)


def create_submit_button_frame(parent, command) -> tk.Button:
    submit_button = tk.Button(parent, text="Submit", command=command)
    return submit_button


def get_sheet_name_widget(
    parent, sheet_name_var: tk.StringVar, sheet_names: List[str]
) -> tk.OptionMenu:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    sheet_name_var.set(sheet_names[0])
    sheet_name_dropdown = tk.OptionMenu(frame, sheet_name_var, *sheet_names)
    return sheet_name_dropdown


def create_scrollable_box_frame(parent: tk.Frame) -> tk.Listbox:
    scrollable_box = tk.Listbox(parent, height=10, width=50)
    scrollable_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=scrollable_box.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    scrollable_box.config(yscrollcommand=scrollbar.set)
    return scrollable_box


def create_dual_combo_box_button_frame(parent, command) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    button = tk.Button(frame, text="Open Dual Combo Box", command=command)
    button.pack()
    return frame


def submit_populate_model(
    pipesim_file_path: str,
    excel_file_path: str,
    sheet_name: str,
    mode: Literal["bulk_import", "export", "simple_import", "import_flowline_geometry"],
    progress_bar: ttk.Progressbar,
    references: dict,
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
        try:
            if mode == "export":
                lb = references.get("listbox", None)
                if not lb:
                    progress_bar.stop()
                    progress_bar.pack_forget()
                    messagebox.showerror(
                        "Error", "No component list found for Export mode."
                    )
                    return
                mp.export_values(
                    excel_file=excel_file_path, components=list(lb.get(0, tk.END))
                )
            elif mode == "simple_import":
                mp.simple_import_data(sheet_name)
            elif mode == "import_flowline_geometry":
                mp.import_flowline_geometry(sheet_name)
            elif mode == "bulk_import":
                mp.bulk_import_values(excel_file=excel_file_path)
        except (ExcelInputError, PipsimModellingError) as e:
            progress_bar.stop()
            progress_bar.pack_forget()
            messagebox.showerror("Error", str(e))
            return

        progress_bar.stop()
        progress_bar.pack_forget()
        messagebox.showinfo("Success", f"Model {mode}ed successfully")

    threading.Thread(target=task).start()


def open_dual_combo_box(scrollable_box: tk.Listbox) -> None:
    values = get_string_values_from_class(ModelComponents)
    selected_values = list(scrollable_box.get(0, tk.END))
    combobox = DualSelectableCombobox(
        scrollable_box,
        "Select Options",
        available_variables=values,
        selected_variables=selected_values,
    )
    scrollable_box.wait_window(combobox)
    selected_values = combobox.confirm_selection()
    scrollable_box.delete(0, tk.END)
    for val in selected_values:
        scrollable_box.insert(tk.END, val)


def create_export_mode_input(parent) -> tk.Listbox:
    scrollable_box = create_scrollable_box_frame(parent)
    create_dual_combo_box_button_frame(parent, lambda: open_dual_combo_box(scrollable_box))
    return scrollable_box


def create_simple_import_mode_input(parent, sheet_name_var: tk.StringVar) -> None:
    tk.Label(
        parent, text="Simple Import Mode: Select an Excel sheet to import data"
    ).pack()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_dropdown = get_sheet_name_widget(
        parent, sheet_name_var, ["Select Sheet Name"]
    )
    sheet_name_dropdown.pack()


def create_import_flowline_geometry_mode_input(parent, sheet_name_var: tk.StringVar) -> None:
    tk.Label(
        parent,
        text="Import Flowline Geometry Mode: Select an Excel sheet containing flowline geometry data",
    ).pack()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_dropdown = get_sheet_name_widget(
        parent, sheet_name_var, ["Select Sheet Name"]
    )
    sheet_name_dropdown.pack()


def create_bulk_import_mode_input(parent, sheet_name_var: tk.StringVar) -> None:
    tk.Label(
        parent, text="Bulk Import Mode: Import bulk data from the Excel file"
    ).pack()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_dropdown = get_sheet_name_widget(
        parent, sheet_name_var, ["Select Sheet Name"]
    )
    sheet_name_dropdown.pack()


def update_sub_frame(sub_frame, mode_var, references, sheet_name_var):
    for widget in sub_frame.winfo_children():
        widget.pack_forget()

    if mode_var.get() == "export":
        references["listbox"] = create_export_mode_input(sub_frame)
    elif mode_var.get() == "simple_import":
        create_simple_import_mode_input(sub_frame, sheet_name_var)
    elif mode_var.get() == "import_flowline_geometry":
        create_import_flowline_geometry_mode_input(sub_frame, sheet_name_var)
    elif mode_var.get() == "bulk_import":
        create_bulk_import_mode_input(sub_frame, sheet_name_var)


def init_populate_model_frame(app: tk.Tk) -> tk.Frame:
    populate_model_frame = tk.Frame(app)
    FRAME_STORE["populate_model"] = populate_model_frame

    MODES = {
        "export": "Export the entire data from the mode for the selected components",
        "bulk_import": "Bulk import data into the model from the Excel file created by the export mode",
        "simple_import": "Import data into the model from selected sheet in the Excel file",
        "import_flowline_geometry": "Import flowline geometry data into the model from the Excel file",
    }

    title_frame = create_title_frame(populate_model_frame)
    pips_frame, pips_entry = create_pipesim_input_frame(populate_model_frame)
    excel_frame, excel_entry = create_excel_input_frame(populate_model_frame)
    selected_mode_var = tk.StringVar()
    selected_mode_var.set("export")
    sub_frame = tk.Frame(populate_model_frame)

    mode_frame = create_mode_selection_frame(
        populate_model_frame, MODES, selected_mode_var
    )

    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")

    progress_bar = ttk.Progressbar(populate_model_frame, mode="indeterminate")

    # Dictionary to store references (like listbox) for different modes.
    references = {}

    submit_button = create_submit_button_frame(
        populate_model_frame,
        lambda: submit_populate_model(
            pips_entry.get(),
            excel_entry.get(),
            sheet_name_var.get(),
            selected_mode_var.get(),
            progress_bar,
            references,
        ),
    )

    title_frame.pack(pady=5)
    pips_frame.pack(pady=5)
    excel_frame.pack(pady=5)
    mode_frame.pack(pady=10)
    sub_frame.pack(pady=5)
    submit_button.pack(pady=5)

    selected_mode_var.trace_add(
        "write", lambda *args: update_sub_frame(sub_frame, selected_mode_var, references, sheet_name_var)
    )

    return populate_model_frame
