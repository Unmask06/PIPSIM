import tkinter as tk
from tkinter import ttk
from typing import List, Dict


class DualCascadeComboBox(tk.Frame):
    def __init__(self, parent, parent_list: List[str], child_mapping: Dict[str, List[str]], *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent_list = parent_list
        self.child_mapping = child_mapping

        self.parent_var = tk.StringVar()
        self.child_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        parent_label = ttk.Label(self, text="Parent List")
        parent_label.grid(row=0, column=0, padx=5, pady=5)

        self.parent_combo = ttk.Combobox(self, textvariable=self.parent_var, values=self.parent_list)
        self.parent_combo.grid(row=1, column=0, padx=5, pady=5)
        self.parent_combo.bind("<<ComboboxSelected>>", self.update_child_list)

        child_label = ttk.Label(self, text="Child List")
        child_label.grid(row=0, column=1, padx=5, pady=5)

        self.child_combo = ttk.Combobox(self, textvariable=self.child_var)
        self.child_combo.grid(row=1, column=1, padx=5, pady=5)

    def update_child_list(self, event):
        selected_parent = self.parent_var.get()
        child_values = self.child_mapping.get(selected_parent, [])
        self.child_combo['values'] = child_values
        if child_values:
            self.child_var.set(child_values[0])
        else:
            self.child_var.set("")


if __name__ == "__main__":
    root = tk.Tk()
    parent_list = ["Flowline", "Pump"]
    child_mapping = {
        "Flowline": ["Length", "Diameter", "Material"],
        "Pump": ["Flow Rate", "Head", "Efficiency"]
    }
    dual_cascade_combo = DualCascadeComboBox(root, parent_list, child_mapping)
    dual_cascade_combo.pack(padx=10, pady=10)
    root.mainloop()
