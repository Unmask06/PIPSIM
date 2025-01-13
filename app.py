import sys
import tkinter as tk
from tkinter import messagebox, scrolledtext

from frames import (
    init_create_model_frame,
    init_home_frame,
    init_run_simulation_frame,
    init_summarize_frame,
    init_update_conditions_frame,
)
from project import FRAME_STORE, switch_frame


def show_menu(app: tk.Tk):
    menu_bar = tk.Menu(app)

    # File menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    file_menu.add_command(
        label="Home", command=lambda: switch_frame(FRAME_STORE["home"])
    )
    file_menu.add_separator()
    file_menu.add_command(label="Exit", command=lambda: sys.exit(0))
    menu_bar.add_cascade(label="File", menu=file_menu)
    app.config(menu=menu_bar)

    # Help menu
    help_menu = tk.Menu(menu_bar, tearoff=0)
    help_menu.add_command(label="Help", command=lambda: show_help(app))
    menu_bar.add_cascade(label="Help", menu=help_menu)
    app.config(menu=menu_bar)


def show_help(app: tk.Tk):
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


def main():

    # Tkinter GUI setup
    app = tk.Tk()
    app.title("PANDORA - Pipesim Pilot")
    app.geometry("600x400")

    show_menu(app)

    # Initialize frames
    home_frame = init_home_frame(app)
    init_create_model_frame(app)
    init_update_conditions_frame(app)
    init_run_simulation_frame(app)
    init_summarize_frame(app)

    # Start with the home frame
    switch_frame(home_frame)

    app.mainloop()


if __name__ == "__main__":
    main()
