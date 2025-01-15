# Home Frame
import logging
import tkinter as tk

from project import FRAME_STORE, switch_frame

logger = logging.getLogger(__name__)


def init_home_frame(app: tk.Tk) -> tk.Frame:
    home_frame = tk.Frame(app)
    FRAME_STORE["home"] = home_frame
    label = tk.Label(
        home_frame, text="Welcome to PANDORA's Pipesim Pilot", font=("Arial", 16)
    )
    label.pack(pady=20)

    create_model_button = tk.Button(
        home_frame,
        text="Create Model Workflow",
        command=lambda: switch_frame(FRAME_STORE["create_model"]),
        width=30,
    )
    create_model_button.pack(pady=5)

    update_conditions_button = tk.Button(
        home_frame,
        text="Update Conditions Workflow",
        command=lambda: switch_frame(FRAME_STORE["update_conditions"]),
        width=30,
    )
    update_conditions_button.pack(pady=5)

    run_simulation_button = tk.Button(
        home_frame,
        text="Run Simulation Workflow",
        command=lambda: switch_frame(FRAME_STORE["run_simulation"]),
        width=30,
    )
    run_simulation_button.pack(pady=5)

    summarize_results_button = tk.Button(
        home_frame,
        text="Summarize Results Workflow",
        command=lambda: switch_frame(FRAME_STORE["summarize"]),
        width=30,
    )
    summarize_results_button.pack(pady=5)

    exit_button = tk.Button(home_frame, text="Exit", command=app.quit, width=30)
    exit_button.pack(pady=10)

    return home_frame
