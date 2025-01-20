import logging
import tkinter as tk
import webbrowser
from tkinter import messagebox
from typing import Callable

from sixgill.definitions import Parameters

from config import BASE_URL
from core import ExcelInputError
from core.multi_case_modeller import MultiCaseModeller
from project import (
    FRAME_STORE,
    browse_folder_or_file,
    update_optionmenu_with_excelsheets,
)

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
    help_text = """ 
    Read the documentation to understand how to use the multi-case workflow.
    """

    def open_documentation():
        webbrowser.open(
            f"{BASE_URL}/docs/static/user-guide/pipesim-userguide/pipesim-pilot-user-guide.html#multi-case-simulation-workflow"
        )

    help_button = tk.Button(
        frame, text="Open Documentation", command=open_documentation
    )

    help_label = tk.Label(frame, text=help_text, font=("Arial", 10, "italic"))
    help_label.pack(side=tk.LEFT)
    help_button.pack(side=tk.LEFT, padx=10)
    return frame


def create_file_input_frame(
    parent, label_text: str, browse_command: Callable
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
    parent, variable: tk.StringVar, label_text: str = "Label"
) -> tuple[tk.Frame, tk.OptionMenu]:
    frame = tk.Frame(parent)
    frame.pack(pady=5)
    label = tk.Label(frame, text=label_text)
    label.pack()
    option_menu = tk.OptionMenu(frame, variable, "Select Sheet Name")
    option_menu.pack()
    return frame, option_menu


def create_submit_button_frame(parent, command) -> tk.Frame:
    frame = tk.Frame(parent)
    frame.pack(pady=10)
    submit_button = tk.Button(frame, text="Submit", command=command)
    submit_button.pack()
    return frame


def browse_and_update_optionmenu(entry_widget, option_menus: list, variables: list):
    path = browse_folder_or_file(entry_widget, file_types=[("Excel Files", "*.xlsx")])
    if path:
        # update_optionmenu_with_excelsheets(option_menu, variable, excel_file_path=path)
        for option_menu, variable in zip(option_menus, variables):
            update_optionmenu_with_excelsheets(
                option_menu, variable, excel_file_path=path
            )


def submit_multi_case_workflow(
    base_pip_file: str,
    excel_file_path: str,
    well_profile_sheet: str,
    conditions_sheet: str,
) -> None:
    logger.info("Handling multi-case workflow")
    try:
        mbm = MultiCaseModeller(
            base_model_path=base_pip_file,
            excel_path=excel_file_path,
            sink_profile_sheet=well_profile_sheet,
            condition_sheet=conditions_sheet,
        )

        mbm.build_all_models(sink_parameter=Parameters.Sink.LIQUIDFLOWRATE)
        messagebox.showinfo("Success", "Multi-case workflow handled successfully")

    except ExcelInputError as e:
        logger.error(f"Excel input error: {e}")
        messagebox.showerror("Error", f"Excel input error: {e}")


def init_multi_case_frame(app: tk.Tk) -> tk.Frame:
    multi_case_frame = tk.Frame(app)
    FRAME_STORE["multi_case"] = multi_case_frame

    create_title_frame(multi_case_frame)

    create_help_frame(multi_case_frame)

    excel_frame, excel_file_entry = create_file_input_frame(
        multi_case_frame,
        "Excel File",
        lambda: browse_and_update_optionmenu(
            excel_file_entry,
            [well_profile_sheet_dropdown, conditions_sheet_dropdown],
            [well_profile_sheet_var, conditions_sheet_var],
        ),
    )

    well_profile_sheet_var = tk.StringVar()
    well_profile_sheet_var.set("Select Sheet Name")
    sheet_frames = tk.Frame(multi_case_frame)
    sheet_frames.pack(pady=5)

    well_profile_sheet_var = tk.StringVar()
    well_profile_sheet_var.set("Select Sheet Name")
    well_profile_sheet_frame, well_profile_sheet_dropdown = create_option_menu_frame(
        sheet_frames, well_profile_sheet_var, "Well Profile Sheet Name"
    )
    well_profile_sheet_frame.pack(side=tk.LEFT, padx=10)

    conditions_sheet_var = tk.StringVar()
    conditions_sheet_var.set("Select Sheet Name")
    conditions_sheet_frame, conditions_sheet_dropdown = create_option_menu_frame(
        sheet_frames, conditions_sheet_var, "Conditions Sheet Name"
    )
    conditions_sheet_frame.pack(side=tk.LEFT, padx=10)

    base_pip_frame, base_pip_file_entry = create_file_input_frame(
        multi_case_frame,
        "Base Pip File",
        lambda: browse_folder_or_file(
            base_pip_file_entry, file_types=[("Pip Files", "*.pips")]
        ),
    )

    def on_submit() -> None:
        submit_multi_case_workflow(
            base_pip_file_entry.get(),
            excel_file_entry.get(),
            well_profile_sheet_var.get(),
            conditions_sheet_var.get(),
        )

    create_submit_button_frame(multi_case_frame, on_submit)

    return multi_case_frame
