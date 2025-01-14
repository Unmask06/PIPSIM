# excel_handling.py
"""
This module contains the ExcelHandler class for reading and writing to Excel files.
"""
import logging
import os

# import traceback
from pathlib import Path
from typing import Optional

import pandas as pd
import xlwings as xw
from openpyxl.utils import column_index_from_string
from xlwings import constants as xw_const

from project import TextHandler

logger = logging.getLogger("ExcelHandler")
logger.addHandler(TextHandler())

class ExcelHandlerError(Exception):
    """Base class for exceptions in this module."""


class ExcelHandler:
    """
    A class for handling Excel files.
    """

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
        df: pd.DataFrame,
        workbook: str,
        sheet_name: str,
        sht_range: Optional[str] = "A2",
        clear_sheet: bool = False,
        save: bool = True,
        only_values: bool = False,
    ):
        try:

            with xw.App(visible=False):
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
                    ws.range(sht_range).value = df.values
                else:
                    ws.range(sht_range).value = df
                if save:
                    wb.save()
        except ExcelHandlerError as e:
            logging.error(f"Error writing to Excel: {str(e)}")

    @staticmethod
    def format_excel_general(workbook: xw.Book, sheet_name):
        try:
            wb = workbook
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
        except ExcelHandlerError as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def format_excel_node_results(workbook, sheet_name):
        value_range = ["D3", "D8"]
        header_range = ["B2", "B6"]
        try:
            with xw.App(visible=False):
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.PrintTitleRows = "$1:$4"
                for cell in value_range:
                    ws.range(cell).expand("right").expand(
                        "down"
                    ).api.NumberFormat = "0.0"
                for cell in header_range:
                    ws.range(cell).expand("right").api.Font.Bold = True
                    ws.range(cell).expand("right").color = (192, 192, 192)
                ws.range("B1").value = ws.name
                wb.save()
        except ExcelHandlerError as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def format_excel_profile_results(workbook, sheet_name):
        value_range = ["C4"]
        header_range = ["B2", "A2"]
        try:
            with xw.App(visible=False):
                wb = xw.Book(workbook)
                ws = wb.sheets(sheet_name)
                ws.api.PageSetup.PrintTitleRows = "$1:$3"
                for cell in value_range:
                    ws.range(cell).expand("right").expand(
                        "down"
                    ).api.NumberFormat = "0.0"
                for cell in header_range:
                    ws.range(cell).expand("right").api.Font.Bold = True
                    ws.range(cell).expand("right").color = (192, 192, 192)
                ws.range("B1").value = ws.name
                wb.save()
        except ExcelHandlerError as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def _format_node_summary(workbook, sheet_name):
        value_range = ["D2"]
        header_range = ["B1"]
        try:
            with xw.App(visible=False):
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
        except ExcelHandlerError as e:
            logging.error(f"Error formatting Excel: {str(e)}")

    @staticmethod
    def get_last_row(workbook: str, sheet_name: str) -> int:
        try:
            with xw.App(visible=False):
                wb = xw.Book(workbook)
                if sheet_name not in [s.name for s in wb.sheets]:
                    print(f"Sheet '{sheet_name}' does not exist in the workbook.")
                    return -1

                ws = wb.sheets[sheet_name]

                if ws.range("B2").value is None:
                    return 1
                last_row = ws.range("B1").end("down").row
                return last_row
        except ExcelHandlerError as e:
            logging.error(f"An error occurred: {e}")
            return -1

    @staticmethod
    def first_row_as_second_header(
        df: pd.DataFrame, index_1: str, index_2: str
    ) -> pd.DataFrame:
        """
        Add the first row of the DataFrame as a second level multi-header.

        Parameters:
        - df (pd.DataFrame): The original DataFrame.
        - index_1 (str): The name of the first level index.
        - index_2 (str): The name of the second level index.

        Returns:
        - pd.DataFrame: A new DataFrame with the first row as part of a multi-index header.
        """

        if df.empty:
            raise ValueError("The DataFrame is empty.")

        first_row = df.iloc[0]
        columns_level_1 = df.columns

        multi_index_tuples = list(zip(columns_level_1, first_row))

        multi_index = pd.MultiIndex.from_tuples(
            multi_index_tuples, names=[index_1, index_2]
        )
        df_modified = df.drop(index=df.index[0])
        df_modified.columns = multi_index
        df_modified.reset_index(drop=True, inplace=True)
        df_modified.index = df_modified.index + 1
        df_modified.index.names = [index_1]

        return df_modified

    @staticmethod
    def split_cell_reference(cell_ref: str) -> dict[str, int]:
        """
        Splits an Excel cell reference into its numerical row and column indices.

        Args:
            cell_ref (str): The Excel cell reference, e.g., "A1".

        Returns:
            dict[str, int]: {"column": column_number, "row": row_number}
            Example: {"column": 1, "row": 1}
        """
        column_letter = "".join(filter(str.isalpha, cell_ref))
        row_number = "".join(filter(str.isdigit, cell_ref))

        column_number = column_index_from_string(column_letter)
        row_number = int(row_number)

        return {"column": column_number, "row": row_number}
