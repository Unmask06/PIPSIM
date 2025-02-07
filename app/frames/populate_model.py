import logging
import threading
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

import pandas as pd
from sixgill.definitions import ModelComponents, Units

from app.core import ExcelInputError, PipsimModellingError
from app.core.model_populater import ModelPopulater
from app.project import (
    FRAME_STORE,
    FrameNames,
    browse_folder_or_file,
    get_string_values_from_class,
)
from app.widgets import DualSelectableCombobox

logger = logging.getLogger("app.core.model_populater")


class PopulateModelFrame(tk.Frame):
    """
    A Tkinter Frame that provides a user interface for populating a model with data from an Excel file.
    """

    export_component_listbox: tk.Listbox
    MODES = {
        "export": "Export the entire data from the mode for the selected components",
        "bulk_import": "Bulk import data into the model from the Excel file created by the export mode",
        "simple_import": "Import data into the model from selected sheet in the Excel file",
        "flowline_geometry_import": "Import flowline geometry data into the model from the Excel file",
    }

    def __init__(self, parent):
        super().__init__(parent)
        FRAME_STORE[FrameNames.POPULATE_MODEL] = self

        self.selected_mode_var = tk.StringVar(value="bulk_import")
        self.sheet_name_var = tk.StringVar(value="Select Sheet Name")
        self.unit_var = tk.StringVar(value=Units.METRIC)

        self._create_widgets()
        self.selected_mode_var.trace_add("write", self.update_sub_frame)

    def _create_widgets(self):
        self.create_title_frame().pack(pady=5)
        self.pips_frame, self.pips_entry = self.create_file_input_frame(
            "Pipesim File", "*.pips"
        )
        self.excel_frame, self.excel_entry = self.create_file_input_frame(
            "Excel File", "*.xlsx *.xls *.xlsm"
        )
        self.pips_frame.pack(pady=5)
        self.excel_frame.pack(pady=5)
        self.create_unit_option_menu_frame().pack(pady=5)
        self.create_mode_selection_frame().pack(pady=10)
        self.sub_frame = tk.Frame(self)
        self.sub_frame.pack(pady=5)
        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")
        self.create_submit_button().pack(pady=5)

    def create_title_frame(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="Populate Model Workflow", font=("Arial", 14)).pack()
        tk.Label(
            frame,
            text="This workflow populates an existing model with data from the Excel file.",
            font=("Arial", 10, "italic"),
        ).pack()
        return frame

    def create_file_input_frame(self, label_text, file_types):
        frame = tk.Frame(self)
        tk.Label(frame, text=label_text).pack()
        entry = tk.Entry(frame, width=75)
        entry.pack(side=tk.LEFT)
        tk.Button(
            frame,
            text="Browse",
            command=lambda: browse_folder_or_file(
                entry, file_types=[("Files", file_types)]
            ),
        ).pack(padx=5, side=tk.LEFT)
        return frame, entry

    def create_unit_option_menu_frame(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="Select Unit").pack()
        unit_option_menu = tk.OptionMenu(
            frame, self.unit_var, *get_string_values_from_class(Units)
        )
        unit_option_menu.pack()
        return frame

    def create_mode_selection_frame(self):
        frame = tk.Frame(self)
        for i, (mode, explanation) in enumerate(self.MODES.items()):
            tk.Radiobutton(
                frame, text=mode, variable=self.selected_mode_var, value=mode
            ).grid(row=i, column=0, sticky=tk.W)
            tk.Label(frame, text=explanation, font=("Arial", 9, "italic")).grid(
                row=i, column=1, sticky=tk.W, padx=10
            )
        return frame

    def create_submit_button(self):
        return tk.Button(self, text="Submit", command=self.submit_populate_model)

    def update_sub_frame(self, *args):
        for widget in self.sub_frame.winfo_children():
            widget.pack_forget()
        mode = self.selected_mode_var.get()
        if mode == "export":
            self.export_component_listbox = self.create_export_mode_input()
        elif mode in ["simple_import", "flowline_geometry_import"]:
            self.create_sheet_selection_mode_input()

    def create_export_mode_input(self):
        scrollable_box = self.create_scrollable_box_frame()
        self.create_dual_combo_box_button(scrollable_box)
        return scrollable_box

    def _update_sheet_names(self, option_menu: tk.OptionMenu, excel_file_path: str):
        sheet_names = pd.ExcelFile(excel_file_path).sheet_names
        menu = option_menu["menu"]
        menu.delete(0, "end")
        for sheet_name in sheet_names:
            menu.add_command(
                label=sheet_name,
                command=lambda sheet_name=sheet_name: self.sheet_name_var.set(
                    str(sheet_name)
                ),
            )

    def create_sheet_selection_mode_input(self):
        tk.Label(
            self.sub_frame,
            text=f"{self.selected_mode_var.get().replace('_', ' ').title()} Mode: Select an Excel sheet",
        ).pack()
        self.sheet_name_var.set("Select Sheet Name")
        option_menu = tk.OptionMenu(
            self.sub_frame, self.sheet_name_var, "Select Sheet Name"
        )

        option_menu.pack()
        if self.excel_entry.get():
            option_menu.config(
                postcommand=self._update_sheet_names(
                    option_menu, self.excel_entry.get()
                )
            )  # type: ignore

    def create_scrollable_box_frame(self):
        scrollable_box = tk.Listbox(self.sub_frame, height=10, width=50)
        scrollable_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(
            self.sub_frame, orient="vertical", command=scrollable_box.yview
        )
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        scrollable_box.config(yscrollcommand=scrollbar.set)
        return scrollable_box

    def create_dual_combo_box_button(self, scrollable_box):
        button = tk.Button(
            self.sub_frame,
            text="Open Dual Combo Box",
            command=lambda: self.open_dual_combo_box(scrollable_box),
        )
        button.pack()

    def open_dual_combo_box(self, scrollable_box):
        values = get_string_values_from_class(ModelComponents)
        selected_values = list(scrollable_box.get(0, tk.END))
        combobox = DualSelectableCombobox(
            scrollable_box,
            "Select Options",
            available_variables=values,
            selected_variables=selected_values,
        )
        self.sub_frame.wait_window(combobox)
        selected_values = combobox.confirm_selection()
        scrollable_box.delete(0, tk.END)
        for val in selected_values:
            scrollable_box.insert(tk.END, val)

    def submit_populate_model(self):
        pipesim_file_path = self.pips_entry.get()
        excel_file_path = self.excel_entry.get()
        sheet_name = self.sheet_name_var.get()
        mode = self.selected_mode_var.get()
        unit = self.unit_var.get()

        if (
            mode in ["simple_import", "flowline_geometry_import"]
            and sheet_name == "Select Sheet Name"
        ):
            messagebox.showerror("Error", "Please select a valid sheet name.")
            return

        def task():
            self.progress_bar.pack(pady=10)
            self.progress_bar.start()
            mp = ModelPopulater(
                pipesim_file=pipesim_file_path,
                excel_file=excel_file_path,
                mode=mode,  # type:ignore
                unit=unit,
            )
            try:
                if mode == "export":
                    lb = self.export_component_listbox
                    if not lb:
                        raise ValueError("No component list found for Export mode.")
                    mp.export_values(
                        excel_file=excel_file_path, components=list(lb.get(0, tk.END))
                    )
                elif mode == "simple_import":
                    mp.simple_import_data(sheet_name)
                elif mode == "flowline_geometry_import":
                    mp.import_flowline_geometry(sheet_name)
                elif mode == "bulk_import":
                    mp.bulk_import_values(excel_file=excel_file_path)
                messagebox.showinfo("Success", f"Model {mode}ed successfully")

            except (ExcelInputError, PipsimModellingError) as e:
                messagebox.showerror("Error", str(e))

            except Exception:
                messagebox.showerror(
                    "Unexpected Error", "Contact the developer or send the error log."
                )
                logger.error(traceback.format_exc())
            finally:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()

        threading.Thread(target=task).start()
