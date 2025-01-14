import logging
import tkinter as tk
from tkinter import filedialog, messagebox

from project import FRAME_STORE, TextHandler


def summarize(logger):
    logger.info("Summarizing data")


def init_summarize_frame(app, master_log_text: tk.Text):
    summarize_frame = tk.Frame(app)
    FRAME_STORE["summarize"] = summarize_frame
    summarize_label = tk.Label(
        summarize_frame, text="Summarize Data", font=("Arial", 14)
    )
    summarize_label.pack(pady=10)

    input_label_sm = tk.Label(summarize_frame, text="Folder containing data files")
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
    logger_sm = logging.getLogger("SummarizeLogger")
    logger_sm.setLevel(logging.INFO)
    logger_sm.addHandler(TextHandler(master_log_text))
    return summarize_frame
