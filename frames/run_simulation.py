"""
frames/run_simulation.py
This script contains the code for the run_simulation frame of the application.
"""

import json
import logging
import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from sixgill.definitions import ProfileVariables, SystemVariables, Units

from core import NetworkSimulationError
from core.network_simulation import NetworkSimulator
from project import FRAME_STORE, browse_folder_or_file, get_string_values_from_class
from widgets.dual_combo_box import DualSelectableCombobox

logger = logging.getLogger("core.network_simulation")


def run_simulation(folder_path, system_vars, profile_vars, unit, parent):
    """
    Excutes the run_existing_model method of the NetworkSimulator class for all .pips files in the specified folder.
    i.e., Run the simulation for each .pips file in the folder.

    Args:
        folder_path (str or Path): The path to the folder containing .pips files.
        system_vars (list): List of system variables to be used in the simulation.
        profile_vars (list): List of profile variables to be used in the simulation.
        unit (str): Unit to be used in the simulation.

    Raises:
        Exception: If an error occurs during the simulation of any .pips file, it will be caught and printed.
    """

    logger.info("Running simulation")
    folder_path = Path(folder_path)
    logger.debug(
        f"System Variables: {system_vars}, Profile Variables: {profile_vars}, Unit: {unit}"
    )

    for pips_file in folder_path.glob("*.pips"):
        try:
            ns = NetworkSimulator(str(pips_file), system_vars, profile_vars, unit)
            ns.run_existing_model()
        except NetworkSimulationError as e:
            logger.error(e)
    create_results_button_frame(parent, ns.NODE_RESULTS_FILE, ns.PROFILE_RESULTS_FILE)
    messagebox.showinfo("Success", "Simulation completed successfully")


def open_checkable_combobox(parent, title, values, listbox):
    combobox = DualSelectableCombobox(parent, title, values)
    parent.wait_window(combobox)
    selected_values = combobox.confirm_selection()
    listbox.delete(0, tk.END)
    for val in selected_values:
        listbox.insert(tk.END, val)


def save_selections(system_vars, profile_vars):
    selections = {
        "system_vars": system_vars,
        "profile_vars": profile_vars,
    }
    file_path = filedialog.asksaveasfilename(
        defaultextension=".json", filetypes=[("JSON files", "*.json")]
    )
    if file_path:
        with open(file_path, "w") as f:
            json.dump(selections, f)
        messagebox.showinfo("Success", "Selections saved successfully")


def load_selections(system_vars_listbox, profile_vars_listbox):
    file_path = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")], title="Select a JSON file"
    )
    if file_path:
        with open(file_path, "r") as f:
            selections = json.load(f)
        system_vars_listbox.delete(0, tk.END)
        for var in selections.get("system_vars", []):
            system_vars_listbox.insert(tk.END, var)
        profile_vars_listbox.delete(0, tk.END)
        for var in selections.get("profile_vars", []):
            profile_vars_listbox.insert(tk.END, var)
        messagebox.showinfo("Success", "Selections loaded successfully")


def create_results_button_frame(run_simulation_frame, node_results, profile_results):
    results_button_frame = tk.Frame(run_simulation_frame)
    results_button_frame.pack(pady=10)
    node_results_button = tk.Button(
        results_button_frame,
        text="Node Results",
        command=lambda: os.startfile(node_results),
    )
    profile_results_button = tk.Button(
        results_button_frame,
        text="Profile Results",
        command=lambda: os.startfile(profile_results),
    )
    node_results_button.pack(side=tk.LEFT, padx=5)
    profile_results_button.pack(side=tk.LEFT, padx=5)
    return results_button_frame


def init_run_simulation_frame(app):
    run_simulation_frame = tk.Frame(app)
    FRAME_STORE["run_simulation"] = run_simulation_frame
    run_label = tk.Label(
        run_simulation_frame, text="Run Simulation Workflow", font=("Arial", 14)
    )
    run_label.pack(pady=10)

    input_label_rs = tk.Label(
        run_simulation_frame, text="Folder containing pipesim files"
    )
    input_label_rs.pack()

    entry_frame = tk.Frame(run_simulation_frame)
    entry_frame.pack(pady=5)

    folder_entry_rs = tk.Entry(entry_frame, width=80, state="readonly")
    folder_entry_rs.pack(side=tk.LEFT)

    config_browse_button_rs = tk.Button(
        entry_frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            folder_entry_rs, title="Select a folder", select_folder=True
        ),
    )
    config_browse_button_rs.pack(side=tk.LEFT, padx=5)

    # Variables Frame
    variables_frame = tk.Frame(run_simulation_frame)
    variables_frame.pack(pady=5)

    # System Variables Listbox
    system_vars_frame = tk.Frame(variables_frame)
    system_vars_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")
    system_vars_label = tk.Label(system_vars_frame, text="System Variables")
    system_vars_label.pack(pady=5)
    system_vars_listbox = tk.Listbox(
        system_vars_frame, selectmode=tk.MULTIPLE, height=10
    )
    system_vars_listbox.pack(pady=5)
    system_vars_add_button = tk.Button(
        system_vars_frame,
        text="Add",
        command=lambda: open_checkable_combobox(
            app,
            "Select System Variables",
            get_string_values_from_class(SystemVariables),
            system_vars_listbox,
        ),
    )
    system_vars_add_button.pack(pady=5)

    # Center Frame
    center_frame = tk.Frame(variables_frame)
    center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
    unit_label = tk.Label(center_frame, text="Select Unit")
    unit_label.pack(pady=5)
    unit_var = tk.StringVar(run_simulation_frame)
    unit_var.set(Units.METRIC)
    unit_optionmenu = tk.OptionMenu(
        center_frame, unit_var, *get_string_values_from_class(Units)
    )
    unit_optionmenu.pack(pady=5)

    ## Buttons
    save_button = tk.Button(
        center_frame,
        text="Save Selections",
        command=lambda: save_selections(
            list(system_vars_listbox.get(0, tk.END)),
            list(profile_vars_listbox.get(0, tk.END)),
        ),
    )
    save_button.pack(pady=5)

    load_button = tk.Button(
        center_frame,
        text="Load Selections",
        command=lambda: load_selections(system_vars_listbox, profile_vars_listbox),
    )
    load_button.pack(pady=5)

    run_button_rs = tk.Button(
        center_frame,
        text="Run Simulations",
        command=lambda: run_simulation(
            folder_entry_rs.get(),
            list(system_vars_listbox.get(0, tk.END)),
            list(profile_vars_listbox.get(0, tk.END)),
            unit_var.get(),
            run_simulation_frame,
        ),
    )
    run_button_rs.config(font=("Arial", 12, "bold"), height=1, width=20)
    run_button_rs.pack(pady=40)

    # Profile Variables Listbox
    profile_vars_frame = tk.Frame(variables_frame)
    profile_vars_frame.grid(row=0, column=2, padx=10, pady=10, sticky="n")
    profile_vars_label = tk.Label(profile_vars_frame, text="Profile Variables")
    profile_vars_label.pack(pady=5)
    profile_vars_listbox = tk.Listbox(
        profile_vars_frame, selectmode=tk.MULTIPLE, height=10
    )
    profile_vars_listbox.pack(pady=5)
    profile_vars_add_button = tk.Button(
        profile_vars_frame,
        text="Add",
        command=lambda: open_checkable_combobox(
            app,
            "Select Profile Variables",
            get_string_values_from_class(ProfileVariables),
            profile_vars_listbox,
        ),
    )
    profile_vars_add_button.pack(pady=5)

    return run_simulation_frame
