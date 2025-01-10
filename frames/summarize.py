from project import TextHandler, add_logger_area, frame_store, switch_frame
import logging
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


def summarize(logger):
    logger.info("Summarizing data")

def init_summarize_frame(app, home_frame):
    summarize_frame = tk.Frame(app)
    frame_store["summarize"] = summarize_frame
    summarize_label = tk.Label(
        summarize_frame, text="Summarize Data", font=("Arial", 14)
    )
    summarize_label.pack(pady=10)

    input_label_sm = tk.Label(
        summarize_frame, text="Folder containing data files"
    )
    input_label_sm.pack()
    config_file_entry_sm = tk.Entry(summarize_frame, width=50, state="readonly")
    config_file_entry_sm.pack()
    config_browse_button_sm = tk.Button(
        summarize_frame,
        text="Browse",
        command=lambda: filedialog.askopenfilename(),
    )
    config_browse_button_sm.pack(pady=5)
    submit_button_sm = tk.Button(
        summarize_frame, text="Submit", command=lambda: summarize(logger_sm)
    )
    submit_button_sm.pack(pady=10)
    log_text_sm = add_logger_area(summarize_frame)
    back_button_sm = tk.Button(
        summarize_frame,
        text="Back to Home",
        command=lambda: switch_frame(home_frame),
    )
    back_button_sm.pack(pady=10)
    logger_sm = logging.getLogger("SummarizeLogger")
    logger_sm.setLevel(logging.INFO)
    logger_sm.addHandler(TextHandler(log_text_sm))
    return summarize_frame