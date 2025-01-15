"""
frames/create_model.py
Generate the create_model frame for the application.
"""

import logging
import tkinter as tk
from tkinter import messagebox

import pandas as pd
from sixgill.definitions import ModelComponents, Parameters

from core.model_builder import ModelBuilder, create_component_name_df
from project import FRAME_STORE, browse_folder_or_file, get_string_values_from_class
from widgets.dual_combo_box import DualSelectableCombobox

logger_cm = logging.getLogger("core.model_builder")


def submit_create_model(
    pipesim_file_path: str,
    excel_file_path: str,
    sheet_name: str,
):
    logger_cm.info("Creating model from scratch")
    component_name = create_component_name_df(
        excel_file_path,
        sheet_name,
    )
    mb = ModelBuilder(
        pipsim_file_path=pipesim_file_path,
        component_name=component_name,
        mode="Scratch",
    )
    mb.main()
    messagebox.showinfo("Success", "Model created successfully")


def submit_populate_model(
    pipesim_file_path: str,
    excel_file_path: str,
    sheet_name: str,
):
    component_name = create_component_name_df(
        excel_file_path,
        sheet_name,
    )
    mb = ModelBuilder(
        pipsim_file_path=pipesim_file_path,
        component_name=component_name,
        mode="Populate",
    )
    mb.main()
    logger_cm.info("Model Information populated successfully")
    messagebox.showinfo("Success", "Model Information populated successfully")


def get_sheet_names(file_path):
    try:
        sheet_names = pd.ExcelFile(file_path).sheet_names
        return sheet_names
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file: {e}")
        return []


def update_optionmenu(option_menu, variable, excel_file_path):
    sheets = get_sheet_names(excel_file_path)
    menu = option_menu["menu"]
    menu.delete(0, "end")
    for sheet in sheets:
        menu.add_command(label=sheet, command=lambda v=sheet: variable.set(v))
    variable.set(sheets[0] if sheets else "No sheets available")


def browse_and_update_optionmenu(entry_widget, option_menu, variable):

    file_path = browse_folder_or_file(
        entry_widget, file_types=[("Excel Files", "*.xlsx *.xls")]
    )
    update_optionmenu(option_menu, variable, file_path)


def open_component_list(parent):
    combobox = DualSelectableCombobox(
        parent,
        title="Refer the list of available components",
        values=get_string_values_from_class(ModelComponents),
        mode="single",
    )
    parent.wait_window(combobox)


def open_flowline_parameters(parent):
    combobox = DualSelectableCombobox(
        parent,
        title="Refer the list of available flowline parameters",
        values=get_string_values_from_class(
            [Parameters.Flowline, Parameters.FlowlineGeometry]
        ),
        mode="single",
    )
    parent.wait_window(combobox)


def init_create_model_frame(app: tk.Tk) -> tk.Frame:  # pylint: disable=R0914
    create_model_frame = tk.Frame(app)
    FRAME_STORE["create_model"] = create_model_frame

    # Title
    create_label = tk.Label(
        create_model_frame, text="Create Model Workflow", font=("Arial", 14)
    )
    create_label.pack(pady=10)

    # Button to open single select combo box
    btn_open_component_list = tk.Button(
        create_model_frame,
        text="Refer the list of available components",
        command=lambda: open_component_list(app),
    )
    btn_open_component_list.pack(pady=5, anchor="ne")

    # Button to open dual select combo box
    btn_open_flowline_parameters = tk.Button(
        create_model_frame,
        text="Refer the list of available flowline parameters",
        command=lambda: open_flowline_parameters(app),
    )
    btn_open_flowline_parameters.pack(pady=5, anchor="ne")

    help_text = """ This workflow creates a model from scratch using the Excel file or
    populates an existing model with data from the Excel file."""
    help_label_cm = tk.Label(
        create_model_frame,
        text=help_text,
        font=("Arial", 10, "italic"),
    )
    help_label_cm.pack(pady=5)

    # Pipesim File Frame
    pipesim_input_container = tk.Frame(create_model_frame)
    pipesim_input_container.pack()
    ps_file_label = tk.Label(pipesim_input_container, text="Pipesim File")
    ps_file_label.pack()
    ps_file_entry = tk.Entry(pipesim_input_container, width=75)
    ps_file_entry.pack(side=tk.LEFT)
    ps_browse_button = tk.Button(
        pipesim_input_container,
        text="Browse",
        command=lambda: browse_folder_or_file(ps_file_entry),
    )
    ps_browse_button.pack(padx=5, side=tk.LEFT)

    # Excel File Frame
    excel_input_container = tk.Frame(create_model_frame)
    excel_input_container.pack()
    excel_file_label = tk.Label(excel_input_container, text="Excel File")
    excel_file_label.pack()
    excel_file_entry = tk.Entry(excel_input_container, width=75)
    excel_file_entry.pack(side=tk.LEFT)

    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")

    # OptionMenu for sheet names
    sheet_name_dropdown = tk.OptionMenu(
        create_model_frame, sheet_name_var, "Select Sheet Name"
    )
    sheet_name_dropdown.pack(pady=5)

    excel_browse_button = tk.Button(
        excel_input_container,
        text="Browse",
        command=lambda: browse_and_update_optionmenu(
            excel_file_entry, sheet_name_dropdown, sheet_name_var
        ),
    )
    excel_browse_button.pack(padx=5, side=tk.LEFT)

    # Radio Button Options
    model_options = {
        "Scratch": "Create a model from scratch using the Excel file",
        "Populate": "Populate an existing model with data from the Excel file",
    }
    model_option_var = tk.StringVar()
    model_option_var.set("Scratch")

    for option, description in model_options.items():
        option_radio = tk.Radiobutton(
            create_model_frame,
            text=description,
            variable=model_option_var,
            value=option,
        )
        option_radio.pack()

    # Submit button
    def on_submit():
        if model_option_var.get() == "Scratch":
            submit_create_model(
                ps_file_entry.get(),
                excel_file_entry.get(),
                sheet_name_var.get(),
            )
        else:
            submit_populate_model(
                ps_file_entry.get(),
                excel_file_entry.get(),
                sheet_name_var.get(),
            )

    submit_button = tk.Button(
        create_model_frame,
        text="Submit",
        command=on_submit,
    )
    submit_button.pack(pady=10)

    return create_model_frame
