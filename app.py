import logging
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext


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


def dummy_function(logger):
    logger.info("Executing dummy function...")
    messagebox.showinfo("Info", "This is a dummy function.")
    logger.info("Dummy function completed.")


def switch_frame(new_frame):
    for frame in frames.values():
        frame.pack_forget()
    new_frame.pack(fill="both", expand=True)


def add_logger_area(parent_frame):
    logger_frame = tk.Frame(parent_frame)
    logger_frame.pack(fill="both", expand=True, pady=10)
    log_text = scrolledtext.ScrolledText(logger_frame, height=10, state="disabled")
    log_text.pack(fill="both", expand=True)
    return log_text


def show_help():
    try:
        help_window = tk.Toplevel(app)
        help_window.title("Help")
        help_window.geometry("600x400")

        help_label = tk.Label(
            help_window, text="Help Documentation", font=("Arial", 16)
        )
        help_label.pack(pady=10)

        # Fallback: Use ScrolledText if HtmlFrame fails
        help_text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text.pack(fill="both", expand=True)

        with open("help.txt", "r", encoding="utf-8") as f:
            markdown_text = f.read()
            # Convert markdown to plain text as a fallback
            help_text.insert(tk.END, markdown_text)
            help_text.configure(state="disabled")

    except FileNotFoundError:
        messagebox.showerror("Error", "The help file 'help.md' was not found.")
    except Exception as e:
        messagebox.showerror("Error", f"An unexpected error occurred: {e}")


# Tkinter GUI setup
app = tk.Tk()
app.title("PANDORA - Pipesim Pilot")
app.geometry("600x400")

menu_bar = tk.Menu(app)
help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="Help", command=show_help)
menu_bar.add_cascade(label="Help", menu=help_menu)
app.config(menu=menu_bar)

frames = {}

# Home Frame
home_frame = tk.Frame(app)
frames["home"] = home_frame

home_label = tk.Label(
    home_frame, text="Welcome to PANDORA's Pipesim Pilot", font=("Arial", 16)
)
home_label.pack(pady=20)

create_model_button = tk.Button(
    home_frame,
    text="Create Model Workflow",
    command=lambda: switch_frame(frames["create_model"]),
    width=30,
)
create_model_button.pack(pady=5)

update_conditions_button = tk.Button(
    home_frame,
    text="Update Conditions Workflow",
    command=lambda: switch_frame(frames["update_conditions"]),
    width=30,
)
update_conditions_button.pack(pady=5)

run_simulation_button = tk.Button(
    home_frame,
    text="Run Simulation Workflow",
    command=lambda: switch_frame(frames["run_simulation"]),
    width=30,
)
run_simulation_button.pack(pady=5)

summarize_results_button = tk.Button(
    home_frame,
    text="Summarize Results Workflow",
    command=lambda: switch_frame(frames["summarize_results"]),
    width=30,
)
summarize_results_button.pack(pady=5)

exit_button = tk.Button(home_frame, text="Exit", command=app.quit, width=30)
exit_button.pack(pady=10)

# Create Model Frame
create_model_frame = tk.Frame(app)
frames["create_model"] = create_model_frame
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
    create_model_frame, text="Submit", command=lambda: dummy_function(logger_cm)
)
submit_button_cm.pack(pady=10)
log_text_cm = add_logger_area(create_model_frame)
back_button_cm = tk.Button(
    create_model_frame, text="Back to Home", command=lambda: switch_frame(home_frame)
)
back_button_cm.pack(pady=10)
logger_cm = logging.getLogger("CreateModelLogger")
logger_cm.setLevel(logging.INFO)
logger_cm.addHandler(TextHandler(log_text_cm))

# Update Conditions Frame
update_conditions_frame = tk.Frame(app)
frames["update_conditions"] = update_conditions_frame
update_label = tk.Label(
    update_conditions_frame, text="Update Conditions Workflow", font=("Arial", 14)
)
update_label.pack(pady=10)
config_label_uc = tk.Label(update_conditions_frame, text="Configuration File")
config_label_uc.pack()
config_file_entry_uc = tk.Entry(update_conditions_frame, width=50)
config_file_entry_uc.pack()
config_browse_button_uc = tk.Button(
    update_conditions_frame, text="Browse", command=lambda: filedialog.askopenfilename()
)
config_browse_button_uc.pack(pady=5)
submit_button_uc = tk.Button(
    update_conditions_frame, text="Submit", command=lambda: dummy_function(logger_uc)
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

# Run Simulation Frame
run_simulation_frame = tk.Frame(app)
frames["run_simulation"] = run_simulation_frame
run_label = tk.Label(
    run_simulation_frame, text="Run Simulation Workflow", font=("Arial", 14)
)
run_label.pack(pady=10)
config_label_rs = tk.Label(run_simulation_frame, text="Configuration File")
config_label_rs.pack()
config_file_entry_rs = tk.Entry(run_simulation_frame, width=50)
config_file_entry_rs.pack()
config_browse_button_rs = tk.Button(
    run_simulation_frame, text="Browse", command=lambda: filedialog.askopenfilename()
)
config_browse_button_rs.pack(pady=5)
submit_button_rs = tk.Button(
    run_simulation_frame, text="Submit", command=lambda: dummy_function(logger_rs)
)
submit_button_rs.pack(pady=10)
log_text_rs = add_logger_area(run_simulation_frame)
back_button_rs = tk.Button(
    run_simulation_frame, text="Back to Home", command=lambda: switch_frame(home_frame)
)
back_button_rs.pack(pady=10)
logger_rs = logging.getLogger("RunSimulationLogger")
logger_rs.setLevel(logging.INFO)
logger_rs.addHandler(TextHandler(log_text_rs))

# Summarize Results Frame
summarize_results_frame = tk.Frame(app)
frames["summarize_results"] = summarize_results_frame
summary_label = tk.Label(
    summarize_results_frame, text="Summarize Results Workflow", font=("Arial", 14)
)
summary_label.pack(pady=10)
config_label_sr = tk.Label(summarize_results_frame, text="Configuration File")
config_label_sr.pack()
config_file_entry_sr = tk.Entry(summarize_results_frame, width=50)
config_file_entry_sr.pack()
config_browse_button_sr = tk.Button(
    summarize_results_frame, text="Browse", command=lambda: filedialog.askopenfilename()
)
config_browse_button_sr.pack(pady=5)
submit_button_sr = tk.Button(
    summarize_results_frame, text="Submit", command=lambda: dummy_function(logger_sr)
)
submit_button_sr.pack(pady=10)
log_text_sr = add_logger_area(summarize_results_frame)
back_button_sr = tk.Button(
    summarize_results_frame,
    text="Back to Home",
    command=lambda: switch_frame(home_frame),
)
back_button_sr.pack(pady=10)
logger_sr = logging.getLogger("SummarizeResultsLogger")
logger_sr.setLevel(logging.INFO)
logger_sr.addHandler(TextHandler(log_text_sr))

# Start with the home frame
switch_frame(home_frame)

app.mainloop()
