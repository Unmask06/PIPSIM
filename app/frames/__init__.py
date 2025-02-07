import tkinter as tk


class FrameNames:
    HOMEFRAME = "home"
    CREATE_MODEL = "create_model"
    POPULATE_MODEL = "populate_model"
    COPY_FLOWLINE_DATA = "copy_flowline_data"
    RUN_SIMULATION = "run_simulation"
    SUMMARIZE = "summarize"
    MULTI_CASE = "multi_case"


FRAME_STORE: dict[str, tk.Frame] = {}

from .copy_flowline_data import init_update_conditions_frame
from .create_model import CreateModelFrame
from .home import HomeFrame
from .multi_case import init_multi_case_frame
from .populate_model import PopulateModelFrame
from .run_simulation import RunSimulationFrame
from .summarize import init_summarize_frame
