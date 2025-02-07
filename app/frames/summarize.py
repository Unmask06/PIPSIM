import logging
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from app.frames import FRAME_STORE, FrameNames

logger_sm = logging.getLogger("SummarizeLogger")


def summarize(progress_bar):
    def task():
        progress_bar.pack(pady=10)
        logger_sm.info("Summarizing data")
        progress_bar.start()

        # Simulate summarizing data
        import time

        time.sleep(5)

        progress_bar.stop()
        progress_bar.pack_forget()
        messagebox.showwarning(
            "Wait", "Data summarization feature is not available yet"
        )
        # messagebox.showinfo("Success", "Data summarized successfully")

    threading.Thread(target=task).start()


def init_summarize_frame(app):
    summarize_frame = tk.Frame(app)
    FRAME_STORE[FrameNames.SUMMARIZE] = summarize_frame
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

    progress_bar = ttk.Progressbar(summarize_frame, mode="indeterminate")

    submit_button_sm = tk.Button(
        summarize_frame, text="Submit", command=lambda: summarize(progress_bar)
    )
    submit_button_sm.pack(pady=10)
    return summarize_frame
