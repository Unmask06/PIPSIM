import logging
import tkinter as tk

from app.config import VERSION
from app.project import FRAME_STORE, switch_frame

logger = logging.getLogger(__name__)


class FrameNames:
    HOMEFRAME = "home"
    CREATE_MODEL = "create_model"
    POPULATE_MODEL = "populate_model"
    UPDATE_CONDITIONS = "update_conditions"
    RUN_SIMULATION = "run_simulation"
    SUMMARIZE = "summarize"
    MULTI_CASE = "multi_case"


class HomeFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        FRAME_STORE["home"] = self
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):
        tk.Label(
            self, text="Welcome to PANDORA's Pipesim Pilot", font=("Arial", 16)
        ).pack(pady=20)

        self.create_navigation_buttons()

        tk.Button(self, text="Exit", command=self.parent.quit, width=30).pack(pady=10)

    def create_navigation_buttons(self):
        buttons = [
            ("Create Model Workflow", FrameNames.CREATE_MODEL),
            ("Populate Model Workflow", FrameNames.POPULATE_MODEL),
            ("Copy Flowline Data Workflow", FrameNames.UPDATE_CONDITIONS),
            ("Run Simulation Workflow", FrameNames.RUN_SIMULATION),
            ("Summarize Results Workflow", FrameNames.SUMMARIZE, tk.DISABLED),
            ("Multi-Case Workflow", FrameNames.MULTI_CASE, tk.DISABLED),
        ]

        for text, frame_key, *state in buttons:
            state = state[0] if state else tk.NORMAL
            tk.Button(
                self,
                text=text,
                command=lambda key=frame_key: switch_frame(FRAME_STORE[key]),
                width=30,
                state=state,
            ).pack(pady=5)
