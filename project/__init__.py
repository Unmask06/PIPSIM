import tkinter as tk
from tkinter import scrolledtext
import logging

frame_store: dict[str, tk.Frame] = {}


def switch_frame(new_frame: tk.Frame):
    for frame in frame_store.values():
        frame.pack_forget()
    new_frame.pack(fill="both", expand=True)


class TextHandler(logging.Handler):
    """This class redirects logging messages to the specified ScrolledText widget."""

    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.configure(state="normal")
        self.text_widget.insert(tk.END, msg + "\n")
        self.text_widget.configure(state="disabled")
        self.text_widget.yview(tk.END)


def add_logger_area(parent_frame):
    logger_frame = tk.Frame(parent_frame)
    logger_frame.pack(fill="both", expand=True, pady=10)
    log_text = scrolledtext.ScrolledText(logger_frame, height=10, state="disabled")
    log_text.pack(fill="both", expand=True)
    return log_text
