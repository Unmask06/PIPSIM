"""
core/model_populater.py
Feed the model with data from the Excel file.
Generate an excel file with the data from the existing model.
"""

import logging
from typing import Dict, Literal, Optional

import pandas as pd
from sixgill.core.mapping import ParameterError
from sixgill.core.model_context import ContextError
from sixgill.definitions import ModelComponents, Parameters, Units
from sixgill.pipesim import Model

from app.core import ExcelInputError
from app.core.excel_handling import ExcelHandler
from app.project import get_string_values_from_class

logger = logging.getLogger(__name__)


class ModelPopulater:
    """Populate the model with data from the Excel file.

    Main methods:
    - simple_import_data: Import data from the Excel file to the Pipsim model.
    - export_values: Export model values to an Excel file.
    - bulk_import_values: Import model values from an Excel file.
    - import_flowline_geometry: Import flowline geometry data from the Excel file.
    """

    component_data: Optional[pd.DataFrame] = None

    def __init__(
        self,
        pipesim_file: str,
        excel_file: str,
        mode: Literal[
            "bulk_import", "export", "simple_import", "import_flowline_geometry"
        ],
        unit: str = Units.METRIC,
    ):
        self.pipesim_file = pipesim_file
        self.excel_file = excel_file
        self.mode = mode
        self.model = Model.open(pipesim_file, units=unit)

    ############################
    # Methods for simple import
    ############################

    def simple_import_data(self, sheet_name: str) -> None:
        """Import data from the Excel file to the Pipsim model."""
        if self.mode != "simple_import":
            raise ValueError("Mode must be 'simple_import' to import data.")

        self.component_data = self._check_create_component_data(sheet_name)
        self.set_new_parameters()

    def _check_create_component_data(self, sheet_name: str) -> pd.DataFrame:
        """Perform a check to create the component data."""
        try:
            # Validate sheet existence
            excel_file = pd.ExcelFile(self.excel_file)
            if sheet_name not in excel_file.sheet_names:
                raise ExcelInputError(
                    "Sheet not found!",
                    excel_path=self.excel_file,
                    sheet_name=sheet_name,
                )

            # Read the sheet data
            component_data = pd.read_excel(self.excel_file, sheet_name=sheet_name)

            # Validate required columns
            required_columns = {"Name", "Component"}
            missing_columns = required_columns - set(component_data.columns)
            if missing_columns:
                raise ExcelInputError(
                    f"Missing required columns: {missing_columns}",
                    excel_path=self.excel_file,
                    sheet_name=sheet_name,
                )

            # Validate unique 'Name' column
            if not component_data["Name"].is_unique:
                raise ExcelInputError(
                    "Name column should have unique values",
                    excel_path=self.excel_file,
                    sheet_name=sheet_name,
                )

            # Validate 'Component' column values
            valid_components = set(get_string_values_from_class(ModelComponents))
            invalid_components = set(component_data["Component"]) - valid_components
            if invalid_components:
                logger.warning(
                    f"Invalid components found and removed: {invalid_components}"
                )
                component_data = component_data[
                    component_data["Component"].isin(valid_components)
                ]

            return component_data

        except pd.errors.EmptyDataError as exc:
            raise ExcelInputError(
                "The sheet is empty.", excel_path=self.excel_file, sheet_name=sheet_name
            ) from exc
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise

    def set_new_parameters(self) -> None:
        """Set new parameters for components in the Pipsim model."""
        if self.component_data is None:
            raise ValueError("component_data is None. Cannot set new parameters.")

        for component in self.component_data["Component"].unique():
            new_parameters = self._get_new_parameters(component)
            if not new_parameters:
                logger.warning(
                    f"No new parameters found for component {component}. Skipping."
                )
                continue

            self.model.set_values(dict=new_parameters)
            logger.info(f"New parameters set for component - {component}")

    def _get_new_parameters(self, component: str) -> Optional[dict]:
        """Get new parameters for a component from isometric data."""
        if self.component_data is None:
            logger.error("component_data is None. Cannot retrieve parameters.")
            return None

        component_names = list(self.model.get_values(component=component).keys())
        filtered_isometric_data = self.component_data[
            (self.component_data["Component"] == component)
            & self.component_data["Name"].isin(component_names)
        ]

        if filtered_isometric_data.empty:
            logger.warning(
                f"No matching isometric data found for component {component}."
            )
            return None

        extra_names = set(filtered_isometric_data["Name"]) - set(component_names)
        if extra_names:
            logger.error(
                f"Extra names in isometric data for component {component}: {extra_names}"
            )

        available_parameters = set(
            pd.DataFrame(self.model.get_values(component=component)).index
        )
        required_parameters = available_parameters.intersection(
            filtered_isometric_data.columns
        )

        if not required_parameters:
            logger.warning(f"No matching parameters found for component {component}.")
            return None

        return (
            filtered_isometric_data[list(required_parameters)]
            .set_index("Name")
            .to_dict("index")
        )

    ########################################
    # Methods for Export and Bulk Import
    ########################################

    def export_values(
        self, excel_file: str, components: Optional[list[str]] = None
    ) -> None:
        """Export model values to an Excel file."""
        model = Model.open(self.pipesim_file)

        if components is None:
            components = get_string_values_from_class(ModelComponents)

        values = {}
        for component in components:
            try:
                v = model.get_values(component=component)
                values[component] = v
            except ContextError:
                continue

        for key, value in values.items():
            df = pd.DataFrame(value).T
            ExcelHandler.write_excel(df, workbook=excel_file, sheet_name=key)
        logger.info(f"Model values exported to {excel_file}")

    def bulk_import_values(self, excel_file: str) -> None:
        """Import model values from an Excel file."""
        df = pd.read_excel(excel_file, sheet_name=None, index_col=0)

        for key, value in df.items():
            try:
                components = get_string_values_from_class(ModelComponents)
                if key in components:
                    self.model.set_values(dict=value.to_dict(orient="index"))
                    logger.info(f"Values set for {key}")
            except ParameterError:
                logger.error(f"ParameterError: Error setting values for {key}")
            except Exception as e:
                logger.error(f"Error setting values for {key}: {e}")
        logger.info(f"Model values imported from {excel_file}")

    ########################################
    # Methods for Flowline Geometry
    ########################################

    def _check_n_create_flowline_data(self, sheet_name: str) -> Dict[str, pd.DataFrame]:
        """Perform a check to create the flowline data."""
        # Validate sheet existence
        excel_file = pd.ExcelFile(self.excel_file)
        if sheet_name not in excel_file.sheet_names:
            raise ExcelInputError(
                "Sheet not found!",
                excel_path=self.excel_file,
                sheet_name=sheet_name,
            )

        flowlines_df = pd.read_excel(self.excel_file, sheet_name=sheet_name)

        # Validate required columns
        required_columns = {"Name", "Elevation"}
        missing_columns = required_columns - set(flowlines_df.columns)
        if missing_columns:
            raise ExcelInputError(
                f"Missing required columns: {missing_columns}",
                excel_path=self.excel_file,
                sheet_name=sheet_name,
            )

        # create dictionary of flowline data
        flowlines_df["Name"] = flowlines_df["Name"].fillna(method="ffill")
        flowlines_df = flowlines_df.dropna(subset=["Name"])
        flowline_data = {}
        for name, group in flowlines_df.groupby("Name"):
            cols = set(
                get_string_values_from_class(Parameters.FlowlineGeometry)
            ).intersection(set(group.columns))
            flowline_data[name] = group[list(cols)]

        return flowline_data

    def convert_to_detailed_flowline(self, flowlines: list):
        flowline_detail_dict = {
            flowline: {Parameters.Flowline.DETAILEDMODEL: True}
            for flowline in flowlines
        }

        self.model.set_values(dict=flowline_detail_dict)
        logger.info("Flowline converted to detailed model")

    def set_flowline_geometry(self, context, data):
        """Set the geometry for a flowline in the Pipsim model."""
        try:
            self.model.set_geometry(context, data)
        except ValueError as e:
            logger.error(f"Error setting geometry for {context}: {e}")

    def import_flowline_geometry(self, sheet_name: str):
        """Import flowline geometry data from the Excel file."""

        flowline_data = self._check_n_create_flowline_data(sheet_name)

        # Convert to detailed flowline
        flowlines = list(flowline_data.keys())
        self.convert_to_detailed_flowline(flowlines)

        # Set flowline geometry
        for name, data in flowline_data.items():
            self.set_flowline_geometry(name, data)
        logger.info("Flowline geometry imported")
