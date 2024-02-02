# excel_handling.py
import logging
import os
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
        range="A2",
        clear_sheet=False,
        workbook=None,
    ):
        try:
            with xw.App(visible=False) as app:
                if workbook is None:
                    wb = xw.Book(self.excel_path)
                else:
                    if os.path.isfile(workbook):
                        wb = xw.Book(workbook)
                    else:
                        wb = xw.Book()
                        wb.save(workbook)
                if sheet_name not in [sheet.name for sheet in wb.sheets]:
                    wb.sheets.add(sheet_name)
                ws = wb.sheets(sheet_name)
                if clear_sheet:
                    ws.clear_contents()
                ws.range(range).value = df
                ws.range("A2:I2").api.Font.Bold = True
                ws.range("A2:I2").api.EntireColumn.AutoFit()
                ws.range("C4").api.CurrentRegion.NumberFormat = "0.0"
                ws.range("B1").value = ws.name
                ws.range("B1").api.Font.Bold = True
                wb.save()
        except Exception as e:
            logging.error(f"Error writing to Excel: {str(e)}")

    def get_all_condition(self, sheet_name="Conditions"):
        conditions = pd.read_excel(
            self.excel_path,
            sheet_name=sheet_name,
            header=1,
            index_col=0,
            usecols="A:E",
        )
        return conditions

    def get_all_profiles(self, sheet_name="PIPSIM Input"):
        profiles = pd.read_excel(
            self.excel_path, sheet_name=sheet_name, header=3, index_col=0
        )
        return profiles