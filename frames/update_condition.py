import logging
import tkinter as tk
from tkinter import filedialog

from project import FRAME_STORE, TextHandler, add_logger_area, switch_frame


def submit_update_conditions(logger_uc: logging.Logger):
    logger_uc.info("Update Conditions Workflow submitted")


def init_update_conditions_frame(app: tk.Tk, home_frame: tk.Frame) -> tk.Frame:
    update_conditions_frame = tk.Frame(app)
    FRAME_STORE["update_conditions"] = update_conditions_frame
    update_label = tk.Label(
        update_conditions_frame, text="Update Conditions Workflow", font=("Arial", 14)
    )
    update_label.pack(pady=10)
    config_label_uc = tk.Label(update_conditions_frame, text="Configuration File")
    config_label_uc.pack()
    config_file_entry_uc = tk.Entry(update_conditions_frame, width=50)
    config_file_entry_uc.pack()
    config_browse_button_uc = tk.Button(
        update_conditions_frame,
        text="Browse",
        command=lambda: filedialog.askopenfilename(),
    )
    config_browse_button_uc.pack(pady=5)
    submit_button_uc = tk.Button(
        update_conditions_frame,
        text="Submit",
        command=lambda: submit_update_conditions(logger_uc),
    )
    submit_button_uc.pack(pady=10)
    log_text_uc = add_logger_area(update_conditions_frame)
    back_button_uc = tk.Button(
        update_conditions_frame,
        text="Back to Home",
        command=lambda: switch_frame(home_frame),
    )
    back_button_uc.pack(pady=10)
    logger_uc = logging.getLogger("UpdateConditionsLogger")
    logger_uc.setLevel(logging.INFO)
    logger_uc.addHandler(TextHandler(log_text_uc))

    return update_conditions_frame
