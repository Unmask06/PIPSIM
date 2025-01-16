"""
frames/create_model.py
Generate the create_model frame for the application.
"""

import logging
import tkinter as tk
from tkinter import messagebox

import pandas as pd
from sixgill.definitions import ModelComponents, Parameters

from core.excel_handling import ExcelHandler
from core.model_builder import ModelBuilder, create_component_name_df
from project import (
    FRAME_STORE,
    browse_folder_or_file,
    generate_dict_from_class,
    get_string_values_from_class,
)
from widgets import DualCascadeListBox, DualSelectableCombobox

logger = logging.getLogger("core.model_builder")


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


def create_radio_buttons_frame(
    parent, options: dict, variable: tk.StringVar, app: tk.Tk
) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=5)

    for option, description in options.items():

        if option == "Scratch":
            scratch_frame = tk.Frame(frame)
            scratch_frame.pack(pady=10)
            radio_button = tk.Radiobutton(
                scratch_frame, text=description, variable=variable, value=option
            )
            radio_button.grid(row=0, column=0, padx=5, pady=5)

            btn_open_component_list = tk.Button(
                scratch_frame,
                text="Refer the list of available components",
                command=lambda: open_component_list(app),
            )
            btn_open_component_list.grid(row=0, column=1, padx=5, pady=5)

        elif option == "Populate":
            populate_frame = tk.Frame(frame)
            populate_frame.pack(pady=10)
            radio_button = tk.Radiobutton(
                populate_frame, text=description, variable=variable, value=option
            )
            radio_button.grid(row=1, column=0, padx=5, pady=5)

            btn_open_flowline_parameters = tk.Button(
                populate_frame,
                text="Create Excel with flowline parameters",
                command=lambda: open_flowline_parameters(app),
            )
            btn_open_flowline_parameters.grid(row=1, column=1, padx=5, pady=5)
    return frame


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
    pipesim_file_path: str, excel_file_path: str, sheet_name: str
) -> None:
    logger.info("Creating model from scratch")
    component_name = create_component_name_df(excel_file_path, sheet_name)
    mb = ModelBuilder(
        pipsim_file_path=pipesim_file_path,
        component_name=component_name,
        mode="Scratch",
    )
    mb.main()
    messagebox.showinfo("Success", "Model created successfully")


def submit_populate_model(
    pipesim_file_path: str, excel_file_path: str, sheet_name: str
) -> None:
    component_name = create_component_name_df(excel_file_path, sheet_name)
    mb = ModelBuilder(
        pipsim_file_path=pipesim_file_path,
        component_name=component_name,
        mode="Populate",
    )
    mb.main()
    logger.info("Model Information populated successfully")
    messagebox.showinfo("Success", "Model Information populated successfully")


def get_sheet_names(file_path: str) -> list[str]:
    try:
        return pd.ExcelFile(file_path).sheet_names
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file: {e}")
        return []


def update_optionmenu(
    option_menu: tk.OptionMenu, variable: tk.StringVar, excel_file_path: str
) -> None:
    sheets = get_sheet_names(excel_file_path)
    menu = option_menu["menu"]
    menu.delete(0, "end")
    for sheet in sheets:
        menu.add_command(label=sheet, command=lambda v=sheet: variable.set(v))
    variable.set(sheets[0] if sheets else "No sheets available")


def browse_and_update_optionmenu(
    entry_widget: tk.Entry, option_menu: tk.OptionMenu, variable: tk.StringVar
) -> None:
    file_path = browse_folder_or_file(
        entry_widget, file_types=[("Excel Files", "*.xlsx *.xls")]
    )
    update_optionmenu(option_menu, variable, file_path)


def open_component_list(parent: tk.Tk) -> None:
    # combobox = DualSelectableCombobox(
    #     parent,
    #     title="Refer the list of available components",
    #     values=get_string_values_from_class(ModelComponents),
    #     mode="single",
    # )
    # parent.wait_window(combobox)

    cascade_box = DualCascadeListBox(
        parent,
        title="Refer the list of available parameters",
        child_mapping=generate_dict_from_class(Parameters),
    )
    parent.wait_window(cascade_box)


def open_flowline_parameters(parent: tk.Tk) -> None:
    combobox = DualSelectableCombobox(
        parent,
        title="Refer the list of available flowline parameters",
        values=get_string_values_from_class(
            [Parameters.Flowline, Parameters.FlowlineGeometry]
        ),
        mode="dual",
    )
    parent.wait_window(combobox)
    if combobox.confirm_selection():
        create_excel_with_selected_parameters(
            "Pandora Pilot Params.xlsx", combobox.confirm_selection()
        )
        messagebox.showinfo("Success", "Excel file created with selected parameters")


def create_excel_with_selected_parameters(
    file_path: str, selected_parameters: list[str]
) -> None:
    columns = ["Name", "Component"] + selected_parameters
    df = pd.DataFrame(columns=columns)
    ExcelHandler.write_excel(df, file_path, "Selected Parameters")
    logger.info("Excel file created with selected parameters")


############################################
# MAIN FUNCTION
############################################


def init_create_model_frame(app: tk.Tk) -> tk.Frame:
    create_model_frame = tk.Frame(app)
    FRAME_STORE["create_model"] = create_model_frame

    create_title_frame(create_model_frame)

    create_help_frame(create_model_frame)

    pipesim_frame, ps_file_entry = create_file_input_frame(
        create_model_frame, "Pipesim File", lambda: browse_folder_or_file(ps_file_entry)
    )
    excel_frame, excel_file_entry = create_file_input_frame(
        create_model_frame,
        "Excel File",
        lambda: browse_and_update_optionmenu(
            excel_file_entry, sheet_name_dropdown, sheet_name_var
        ),
    )

    sheet_name_var = tk.StringVar()
    sheet_name_var.set("Select Sheet Name")
    sheet_name_frame, sheet_name_dropdown = create_option_menu_frame(
        create_model_frame, sheet_name_var
    )

    model_options = {
        "Scratch": "Create a model from scratch using the Excel file",
        "Populate": "Populate an existing model with data from the Excel file",
    }
    model_option_var = tk.StringVar()
    model_option_var.set("Scratch")
    create_radio_buttons_frame(create_model_frame, model_options, model_option_var, app)

    def on_submit() -> None:
        if model_option_var.get() == "Scratch":
            submit_create_model(
                ps_file_entry.get(), excel_file_entry.get(), sheet_name_var.get()
            )
        else:
            submit_populate_model(
                ps_file_entry.get(), excel_file_entry.get(), sheet_name_var.get()
            )

    create_submit_button_frame(create_model_frame, on_submit)

    return create_model_frame
