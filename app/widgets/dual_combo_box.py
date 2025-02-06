import tkinter as tk
from tkinter import ttk
from typing import Any, List, Optional


class DualSelectableCombobox(tk.Toplevel):
    """Custom Combo Box with optional single or dual lists, Add/Remove functionality, Searchbox, and ordering."""

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        available_variables: List[str],
        selected_variables: Optional[List[str]] = None,
        mode: str = "dual",
    ) -> None:
        super().__init__(parent)
        self.title(title)
        self.geometry("800x400")  # Increase the size of the window
        self.available_variables: List[str] = available_variables
        self.selected_values: List[str] = selected_variables or []
        self.mode: str = mode  # Mode can be 'single' or 'dual'

        # Create the main frame
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Make the frame's grid cells expandable
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        if self.mode == "dual":
            self.main_frame.grid_columnconfigure(2, weight=1)

        # Available variables label and search bar
        available_label = ttk.Label(self.main_frame, text="Available Variables")
        available_label.grid(row=0, column=0)

        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(self.main_frame, textvariable=self.search_var)
        self.search_entry.grid(row=1, column=0, padx=5, pady=(0, 5), sticky="ew")
        self.search_var.trace_add("write", self.update_available_list)

        # Available listbox
        self.available_listbox = tk.Listbox(
            self.main_frame,
            selectmode=tk.SINGLE,
            height=15,
            width=40,  # Adjusted to match selected box width
        )
        # Enable right-click copy
        self.available_listbox.bind("<Button-3>", self.show_context_menu)
        self.available_context_menu = tk.Menu(self.available_listbox, tearoff=0)
        self.available_context_menu.add_command(
            label="Copy", command=self.copy_selected_item
        )

        # Expand the listbox in both directions
        self.available_listbox.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.available_listbox.bind("<Double-1>", self.add_to_selected_double_click)

        # Populate available listbox
        self.filtered_values: List[str] = list(
            self.available_variables
        )  # Keep a filtered list for searching
        self.update_available_list()

        if self.mode == "dual":
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
                self.main_frame,
                selectmode=tk.SINGLE,
                height=15,
                width=40,  # Same width as available box for uniformity
            )
            # Enable right-click copy for selected listbox
            self.selected_listbox.bind("<Button-3>", self.show_context_menu_selected)
            self.selected_context_menu = tk.Menu(self.selected_listbox, tearoff=0)
            self.selected_context_menu.add_command(
                label="Copy", command=self.copy_selected_item_selected
            )

            # Expand the listbox in both directions
            self.selected_listbox.grid(row=2, column=2, padx=5, pady=5, sticky="nsew")

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
        self.update()

    def update(self) -> None:
        """Ensure the list boxes contain the correct values."""
        self.available_listbox.delete(0, tk.END)
        for val in self.available_variables:
            if val not in self.selected_values:
                self.available_listbox.insert(tk.END, val)

        if self.mode == "dual":
            self.selected_listbox.delete(0, tk.END)
            for val in self.selected_values:
                self.selected_listbox.insert(tk.END, val)

    def update_available_list(self, *args: Any) -> None:
        """Update available listbox based on search entry."""
        search_term = self.search_var.get().lower()
        self.available_listbox.delete(0, tk.END)
        for val in self.available_variables:
            if search_term in val.lower():
                self.available_listbox.insert(tk.END, val)

    def add_to_selected(self) -> None:
        """Move selected items from Available to Selected."""
        if self.mode == "single":
            return
        selected_index = self.available_listbox.curselection()
        if selected_index:
            value = self.available_listbox.get(selected_index)
            if value not in self.selected_values:
                self.selected_values.append(value)
                self.update()

    def add_to_selected_double_click(self, event: tk.Event) -> None:
        """Add to selected listbox on double-click."""
        if self.mode == "dual":
            self.add_to_selected()

    def remove_from_selected(self) -> None:
        """Move selected items from Selected to Available."""
        if self.mode == "single":
            return
        selected_index = self.selected_listbox.curselection()
        if selected_index:
            value = self.selected_listbox.get(selected_index)
            if value in self.selected_values:
                self.selected_values.remove(value)
                self.update()

    def move_selected_up(self) -> None:
        """Move the selected item up in the order."""
        if self.mode == "single":
            return
        selected_index = self.selected_listbox.curselection()
        if selected_index and selected_index[0] > 0:
            idx = selected_index[0]
            self.selected_values[idx], self.selected_values[idx - 1] = (
                self.selected_values[idx - 1],
                self.selected_values[idx],
            )
            self.update()
            self.selected_listbox.select_set(idx - 1)
            self.selected_listbox.see(idx - 1)

    def move_selected_down(self) -> None:
        """Move the selected item down in the order."""
        if self.mode == "single":
            return
        selected_index = self.selected_listbox.curselection()
        if selected_index and selected_index[0] < len(self.selected_values) - 1:
            idx = selected_index[0]
            self.selected_values[idx], self.selected_values[idx + 1] = (
                self.selected_values[idx + 1],
                self.selected_values[idx],
            )
            self.update()
            self.selected_listbox.select_set(idx + 1)
            self.selected_listbox.see(idx + 1)

    def update_selected_listbox(self, highlight_index: int) -> None:
        """Update the selected listbox with the current order and highlight an item."""
        self.update()
        self.selected_listbox.select_set(highlight_index)
        self.selected_listbox.see(
            highlight_index
        )  # Ensure the highlighted item is visible

    def confirm_selection(self) -> List[str]:
        """Return the selected values and destroy the window"""
        self.destroy()
        return self.selected_values

    def show_context_menu(self, event: tk.Event) -> None:
        """Show the right-click context menu for available listbox."""
        try:
            self.available_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.available_context_menu.grab_release()

    def copy_selected_item(self) -> None:
        """Copy selected item from available listbox to clipboard."""
        selected_index = self.available_listbox.curselection()
        if selected_index:
            value = self.available_listbox.get(selected_index)
            self.clipboard_clear()
            self.clipboard_append(value)

    def show_context_menu_selected(self, event: tk.Event) -> None:
        """Show the right-click context menu for selected listbox."""
        if self.mode == "single":
            return
        try:
            self.selected_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.selected_context_menu.grab_release()

    def copy_selected_item_selected(self) -> None:
        """Copy selected item from selected listbox to clipboard."""
        selected_index = self.selected_listbox.curselection()
        if selected_index:
            value = self.selected_listbox.get(selected_index)
            self.clipboard_clear()
            self.clipboard_append(value)
