import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from app.core.multi_case_modeller import copy_flowline_data
from app.project import FRAME_STORE, FrameNames, browse_folder_or_file

logger_uc = logging.getLogger("app.core.simulation_modeller")


def submit_copy_flowline_data(
    source_file: str, destination_folder: str, progress_bar: ttk.Progressbar
):
    """Copy the flowline information from the source file to all the files in the destination folder."""

    def task():
        progress_bar.pack(pady=10)
        logger_uc.info("Copying flowline conditions")
        progress_bar.start()

        copy_flowline_data(source_file, destination_folder)

        progress_bar.stop()
        progress_bar.pack_forget()
        logger_uc.info("Flowline conditions copied successfully")
        messagebox.showinfo("Success", "Flowline conditions copied successfully")

    threading.Thread(target=task).start()


def init_update_conditions_frame(app: tk.Tk) -> tk.Frame:
    update_conditions_frame = tk.Frame(app)
    FRAME_STORE[FrameNames.COPY_FLOWLINE_DATA] = update_conditions_frame
    update_label = tk.Label(
        update_conditions_frame, text="Copy Flowline Data Workflow", font=("Arial", 14)
    )
    update_label.pack(pady=10)

    # Help label
    help_text = """ This workflow copies the flowline data from a source model to all the models in a folder.
    Only Python Toolkit license is required for this workflow."""

    help_label_uc = tk.Label(
        update_conditions_frame,
        text=help_text,
        font=("Arial", 10, "italic"),
    )
    help_label_uc.pack(pady=5)

    # Source model
    uc_pipesim_frame = tk.Frame(update_conditions_frame)
    uc_pipesim_frame.pack(pady=5)
    source_label_uc = tk.Label(uc_pipesim_frame, text="Source Model")
    source_label_uc.pack()
    source_file_entry_uc = tk.Entry(uc_pipesim_frame, width=75, state="readonly")
    source_file_entry_uc.pack(side=tk.LEFT)
    source_browse_button_uc = tk.Button(
        uc_pipesim_frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            source_file_entry_uc,
            file_types=[("Pipesim files", "*.pips")],
            title="Select a source model",
        ),
    )
    source_browse_button_uc.pack(side=tk.LEFT, padx=5)

    # Destination folder
    uc_folder_frame = tk.Frame(update_conditions_frame)
    uc_folder_frame.pack(pady=5)
    folder_label_uc = tk.Label(uc_folder_frame, text="Destination Folder")
    folder_label_uc.pack()
    folder_entry_uc = tk.Entry(uc_folder_frame, width=75, state="readonly")
    folder_entry_uc.pack(side=tk.LEFT)
    folder_browse_button_uc = tk.Button(
        uc_folder_frame,
        text="Browse",
        command=lambda: browse_folder_or_file(
            folder_entry_uc, title="Select a folder", select_folder=True
        ),
    )
    folder_browse_button_uc.pack(side=tk.LEFT, padx=5)

    # Progress bar
    progress_bar = ttk.Progressbar(update_conditions_frame, mode="indeterminate")

    # Submit button
    submit_button_uc = tk.Button(
        update_conditions_frame,
        text="Copy Data",
        command=lambda: submit_copy_flowline_data(
            source_file_entry_uc.get(), folder_entry_uc.get(), progress_bar
        ),
    )
    submit_button_uc.pack(pady=10)

    return update_conditions_frame
