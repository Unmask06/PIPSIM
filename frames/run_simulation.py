import logging
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext

from core.model_input import ModelInput, PipsimModel
from core.network_simulation import NetworkSimulator
from project import TextHandler, add_logger_area, frame_store, switch_frame


def run_simulation(logger):
    logger.info("Running simulation")
    folder_path = Path(r"C:\Users\IDM252577\Desktop\Python Projects\PIPSIM")

    for pips_file in folder_path.glob("*.pips"):
        try:
            model = PipsimModel(str(pips_file), folder_path=str(folder_path))
            model_input = ModelInput()
            ns = NetworkSimulator(model, model_input)
            ns.run_existing_model()
        except Exception as e:
            print(e)


def init_run_simulation_frame(app, home_frame):
    run_simulation_frame = tk.Frame(app)
    frame_store["run_simulation"] = run_simulation_frame
    run_label = tk.Label(
        run_simulation_frame, text="Run Simulation Workflow", font=("Arial", 14)
    )
    run_label.pack(pady=10)

    input_label_rs = tk.Label(
        run_simulation_frame, text="Folder containing pipesim files"
    )
    input_label_rs.pack()
    config_file_entry_rs = tk.Entry(run_simulation_frame, width=50, state="readonly")
    config_file_entry_rs.pack()
    config_browse_button_rs = tk.Button(
        run_simulation_frame,
        text="Browse",
        command=lambda: filedialog.askopenfilename(),
    )
    config_browse_button_rs.pack(pady=5)
    submit_button_rs = tk.Button(
        run_simulation_frame, text="Submit", command=lambda: run_simulation(logger_rs)
    )
    submit_button_rs.pack(pady=10)
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
