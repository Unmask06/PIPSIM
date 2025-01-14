"""
This module contains the UnitConversion class for converting units in a dataframe.
unit conversion mappings are defined in the unit_conversions dictionary.
unit nomenclature is based on the PIPSIM Units.
"""

import pandas as pd
import logging
from project import TextHandler

logger = logging.getLogger("UnitConversion")
logger.addHandler(TextHandler())

class UnitConversion:
    """
    Class to convert units in a dataframe.
    """

    unit_conversions = {
        ("psia", "barg"): lambda x: (x - 14.7) / 14.5038,
        ("degF", "degC"): lambda x: (x - 32) / 1.8,
        ("ft", "m"): lambda x: x * 0.3048,
        ("ft/s", "m/s"): lambda x: x * 0.3048,
        ("psi/ft", "bar/100m"): lambda x: x * ((1 / 14.5038) / (0.3048 / 100)),
        ("lbm/ft3", "kg/m3"): lambda x: x * 16.0185,
        ("lbm/s", "kg/s"): lambda x: x * 0.453592,
    }

    @staticmethod
    def convert_units(
        dataframe, conversions: dict, first_row_is_unit=True
    ) -> pd.DataFrame:
        """
        Convert units for specified columns in a dataframe based on provided mappings.

        :param dataframe: Pandas DataFrame with data to convert.
        :param conversions: Dictionary where keys are column names in dataframe,
                            and values are tuples of (source_unit, target_unit).

        :param first_row_is_unit: Boolean indicating whether the first row of the dataframe
                                  contains unit labels.

        Eg. conversions = { 'Pressure': ('psia', 'barg'), 'Temperature': ('F', 'C') }
        """

        for column, (source_unit, target_unit) in conversions.items():
            # Check if the column exists and conversion mapping is defined
            if (
                column in dataframe.columns
                and (source_unit, target_unit) in UnitConversion.unit_conversions
            ):
                conversion_factor = UnitConversion.unit_conversions[
                    (source_unit, target_unit)
                ]
                if first_row_is_unit:
                    # Apply conversion
                    dataframe.loc[dataframe.index[1:], column] = dataframe.loc[
                        dataframe.index[1:], column
                    ].apply(conversion_factor)
                    # Update unit in the first row (assuming it contains unit labels)
                    dataframe.loc[dataframe.index[0], column] = target_unit
                else:
                    # Apply conversion
                    dataframe[column] = dataframe[column].apply(conversion_factor)
        return dataframe
