import logging
import logging.config
import tkinter as tk
from tkinter import filedialog

import yaml

FRAME_STORE: dict[str, tk.Frame] = {}


def switch_frame(new_frame: tk.Frame):
    for frame in FRAME_STORE.values():
        frame.pack_forget()
    new_frame.pack(fill="both", expand=True)


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


def setup_logger():
    with open("logging.yml", "r") as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
