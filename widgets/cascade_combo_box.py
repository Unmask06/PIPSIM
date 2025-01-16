import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from sixgill.definitions import Parameters


class DualCascadeListBox(tk.Toplevel):
    """
    Displays two listboxes with respective search bars.
    Selecting an item in the parent list updates the child list.
    """

    def __init__(
        self,
        parent: tk.Tk,
        title: str,
        child_mapping: Dict[str, List[str]],
    ):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x300")
        self.parent_list = child_mapping.keys()
        self.child_mapping = child_mapping

        self.filtered_parents = self.parent_list
        self.filtered_children: List[str] = []

        self.parent_search_var = tk.StringVar()
        self.child_search_var = tk.StringVar()

        # Make the frame's grid cells expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.grab_set()

    def build_ui(self):
        # Parent List UI
        parent_frame = ttk.Frame(self)
        parent_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        parent_search_entry = ttk.Entry(
            parent_frame, textvariable=self.parent_search_var
        )
        parent_search_entry.pack(fill=tk.X)
        parent_search_entry.bind("<KeyRelease>", self.filter_parent_list)

        self.parent_listbox = tk.Listbox(parent_frame)
        self.parent_listbox.pack(fill=tk.BOTH, expand=True)
        self.parent_listbox.bind("<<ListboxSelect>>", self.update_child_list)

        parent_scrollbar = ttk.Scrollbar(
            self.parent_listbox, command=self.parent_listbox.yview
        )
        self.parent_listbox.configure(yscrollcommand=parent_scrollbar.set)
        parent_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Child List UI
        child_frame = ttk.Frame(self)
        child_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        child_search_entry = ttk.Entry(child_frame, textvariable=self.child_search_var)
        child_search_entry.pack(fill=tk.X)
        child_search_entry.bind("<KeyRelease>", self.filter_child_list)

        self.child_listbox = tk.Listbox(child_frame)
        self.child_listbox.pack(fill=tk.BOTH, expand=True)

        child_scrollbar = ttk.Scrollbar(
            self.child_listbox, command=self.child_listbox.yview
        )
        self.child_listbox.configure(yscrollcommand=child_scrollbar.set)
        child_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.create_context_menu_for_listbox(
            self.parent_listbox, self.copy_parent_selection
        )
        self.create_context_menu_for_listbox(
            self.child_listbox, self.copy_child_selection
        )
        self.parent_listbox.bind("<Control-c>", lambda e: self.copy_parent_selection())
        self.child_listbox.bind("<Control-c>", lambda e: self.copy_child_selection())

        self.populate_parent_list()

    def create_context_menu_for_listbox(self, listbox, copy_method):
        menu = tk.Menu(listbox, tearoff=0)
        menu.add_command(label="Copy", command=copy_method)

        def show_menu(event):
            menu.tk_popup(event.x_root, event.y_root)

        listbox.bind("<Button-3>", show_menu)

    def populate_parent_list(self):
        self.parent_listbox.delete(0, tk.END)
        for item in self.filtered_parents:
            self.parent_listbox.insert(tk.END, item)

    def populate_child_list(self):
        self.child_listbox.delete(0, tk.END)
        for item in self.filtered_children:
            self.child_listbox.insert(tk.END, item)

    def filter_parent_list(self, event=None):
        search_term = self.parent_search_var.get().lower()
        self.filtered_parents = [
            p for p in self.parent_list if search_term in p.lower()
        ]
        self.populate_parent_list()

    def filter_child_list(self, event=None):
        search_term = self.child_search_var.get().lower()
        displayed_children = [
            c for c in self.filtered_children if search_term in c.lower()
        ]
        self.child_listbox.delete(0, tk.END)
        for item in displayed_children:
            self.child_listbox.insert(tk.END, item)

    def update_child_list(self, event=None):
        selection = self.parent_listbox.curselection()
        if selection:
            parent_choice = self.parent_listbox.get(selection[0])
            self.filtered_children = self.child_mapping.get(parent_choice, [])
            self.child_search_var.set("")
            self.populate_child_list()

    def copy_parent_selection(self):
        selection = self.parent_listbox.curselection()
        if selection:
            self.clipboard_clear()
            self.clipboard_append(self.parent_listbox.get(selection[0]))

    def copy_child_selection(self):
        selection = self.child_listbox.curselection()
        if selection:
            self.clipboard_clear()
            self.clipboard_append(self.child_listbox.get(selection[0]))

    def close_window(self):
        self.destroy()
