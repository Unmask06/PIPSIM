"""
frame/multi_case.py
This module contains the MultiCaseFrame class which is responsible for handling the multi-case workflow.
"""

import logging
import os
import threading
import tkinter as tk
import traceback
from tkinter import messagebox, ttk
from typing import Callable

from app.core import ExcelInputError
from app.core.multi_case_modeller import MultiCaseModeller
from app.project import (
    FRAME_STORE,
    FrameNames,
    browse_folder_or_file,
    update_optionmenu_with_excelsheets,
)

logger = logging.getLogger("app.core.multi_case_modeller")


class MultiCaseFrame(tk.Frame):
    def __init__(self, parent: tk.Tk):
        super().__init__(parent)
        self.parent = parent
        self.pack()

        FRAME_STORE[FrameNames.MULTI_CASE] = self

        self.multi_case_sheet_var = tk.StringVar(value="Select Sheet Name")

        self.create_widgets()

    def create_widgets(self):
        self.create_title_frame()
        self.create_file_input_frames()
        self.create_option_menus()
        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")
        self.create_submit_button()

    def create_title_frame(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Label(frame, text="Multi-Case Workflow", font=("Arial", 14)).pack()
        tk.Label(
            frame,
            text="This workflow creates multiple models from an Excel file.",
            font=("Arial", 10, "italic"),
        ).pack(pady=5)

    def create_file_input_frames(self):
        self.base_pip_file_entry = self.create_file_input_frame(
            "Base Pipesim File", self.browse_pip_file
        )

        self.excel_file_entry = self.create_file_input_frame(
            "Excel File", self.browse_excel_file
        )

    def create_file_input_frame(
        self, label_text: str, browse_command: Callable
    ) -> tk.Entry:
        frame = tk.Frame(self)
        frame.pack(pady=5)
        tk.Label(frame, text=label_text).pack()
        entry = tk.Entry(frame, width=75)
        entry.pack(side=tk.LEFT)
        tk.Button(frame, text="Browse", command=browse_command).pack(
            padx=5, side=tk.LEFT
        )
        return entry

    def browse_excel_file(self):
        path = browse_folder_or_file(
            self.excel_file_entry, file_types=[("Excel Files", "*.xlsx *.xls *.xlsm")]
        )
        if path:
            update_optionmenu_with_excelsheets(
                self.sheet_dropdown,
                self.multi_case_sheet_var,
                excel_file_path=path,
            )

    def browse_pip_file(self):
        browse_folder_or_file(
            self.base_pip_file_entry, file_types=[("Pip Files", "*.pips")]
        )

    def create_option_menus(self):
        sheet_frames = tk.Frame(self)
        sheet_frames.pack(pady=5)

        self.sheet_dropdown = self.create_option_menu(
            sheet_frames, self.multi_case_sheet_var, "Multi-Case Sheet"
        )

    def create_option_menu(
        self, parent, variable: tk.StringVar, label_text: str
    ) -> tk.OptionMenu:
        frame = tk.Frame(parent)
        frame.pack(side=tk.LEFT, padx=10)
        tk.Label(frame, text=label_text).pack()
        option_menu = tk.OptionMenu(frame, variable, "Select Sheet Name")
        option_menu.pack()
        return option_menu

    def create_result_folder_button(self, path: str) -> tk.Button:

        for widget in self.winfo_children():
            if isinstance(widget, tk.Button):
                if widget.cget("text") == "Open Result Folder":
                    widget.destroy()
                    break
        return tk.Button(
            self,
            text="Open Result Folder",
            command=lambda: os.startfile(path),
        )

    def create_submit_button(self):
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Button(frame, text="Submit", command=self.on_submit).pack()

    def on_submit(self):
        threading.Thread(target=self.submit_multi_case_workflow).start()

    def submit_multi_case_workflow(self):
        self.progress_bar.pack(pady=10)
        self.progress_bar.start()

        try:
            mbm = MultiCaseModeller(
                base_model_path=self.base_pip_file_entry.get(),
                excel_path=self.excel_file_entry.get(),
                multi_case_sheet=self.multi_case_sheet_var.get(),
            )
            model_path = mbm.build_all_models()
            self.parent.after(
                0,
                lambda: messagebox.showinfo(
                    "Success", "Multi-case workflow handled successfully"
                ),
            )
            self.create_result_folder_button(str(model_path)).pack()
        except ExcelInputError as e:
            logger.error(f"Excel input error: {e}")
            self.parent.after(
                0, lambda: messagebox.showerror("Error", f"Excel input error: {e}")
            )
        except Exception as e:
            logger.error(f"Error handling multi-case workflow: {e}")
            logger.error(traceback.format_exc())
            self.parent.after(
                0,
                lambda: messagebox.showerror(
                    "Unexpected Error", "Contact the developer for help"
                ),
            )
        finally:
            self.parent.after(0, self.progress_bar.stop)
            self.parent.after(0, self.progress_bar.pack_forget)
