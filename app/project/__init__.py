import inspect
import logging
import logging.config
import os
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox
from typing import Dict, List

import pandas as pd
import yaml
from sixgill.definitions import Parameters

from app.config import BASE_URL
from app.frames import FRAME_STORE
from app.widgets import DualCascadeListBox


def switch_frame(new_frame: tk.Frame):
    for frame in FRAME_STORE.values():
        frame.pack_forget()
    new_frame.pack(fill="both", expand=True)


def browse_folder_or_file(
    entry_widget: tk.Entry,
    file_types: list[tuple[str, str]] | None = None,
    title: str = "Select a file or folder",
    select_folder: bool = False,
) -> str:
    """
    Opens a file or folder selection dialog and updates the provided entry widget with the selected path.
    Wrapper function for the filedialog.askopenfilename and filedialog.askdirectory functions.

    Returns:
        str: The selected file or folder path.
    """

    path = (
        filedialog.askdirectory(title=title)
        if select_folder
        else filedialog.askopenfilename(
            filetypes=file_types or [("All Files", "*.*")], title=title
        )
    )
    if path:
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)
        entry_widget.config(state="readonly")

        # Remove existing open button if it exists
        for widget in entry_widget.master.winfo_children():
            if isinstance(widget, tk.Button) and widget.cget("text") == "Open":
                widget.destroy()

        open_button = tk.Button(
            entry_widget.master, text="Open", command=lambda: os.startfile(path)
        )
        open_button.pack(side="left", padx=5, pady=5)

    return path


def setup_logger():
    with open("logging.yml", "r") as f:
        config = yaml.safe_load(f.read())
    config["handlers"] = {"console": config["handlers"]["console"]}
    logging.config.dictConfig(config)


def get_string_values_from_class(class_names: type | list[type]) -> list:
    def extract_string_values(class_name):
        return sorted(
            [
                value
                for key, value in class_name.__dict__.items()
                if not key.startswith("__") and isinstance(value, str)
            ]
        )

    combined_values = set()

    def get_inherited_classes(class_name):
        for _class in inspect.getmro(class_name):
            if _class.__name__ == "object":
                break
            combined_values.update(extract_string_values(_class))
        return combined_values

    if isinstance(class_names, list):
        for class_name in class_names:
            get_inherited_classes(class_name)
    else:
        get_inherited_classes(class_names)

    return sorted(combined_values)


def get_class_by_name(abstract_class: type, class_name: str) -> type:
    """
    Dynamically retrieves a class from the Parameters module by its name.
    """
    try:
        # Dynamically get the class from Parameters
        class_object = getattr(abstract_class, class_name)
        return class_object
    except AttributeError:
        raise ValueError(f"Class '{class_name}' not found in Parameters.")


def generate_dict_from_class(class_name: type) -> Dict[str, List[str]]:
    """
    Generates a dictionary from a class with string attributes.
    """

    def is_valid_component(component):
        return not component.startswith("__")

    components = sorted(filter(is_valid_component, class_name.__dict__.keys()))
    return {
        component: get_string_values_from_class(
            get_class_by_name(class_name, component)
        )
        for component in components
    }


def update_optionmenu_with_excelsheets(
    option_menu: tk.OptionMenu, variable: tk.StringVar, excel_file_path: str
) -> None:
    """
    Updates the given Tkinter OptionMenu with the sheet names from the specified Excel file.

    Args:
        option_menu (tk.OptionMenu): The OptionMenu widget to update.
        variable (tk.StringVar): The Tkinter StringVar associated with the OptionMenu.
        excel_file_path (str): The file path to the Excel file.

    Returns:
        None

    Raises:
        None. Displays an error message using messagebox.showerror if the Excel file cannot be read.
    """
    try:
        sheets = pd.ExcelFile(excel_file_path).sheet_names
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file: {e}")
        return

    menu = option_menu["menu"]
    menu.delete(0, "end")
    for sheet in sheets:
        menu.add_command(label=sheet, command=lambda v=sheet: variable.set(v))
    variable.set("Select Sheet Name" if sheets else "No sheets available")


def open_documentation():
    webbrowser.open(f"{BASE_URL}/docs/static/user-guide/pipesim-pilot/index.html#")


def open_component_param_box(parent: tk.Tk) -> None:
    """
    Opens a DualCascadeListBox window to display a list of available parameters.

    Args:
        parent (tk.Tk): The parent Tkinter window.
    """
    cascade_box = DualCascadeListBox(
        parent,
        title="Refer the list of available parameters",
        child_mapping=generate_dict_from_class(Parameters),
    )
    parent.wait_window(cascade_box)
