#excel_handling.py
import os
import logging
import traceback
import pandas as pd
import xlwings as xw

class ExcelHandler:
    def __init__(self, folder_directory, excel_filename) -> None:
        self.excel_filename = excel_filename
        self.excel_path = f"{folder_directory}\\{excel_filename}"

    def write_excel(
        self,
        df,
        sheet_name,
        range="B1",
        clear_sheet=False,
    ):
        wb = xw.Book(self.excel_path)
        if sheet_name not in [sheet.name for sheet in wb.sheets]:
            wb.sheets.add(sheet_name)
        ws = wb.sheets(sheet_name)
        if clear_sheet:
            ws.clear_contents()
        ws.range(range).value = df

    def get_all_condition(self):
        conditions = pd.read_excel(
            self.excel_path,
            sheet_name="Conditions",
            header=1,
            index_col=0,
            usecols="A:E",
        )
        return conditions

    def get_all_profiles(self):
        profiles = pd.read_excel(
            self.excel_path, sheet_name="PIPSIM Input", header=3, index_col=0
        )
        return profiles

    # cut and paste the worksheet ending with "_NR" and "_PR" a new excel file
    def move_sheets_to_new_excel(self, new_excel_path):
        pass
