"""
frames/run_simulation.py
This script contains the code for the run_simulation frame of the application.
"""

import logging
import tkinter as tk
from pathlib import Path

from core.model_input import ModelInput, PipsimModel
from core.network_simulation import NetworkSimulator
from project import (
    FRAME_STORE,
    TextHandler,
    add_logger_area,
    browse_folder_or_file,
    switch_frame,
)


def run_simulation(folder_path, logger: logging.Logger):
    """
    Excutes the run_existing_model method of the NetworkSimulator class for all .pips files in the specified folder.
    i.e., Run the simulation for each .pips file in the folder.

    Args:
        folder_path (str or Path): The path to the folder containing .pips files.
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
            ns = NetworkSimulator(model, model_input)
            ns.run_existing_model()
        except Exception as e:
            logger.error(f"Error running simulation for {pips_file}: {e}")


def init_run_simulation_frame(app, home_frame):
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

    run_button_rs = tk.Button(
        run_simulation_frame,
        text="Run Simulations",
        command=lambda: run_simulation(config_file_entry_rs.get(), logger_rs),
    )
    run_button_rs.pack(pady=10)
    log_text_rs = add_logger_area(run_simulation_frame)
    back_button_rs = tk.Button(
        run_simulation_frame,
        text="Back to Home",
        command=lambda: switch_frame(home_frame),
    )
    back_button_rs.pack(pady=10)
    logger_rs = logging.getLogger("RunSimulationLogger")
    logger_rs.setLevel(logging.INFO)
    logger_rs.addHandler(TextHandler(log_text_rs))
    return run_simulation_frame
