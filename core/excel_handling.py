# excel_handling.py
import logging
import os
import traceback
from pathlib import Path
from re import A
from typing import Any, Optional

import pandas as pd
import xlwings as xw
from traitlets import Bool
from xlwings import constants as xw_const

logger = logging.getLogger("ExcelHandler")


class ExcelHandler:

    def __init__(
        self, excel_filename: str, folder_directory: Optional[Path] = None
    ) -> None:

        self.excel_filename = excel_filename
        self.excel_path = self._get_excel_path(excel_filename, folder_directory)

    def _get_excel_path(
        self, excel_filename: str, folder_directory: Optional[Path]
    ) -> Path:

        if folder_directory is None:
            folder_directory = Path.cwd()

        excel_path = folder_directory / excel_filename
        return excel_path

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

    @staticmethod
    def write_excel(
        df,
        workbook: str,
        sheet_name: str,
        range: Optional[str] = "A2",
        clear_sheet: bool = False,
        save: bool = True,
        only_values: bool = False,
    ):
        try:
            with xw.App(visible=False) as app:
                if os.path.isfile(workbook):
                    wb = xw.Book(workbook)
                else:
                    wb = xw.Book()
                    wb.save(workbook)
                if len(sheet_name) > 30:
                    sheet_name = sheet_name[:30]
                    logger.warning(f"Sheet name too long. Truncated to {sheet_name}")
                if sheet_name not in [sheet.name for sheet in wb.sheets]:
                    wb.sheets.add(sheet_name)
                ws = wb.sheets(sheet_name)
                if clear_sheet:
                    ws.clear_contents()
                if only_values:
                    ws.range(range).value = df.values
                else:
                    ws.range(range).value = df
                if save:
                    wb.save()
        except Exception as e:
            logging.error(f"Error writing to Excel: {str(e)}")

    @staticmethod
    def format_excel_general(workbook, sheet_name):
        try:
            with xw.App(visible=False) as app:
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.Orientation = xw_const.PageOrientation.xlPortrait
                ws.api.PageSetup.Zoom = False
                ws.api.PageSetup.FitToPagesWide = 1
                ws.api.PageSetup.FitToPagesTall = False
                ws.api.PageSetup.PaperSize = xw_const.PaperSize.xlPaperA4
                used_range = ws.used_range
                used_range.api.EntireColumn.AutoFit()
                for border_id in range(7, 13):
                    used_range.api.Borders(border_id).LineStyle = (
                        xw_const.LineStyle.xlContinuous
                    )
                    used_range.api.Borders(border_id).Weight = (
                        xw_const.BorderWeight.xlThin
                    )
                wb.save()
        except Exception as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def format_excel_node_results(workbook, sheet_name):
        value_range = ["D3", "D8"]
        header_range = ["B2", "B6"]
        try:
            with xw.App(visible=False) as app:
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.PrintTitleRows = "$1:$4"
                for cell in value_range:
                    ws.range(cell).expand("right").expand(
                        "down"
                    ).api.NumberFormat = "0.0"
                for cell in header_range:
                    ws.range(cell).expand("right").api.Font.Bold = True
                ws.range("B1").value = ws.name
                wb.save()
        except Exception as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def format_excel_profile_results(workbook, sheet_name):
        value_range = ["C4"]
        header_range = ["B2", "A2"]
        try:
            with xw.App(visible=False) as app:
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.PrintTitleRows = "$1:$3"
                for cell in value_range:
                    ws.range(cell).expand("right").expand(
                        "down"
                    ).api.NumberFormat = "0.0"
                for cell in header_range:
                    ws.range(cell).expand("right").api.Font.Bold = True
                ws.range("B1").value = ws.name
                wb.save()
        except Exception as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def _format_node_summary(workbook, sheet_name):
        value_range = ["D2"]
        header_range = ["B1"]
        try:
            with xw.App(visible=False) as app:
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.PrintTitleRows = "$1:$1"
                for cell in value_range:
                    ws.range(cell).expand("right").expand(
                        "down"
                    ).api.NumberFormat = "0.0"
                for cell in header_range:
                    ws.range(cell).expand("right").api.Font.Bold = True
                ws.range("B1").value = ws.name
        except Exception as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def get_last_row(workbook: str, sheet_name: str) -> int:
        try:
            with xw.App(visible=False) as app:
                wb = xw.Book(workbook)
                if sheet_name not in [s.name for s in wb.sheets]:
                    print(f"Sheet '{sheet_name}' does not exist in the workbook.")
                    return -1

                ws = wb.sheets[sheet_name]

                if ws.range("B2").value is None:
                    return 1
                last_row = ws.range("B1").end("down").row
                return last_row
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return -1
