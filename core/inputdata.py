# inputdata.py
"""
This module contains the 'InputData' dataclass for processing data from an Excel file
specified in the input configuration file.
"""

from dataclasses import dataclass, field

import pandas as pd

from .excel_handling import ExcelHandler


@dataclass
class InputData:
    """Dataclass for processing and storing data from an input configuration Excel file.

    Attributes:
        excelfile (str): The path to the input configuration Excel file.
        well_profile_sheet (str): The name of the sheet containing well profile data.
        well_profile_starting_range (str): The starting cell range of the well profile data.
        conditions_sheet (str): The name of the sheet containing conditions data.
        conditions_starting_range (str): The starting cell range of the conditions data.
    
    Generated Attributes:
        well_profile (pd.DataFrame): The loaded well profile data as a pandas DataFrame.
        conditions (pd.DataFrame): The loaded conditions data as a pandas DataFrame.
    """

    excelfile: str
    well_profile_sheet: str
    well_profile_starting_range: str
    conditions_sheet: str
    conditions_starting_range: str
    well_profile: pd.DataFrame = field(init=False)
    conditions: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        """Initializes the dataframes after the dataclass is instantiated."""
        self.well_profile = self._load_sheet_data(
            self.well_profile_sheet, self.well_profile_starting_range
        )
        self.conditions = self._load_sheet_data(
            self.conditions_sheet, self.conditions_starting_range
        )

    def _load_sheet_data(self, sheet_name: str, starting_range: str) -> pd.DataFrame:
        """Loads data from a specified sheet and range in the Excel file.

        Args:
            sheet_name (str): The name of the Excel sheet.
            starting_range (str): The cell range where data starts.

        Returns:
            pd.DataFrame: The data loaded from the Excel sheet as a pandas DataFrame.
        """
        try:
            row_col = ExcelHandler.split_cell_reference(starting_range)
            df = pd.read_excel(
                self.excelfile,
                sheet_name=sheet_name,
                header=row_col["row"] - 1,
                index_col=row_col["column"] - 1,
            )
            df.reset_index(inplace=True)
            return df
        except Exception as e:
            print(f"Failed to load data from {sheet_name} due to: {e}")
            return pd.DataFrame()
