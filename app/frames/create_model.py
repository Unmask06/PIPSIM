import logging
import threading
import tkinter as tk
import traceback
from tkinter import messagebox, ttk

from sixgill.definitions import Units

from app.core import ExcelInputError, PipsimModellingError
from app.core.helper import get_string_values_from_class
from app.core.model_builder import ModelBuilder
from app.project import (
    FRAME_STORE,
    FrameNames,
    browse_folder_or_file,
    update_optionmenu_with_excelsheets,
)

logger = logging.getLogger("app.core.model_builder")


class CreateModelFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        FRAME_STORE[FrameNames.CREATE_MODEL] = self

        self.sheet_name_var = tk.StringVar(value="Select Sheet Name")
        self.unit_var = tk.StringVar(value=Units.METRIC)
        self._create_widgets()

    def _create_widgets(self):
        self.create_title_frame().pack(pady=10)
        self.create_help_frame().pack(pady=5)

        self.pipesim_frame, self.pipesim_entry = self.create_file_input_frame(
            "Pipesim File", "*.pips"
        )
        self.pipesim_frame.pack(pady=5)

        self.excel_frame, self.excel_entry = self.create_file_input_frame(
            "Excel File", "*.xlsx *.xls *.xlsm", self.update_sheet_names
        )
        self.excel_frame.pack(pady=5)

        self.option_menu_frame, self.sheet_name_dropdown = (
            self.create_option_menu_frame()
        )
        self.option_menu_frame.pack(pady=5)

        self.unit_option_menu_frame = self.create_unit_option_menu_frame()
        self.unit_option_menu_frame.pack(pady=5)

        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")

        self.create_submit_button().pack(pady=10)

    def create_title_frame(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="Create Model Workflow", font=("Arial", 14)).pack()
        return frame

    def create_help_frame(self):
        frame = tk.Frame(self)
        help_text = """This workflow creates a model from scratch using the Excel file or
        populates an existing model with data from the Excel file."""
        tk.Label(frame, text=help_text, font=("Arial", 10, "italic")).pack()
        return frame

    def create_file_input_frame(self, label_text, file_types, command=None):
        frame = tk.Frame(self)
        tk.Label(frame, text=label_text).pack()
        entry = tk.Entry(frame, width=75)
        entry.pack(side=tk.LEFT)
        browse_button = tk.Button(
            frame,
            text="Browse",
            command=lambda: browse_folder_or_file(
                entry, file_types=[("Files", file_types)]
            ),
        )
        browse_button.pack(padx=5, side=tk.LEFT)

        if command:
            browse_button.configure(command=lambda: command(entry))

        return frame, entry

    def create_option_menu_frame(self):
        frame = tk.Frame(self)
        option_menu = tk.OptionMenu(frame, self.sheet_name_var, "Select Sheet Name")
        option_menu.pack()
        return frame, option_menu

    def create_unit_option_menu_frame(self):
        frame = tk.Frame(self)
        tk.Label(frame, text="Select Unit").pack()
        unit_option_menu = tk.OptionMenu(
            frame, self.unit_var, *get_string_values_from_class(Units)
        )
        unit_option_menu.pack()
        return frame

    def create_submit_button(self):
        return tk.Button(self, text="Submit", command=self.submit_create_model)

    def browse_and_update_optionmenu(self, entry_widget: tk.Entry):
        file_path = browse_folder_or_file(
            entry_widget, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
        )
        update_optionmenu_with_excelsheets(
            self.sheet_name_dropdown, self.sheet_name_var, file_path
        )

    def update_sheet_names(self, entry_widget):
        self.browse_and_update_optionmenu(entry_widget)

    def submit_create_model(self):
        pipesim_file_path = self.pipesim_entry.get()
        excel_file_path = self.excel_entry.get()
        sheet_name = self.sheet_name_var.get()
        unit = self.unit_var.get()

        if sheet_name == "Select Sheet Name":
            messagebox.showerror("Error", "Please select a valid sheet name.")
            return

        def task():
            self.progress_bar.pack(pady=10)
            logger.info("Creating model from scratch")
            self.progress_bar.start()

            try:
                mb = ModelBuilder(
                    pipsim_file_path=pipesim_file_path,
                    excel_file_path=excel_file_path,
                    sheet_name=sheet_name,
                    units=unit,
                )
                mb.create_model()
                messagebox.showinfo("Success", "Model created successfully")
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
