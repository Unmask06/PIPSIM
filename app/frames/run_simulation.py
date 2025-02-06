import json
import logging
import os
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from sixgill.definitions import ProfileVariables, SystemVariables, Units

from app.core import NetworkSimulationError
from app.core.network_simulation import NetworkSimulator
from app.project import FRAME_STORE, browse_folder_or_file, get_string_values_from_class
from app.widgets.dual_combo_box import DualSelectableCombobox

logger = logging.getLogger("app.core.network_simulation")


class RunSimulationFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        FRAME_STORE["run_simulation"] = self
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self, text="Run Simulation Workflow", font=("Arial", 14)).pack(pady=10)

        tk.Label(self, text="Folder containing pipesim files").pack()
        entry_frame = tk.Frame(self)
        entry_frame.pack(pady=5)

        self.folder_entry = tk.Entry(entry_frame, width=80, state="readonly")
        self.folder_entry.pack(side=tk.LEFT)

        tk.Button(entry_frame, text="Browse", command=self.browse_folder).pack(
            side=tk.LEFT, padx=5
        )

        self.create_variables_section()

        self.progress_bar = ttk.Progressbar(self, mode="indeterminate")

        tk.Button(
            self,
            text="Run Simulations",
            font=("Arial", 12, "bold"),
            height=1,
            width=20,
            command=self.run_simulation,
        ).pack(pady=40)

    def create_variables_section(self):
        variables_frame = tk.Frame(self)
        variables_frame.pack(pady=5)

        self.system_vars_listbox = self.create_listbox(
            variables_frame, "System Variables", row=0, column=0, values=SystemVariables
        )
        self.unit_var = self.create_unit_selection(variables_frame)
        self.profile_vars_listbox = self.create_listbox(
            variables_frame,
            "Profile Variables",
            row=0,
            column=2,
            values=ProfileVariables,
        )

    def create_listbox(self, parent, label, row, column, values: type):
        frame = tk.Frame(parent)
        frame.grid(row=row, column=column, padx=10, pady=10, sticky="n")
        tk.Label(frame, text=label).pack(pady=5)
        listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=10)
        listbox.pack(pady=5)
        tk.Button(
            frame,
            text="Add",
            command=lambda: self.open_checkable_combobox(label, values, listbox),
        ).pack(pady=5)
        return listbox

    def create_unit_selection(self, parent):
        frame = tk.Frame(parent)
        frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
        tk.Label(frame, text="Select Unit").pack(pady=5)
        unit_var = tk.StringVar(self)
        unit_var.set(Units.METRIC)
        tk.OptionMenu(frame, unit_var, *get_string_values_from_class(Units)).pack(
            pady=5
        )

        tk.Button(frame, text="Save Selections", command=self.save_selections).pack(
            pady=5
        )
        tk.Button(frame, text="Load Selections", command=self.load_selections).pack(
            pady=5
        )
        return unit_var

    def browse_folder(self):
        browse_folder_or_file(
            self.folder_entry, title="Select a folder", select_folder=True
        )

    def open_checkable_combobox(self, title, values, listbox):
        combobox = DualSelectableCombobox(
            self.parent, title, get_string_values_from_class(values)
        )
        self.parent.wait_window(combobox)
        selected_values = combobox.confirm_selection()
        listbox.delete(0, tk.END)
        for val in selected_values:
            listbox.insert(tk.END, val)

    def save_selections(self):
        selections = {
            "system_vars": list(self.system_vars_listbox.get(0, tk.END)),
            "profile_vars": list(self.profile_vars_listbox.get(0, tk.END)),
        }
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            with open(file_path, "w") as f:
                json.dump(selections, f)
            messagebox.showinfo("Success", "Selections saved successfully")

    def load_selections(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")], title="Select a JSON file"
        )
        if file_path:
            with open(file_path, "r") as f:
                selections = json.load(f)
            self.system_vars_listbox.delete(0, tk.END)
            for var in selections.get("system_vars", []):
                self.system_vars_listbox.insert(tk.END, var)
            self.profile_vars_listbox.delete(0, tk.END)
            for var in selections.get("profile_vars", []):
                self.profile_vars_listbox.insert(tk.END, var)
            messagebox.showinfo("Success", "Selections loaded successfully")

    def run_simulation(self):
        folder_path = self.folder_entry.get()
        system_vars = list(self.system_vars_listbox.get(0, tk.END))
        profile_vars = list(self.profile_vars_listbox.get(0, tk.END))
        unit = self.unit_var.get()

        def task():
            self.progress_bar.pack(pady=10)
            logger.info("Running simulation")
            folder = Path(folder_path)
            logger.debug(
                f"System Variables: {system_vars}, Profile Variables: {profile_vars}, Unit: {unit}"
            )
            self.progress_bar.start()
            try:
                for pips_file in folder.glob("*.pips"):
                    ns = NetworkSimulator(
                        str(pips_file),
                        system_vars,
                        profile_vars,
                        unit,
                        folder=str(folder),
                    )
                    ns.run_existing_model()
                self.create_results_button_frame(
                    ns.NODE_RESULTS_FILE, ns.PROFILE_RESULTS_FILE
                )
                messagebox.showinfo("Success", "Simulation completed successfully")
            except NetworkSimulationError as e:
                logger.error(e)
            finally:
                self.progress_bar.stop()
                self.progress_bar.pack_forget()

        threading.Thread(target=task).start()

    def create_results_button_frame(self, node_results, profile_results):
        frame = tk.Frame(self)
        frame.pack(pady=10)
        tk.Button(
            frame, text="Node Results", command=lambda: os.startfile(node_results)
        ).pack(side=tk.LEFT, padx=5)
        tk.Button(
            frame, text="Profile Results", command=lambda: os.startfile(profile_results)
        ).pack(side=tk.LEFT, padx=5)
        return frame
