import tkinter as tk
from tkinter import ttk
from typing import Any, List


class CheckableCombobox(tk.Toplevel):
    """Custom Combo Box with Available and Selected lists, Add/Remove functionality, Searchbox, and ordering."""

    def __init__(self, parent: tk.Tk, title: str, values: List[str]) -> None:
        super().__init__(parent)
        self.title(title)
        self.values: List[str] = values
        self.selected_values: List[str] = []  # List to maintain order

        # Create the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Available variables label and search bar
        available_label = ttk.Label(self.main_frame, text="Available Variables")
        available_label.grid(row=0, column=0)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.main_frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
        self.search_var.trace_add("write", self.update_available_list)

        # Available listbox
        self.available_listbox = tk.Listbox(
            self.main_frame, selectmode=tk.SINGLE, height=10
        )
        self.available_listbox.grid(row=2, column=0, padx=5, pady=5)
        self.available_listbox.bind("<Double-1>", self.add_to_selected_double_click)

        # Populate available listbox
        self.filtered_values: List[str] = list(
            self.values
        )  # Keep a filtered list for searching
        self.update_available_list()

        # Buttons to move items
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.grid(row=2, column=1)

        self.add_button = ttk.Button(
            self.button_frame, text="→", command=self.add_to_selected
        )
        self.add_button.pack(pady=5)

        self.remove_button = ttk.Button(
            self.button_frame, text="←", command=self.remove_from_selected
        )
        self.remove_button.pack(pady=5)

        # Selected variables label and listbox
        selected_label = ttk.Label(self.main_frame, text="Selected Variables")
        selected_label.grid(row=0, column=2)

        self.selected_listbox = tk.Listbox(
            self.main_frame, selectmode=tk.SINGLE, height=10
        )
        self.selected_listbox.grid(row=2, column=2, padx=5, pady=5)

        # Buttons for ordering selected items
        self.order_button_frame = ttk.Frame(self.main_frame)
        self.order_button_frame.grid(row=2, column=3)

        self.up_button = ttk.Button(
            self.order_button_frame, text="↑", command=self.move_selected_up
        )
        self.up_button.pack(pady=5)

        self.down_button = ttk.Button(
            self.order_button_frame, text="↓", command=self.move_selected_down
        )
        self.down_button.pack(pady=5)

        # Add a confirm button
        self.confirm_button = ttk.Button(
            self, text="Confirm", command=self.confirm_selection
        )
        self.confirm_button.pack(pady=10)

    def update_available_list(self, *args: Any) -> None:
        """Update available listbox based on search entry."""
        search_term = self.search_var.get().lower()
        self.available_listbox.delete(0, tk.END)
        for val in self.values:
            if search_term in val.lower():
                self.available_listbox.insert(tk.END, val)

    def add_to_selected(self) -> None:
        """Move selected items from Available to Selected."""
        selected_index = self.available_listbox.curselection()
        if selected_index:
            value = self.available_listbox.get(selected_index)
            if value not in self.selected_values:
                self.selected_values.append(value)
                self.selected_listbox.insert(tk.END, value)
                self.available_listbox.delete(selected_index)

    def add_to_selected_double_click(self, event: tk.Event) -> None:
        """Add to selected listbox on double-click."""
        self.add_to_selected()

    def remove_from_selected(self) -> None:
        """Move selected items from Selected to Available."""
        selected_index = self.selected_listbox.curselection()
        if selected_index:
            value = self.selected_listbox.get(selected_index)
            if value in self.selected_values:
                self.selected_values.remove(value)
                self.selected_listbox.delete(selected_index)
                self.available_listbox.insert(
                    0, value
                )  # Insert at the top for better user experience

    def move_selected_up(self) -> None:
        """Move the selected item up in the order."""
        selected_index = self.selected_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            idx = selected_index[0]
            self.selected_values[idx], self.selected_values[idx - 1] = (
                self.selected_values[idx - 1],
                self.selected_values[idx],
            )
            self.update_selected_listbox(idx - 1)

    def move_selected_down(self) -> None:
        """Move the selected item down in the order."""
        selected_index = self.selected_listbox.curselection()
        if selected_index and selected_index[0] < len(self.selected_values) - 1:
            idx = selected_index[0]
            self.selected_values[idx], self.selected_values[idx + 1] = (
                self.selected_values[idx + 1],
                self.selected_values[idx],
            )
            self.update_selected_listbox(idx + 1)

    def update_selected_listbox(self, highlight_index: int) -> None:
        """Update the selected listbox with the current order and highlight an item."""
        self.selected_listbox.delete(0, tk.END)
        for val in self.selected_values:
            self.selected_listbox.insert(tk.END, val)
        self.selected_listbox.select_set(highlight_index)
        self.selected_listbox.see(
            highlight_index
        )  # Ensure the highlighted item is visible

    def confirm_selection(self) -> None:
        """Confirm the selected items."""
        final_selection: List[str] = self.selected_values
        print(f"Final Selected Variables: {final_selection}")
        self.destroy()
