import logging
import logging.config
import tkinter as tk
from tkinter import filedialog, scrolledtext

import yaml

FRAME_STORE: dict[str, tk.Frame] = {}


def switch_frame(new_frame: tk.Frame):
    for frame in FRAME_STORE.values():
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


def browse_folder_or_file(
    entry_widget: tk.Entry,
    file_types: list[tuple[str, str]] | None = None,
    title: str = "Select a file or folder",
    select_folder: bool = False,
) -> str:
    path = (
        filedialog.askdirectory(title=title)
        if select_folder
        else filedialog.askopenfilename(
            filetypes=file_types or [("All Files", "*.*")], title=title
        )
    )
    if path:
        entry_widget.config(state="normal")
        entry_widget.delete(0, tk.END)
        entry_widget.insert(0, path)
        entry_widget.config(state="readonly")
    return path


def add_handler_to_all_loggers(text_widget):
    logger_dict = logging.Logger.manager.loggerDict
    print(logger_dict.keys())
    for logger in logger_dict.values():
        if isinstance(logger, logging.Logger):
            logger.addHandler(TextHandler(text_widget))
    logging.getLogger().setLevel(logging.INFO)


def setup_logger():
    with open("logging.yml", "r") as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
