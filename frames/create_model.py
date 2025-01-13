import logging
import tkinter as tk
from tkinter import filedialog

from project import FRAME_STORE, TextHandler, add_logger_area, switch_frame


def submit_create_model(logger_cm: logging.Logger):
    logger_cm.info("Create Model Workflow submitted")


def init_create_model_frame(app: tk.Tk, home_frame: tk.Frame) -> tk.Frame:
    create_model_frame = tk.Frame(app)
    FRAME_STORE["create_model"] = create_model_frame
    create_label = tk.Label(
        create_model_frame, text="Create Model Workflow", font=("Arial", 14)
    )
    create_label.pack(pady=10)
    config_label_cm = tk.Label(create_model_frame, text="Configuration File")
    config_label_cm.pack()
    config_file_entry_cm = tk.Entry(create_model_frame, width=50)
    config_file_entry_cm.pack()
    config_browse_button_cm = tk.Button(
        create_model_frame, text="Browse", command=lambda: filedialog.askopenfilename()
    )
    config_browse_button_cm.pack(pady=5)
    submit_button_cm = tk.Button(
        create_model_frame,
        text="Submit",
        command=lambda: submit_create_model(logger_cm),
    )
    submit_button_cm.pack(pady=10)
    log_text_cm = add_logger_area(create_model_frame)
    back_button_cm = tk.Button(
        create_model_frame,
        text="Back to Home",
        command=lambda: switch_frame(home_frame),
    )
    back_button_cm.pack(pady=10)
    logger_cm = logging.getLogger("CreateModelLogger")
    logger_cm.setLevel(logging.INFO)
    logger_cm.addHandler(TextHandler(log_text_cm))

    return create_model_frame
