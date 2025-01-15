"""
frames/run_simulation.py
This script contains the code for the run_simulation frame of the application.
"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from sixgill.definitions import ProfileVariables, SystemVariables, Units

from core.model_input import ModelInput, PipsimModel
from core.network_simulation import NetworkSimulator
from project import (
    FRAME_STORE,
    browse_folder_or_file,
    get_string_values_from_class,
    switch_frame,
)
from widgets.checkable_combo_box import CheckableCombobox

logger = logging.getLogger("core.network_simulation")


def run_simulation(folder_path, system_vars, profile_vars, unit):
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
        except Exception as e:
            logger.error(f"Error running simulation for {pips_file}: {e}")


def open_checkable_combobox(parent, title, values, listbox):
    combobox = CheckableCombobox(parent, title, values)
    parent.wait_window(combobox)
    selected_values = combobox.confirm_selection()
    listbox.delete(0, tk.END)
    for val in selected_values:
        listbox.insert(tk.END, val)


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
    variables_frame.pack(pady=10)

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

    # Unit OptionMenu
    unit_frame = tk.Frame(variables_frame)
    unit_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")
    unit_label = tk.Label(unit_frame, text="Select Unit")
    unit_label.pack(pady=5)
    unit_var = tk.StringVar(run_simulation_frame)
    unit_var.set(Units.METRIC)
    unit_optionmenu = tk.OptionMenu(
        unit_frame, unit_var, *get_string_values_from_class(Units)
    )
    unit_optionmenu.pack(pady=5)

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

    run_button_rs = tk.Button(
        run_simulation_frame,
        text="Run Simulations",
        command=lambda: run_simulation(
            folder_entry_rs.get(),
            list(system_vars_listbox.get(0, tk.END)),
            list(profile_vars_listbox.get(0, tk.END)),
            unit_var.get(),
        ),
    )
    run_button_rs.pack(pady=10)

    return run_simulation_frame
