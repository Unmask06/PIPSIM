# inputdata.py
"""
This module contains the 'InputData' dataclass for processing data from an Excel file
specified in the input configuration file.
"""

from dataclasses import dataclass, field
from itertools import product

import pandas as pd

from app.core.excel_handling import ExcelHandler


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

        self._create_case_conditions()

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

    def get_parameter_for_condition(self, condition: str, param: str) -> float:
        """
        Retrieves the value of a parameter for a given condition.

        Args:
            condition (str): The condition for which to retrieve the parameter value.
            param (str): The name of the parameter to retrieve.

        Returns:
            float: The value of the parameter for the given condition.

        Raises:
            ValueError: If the specified parameter is not found in the conditions sheet.
        """

        if param not in self.conditions.columns:
            raise ValueError(f"Parameter '{param}' not found in the conditions sheet.")
        return self.conditions.loc[
            self.conditions["Conditions"] == condition, param
        ].values[0]

    def _create_case_conditions(self) -> None:
        """
        Creates self.case_conditions as a list of tuples of case and condition.

        Raises:
            ValueError: If the well profile sheet does not have 'Wells' as the first column.
            ValueError: If the conditions sheet does not have 'Conditions' as the first column.
        """

        if not self.well_profile.columns[0] == "Wells":
            raise ValueError(
                "The well profile sheet must have 'Wells' as the first column."
            )

        cases = [
            case
            for case in self.well_profile.columns
            if "Unnamed" not in case and "Wells" not in case
        ]
        if not self.conditions.columns[0] == "Conditions":
            raise ValueError(
                "The conditions sheet must have 'Conditions' as the first column."
            )

        conditions = self.conditions["Conditions"].to_list()

        self.case_conditions = list(product(cases, conditions))
