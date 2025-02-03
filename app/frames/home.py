# Home Frame
import logging
import tkinter as tk

from app.project import FRAME_STORE, switch_frame
from app.config import VERSION

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

    copy_flowline_data_button = tk.Button(
        home_frame,
        text="Copy Flowline Data Workflow",
        command=lambda: switch_frame(FRAME_STORE["update_conditions"]),
        width=30,
    )

    run_simulation_button = tk.Button(
        home_frame,
        text="Run Simulation Workflow",
        command=lambda: switch_frame(FRAME_STORE["run_simulation"]),
        width=30,
    )

    summarize_results_button = tk.Button(
        home_frame,
        text="Summarize Results Workflow",
        command=lambda: switch_frame(FRAME_STORE["summarize"]),
        width=30,
    )

    multi_case_button = tk.Button(
        home_frame,
        text="Multi-Case Workflow",
        command=lambda: switch_frame(FRAME_STORE["multi_case"]),
        width=30,
    )

    home_frame.pack(pady=10)
    create_model_button.pack(pady=5)
    multi_case_button.pack(pady=5)
    run_simulation_button.pack(pady=5)
    copy_flowline_data_button.pack(pady=5)
    summarize_results_button.pack(pady=5)

    exit_button = tk.Button(home_frame, text="Exit", command=app.quit, width=30)
    exit_button.pack(pady=10)

    return home_frame
