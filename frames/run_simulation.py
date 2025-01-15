"""
frames/run_simulation.py
This script contains the code for the run_simulation frame of the application.
"""

import logging
import tkinter as tk
from pathlib import Path
from tkinter import ttk

from core.model_input import ModelInput, PipsimModel
from core.network_simulation import NetworkSimulator
from project import FRAME_STORE, browse_folder_or_file, switch_frame
from frames.checkable_combo_box import CheckableCombobox

logger = logging.getLogger("core.network_simulation")


def run_simulation(folder_path, system_vars, profile_vars, unit, logger: logging.Logger):
    """
    Excutes the run_existing_model method of the NetworkSimulator class for all .pips files in the specified folder.
    i.e., Run the simulation for each .pips file in the folder.

    Args:
        folder_path (str or Path): The path to the folder containing .pips files.
        system_vars (list): List of system variables to be used in the simulation.
        profile_vars (list): List of profile variables to be used in the simulation.
        unit (str): Unit to be used in the simulation.
        logger (logging.Logger): The logger instance for logging information.

    Raises:
        Exception: If an error occurs during the simulation of any .pips file, it will be caught and printed.
    """

    logger.info("Running simulation")
    folder_path = Path(folder_path)

    for pips_file in folder_path.glob("*.pips"):
        try:
            model = PipsimModel(str(pips_file), folder_path=str(folder_path))
            model_input = ModelInput()
            ns = NetworkSimulator(model, model_input, system_vars, profile_vars, unit)
            ns.run_existing_model()
        except Exception as e:
            logger.error(f"Error running simulation for {pips_file}: {e}")


def open_checkable_combobox(parent, title, values, listbox):
    combobox = CheckableCombobox(parent, title, values)
    parent.wait_window(combobox)
    listbox.delete(0, tk.END)
    for val in combobox.selected_values:
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

    config_file_entry_rs = tk.Entry(entry_frame, width=80, state="readonly")
    config_file_entry_rs.pack(side=tk.LEFT)

    config_browse_button_rs = tk.Button(
        entry_frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            config_file_entry_rs, title="Select a folder", select_folder=True
        ),
    )
    config_browse_button_rs.pack(side=tk.LEFT, padx=5)

    # System Variables Listbox
    system_vars_frame = tk.Frame(run_simulation_frame)
    system_vars_frame.pack(pady=5)
    system_vars_label = tk.Label(system_vars_frame, text="System Variables")
    system_vars_label.pack()
    system_vars_listbox = tk.Listbox(system_vars_frame, selectmode=tk.MULTIPLE, height=10)
    system_vars_listbox.pack(side=tk.LEFT, padx=5)
    system_vars_add_button = tk.Button(
        system_vars_frame,
        text="Add",
        command=lambda: open_checkable_combobox(
            app, "Select System Variables", ["Var1", "Var2", "Var3"], system_vars_listbox
        ),
    )
    system_vars_add_button.pack(side=tk.LEFT, padx=5)

    # Profile Variables Listbox
    profile_vars_frame = tk.Frame(run_simulation_frame)
    profile_vars_frame.pack(pady=5)
    profile_vars_label = tk.Label(profile_vars_frame, text="Profile Variables")
    profile_vars_label.pack()
    profile_vars_listbox = tk.Listbox(profile_vars_frame, selectmode=tk.MULTIPLE, height=10)
    profile_vars_listbox.pack(side=tk.LEFT, padx=5)
    profile_vars_add_button = tk.Button(
        profile_vars_frame,
        text="Add",
        command=lambda: open_checkable_combobox(
            app, "Select Profile Variables", ["Var1", "Var2", "Var3"], profile_vars_listbox
        ),
    )
    profile_vars_add_button.pack(side=tk.LEFT, padx=5)

    # Unit OptionMenu
    unit_var = tk.StringVar(run_simulation_frame)
    unit_var.set("Select Unit")
    unit_label = tk.Label(run_simulation_frame, text="Select Unit")
    unit_label.pack()
    unit_optionmenu = tk.OptionMenu(run_simulation_frame, unit_var, "Unit1", "Unit2", "Unit3")
    unit_optionmenu.pack(pady=5)

    run_button_rs = tk.Button(
        run_simulation_frame,
        text="Run Simulations",
        command=lambda: run_simulation(
            config_file_entry_rs.get(),
            list(system_vars_listbox.get(0, tk.END)),
            list(profile_vars_listbox.get(0, tk.END)),
            unit_var.get(),
            logger,
        ),
    )
    run_button_rs.pack(pady=10)

    return run_simulation_frame
