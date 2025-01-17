# simulation_modeller.py
"""
This module contains the class for building the model for network simulation using Pipesim model.
  
    Classes:
    - PipsimModeller: Builds the model for network simulation using the Pipesim model.

    Methods:
    - copy_flowline_data: Copy flowline data from the source model to the target model.
    
    Raises:
    - PipsimModellingError: Raised when an error occurs in the modelling process.
"""
import logging
from itertools import product

# import traceback
from pathlib import Path

import pandas as pd
from sixgill.definitions import ModelComponents, Parameters
from sixgill.pipesim import Model

from core import PipsimModellingError

logger = logging.getLogger(__name__)


class ConditionColumns:
    """
    Class containing the column names for the conditions DataFrame.
    """

    CONDITIONS = "Conditions"
    COMPONENT_NAME = "Component Name"
    COMPONENT_TYPE = "Component Type"
    PARAMETER = "Parameter"
    VALUE = "Value"


class MultiCaseModeller:
    """
    Builds the model for network simulation using the Pipesim model for multiple cases.
    """

    model: Model
    boundary_conditions: pd.DataFrame
    values: pd.DataFrame
    category: pd.DataFrame
    well_values: pd.DataFrame
    well_lists: list

    MINIMUM_FLOWRATE = 0.001  # Minimum flowrate for a well to be active (STBD)

    def __init__(
        self,
        base_model_path: str,
        excel_path: str,
        sink_profile_sheet: str,
        condition_sheet: str,
    ) -> None:
        self.model = Model.open(base_model_path)
        self.excel_path = excel_path
        self.sink_profile = self._fetch_excel_data(sink_profile_sheet, "Sinks")
        self.conditions = self._fetch_excel_data(condition_sheet, "Conditions")

    def _fetch_excel_data(self, sheet_name: str, key_column: str) -> pd.DataFrame:
        """
        Fetches data from the specified excel sheet.

        Args:
            sheet_name (str): The name of the sheet to fetch data from.
            key_column (str): The key column to set as index and to look for header row.

        Returns:
            pd.DataFrame: The fetched data as a DataFrame.
        """
        data = pd.read_excel(self.excel_path, sheet_name=sheet_name)

        if not key_column in data.iloc[:, 0].to_list():
            msg = f"Key column '{key_column}' not found in the first column of sheet '{sheet_name}'"
            logger.error(msg)
            raise PipsimModellingError(msg)

        header_row = data.loc[data.iloc[:, 0] == key_column].index[0]
        data.columns = data.iloc[header_row]
        data = data.iloc[header_row + 1 :]
        data = data.dropna(subset=[key_column]).reset_index(drop=True)
        data = data.set_index(key_column) if key_column == "Sinks" else data

        if any("_" in str(col) for col in data.columns):
            logger.warning(
                "Don't use underscores in column names.Replacing underscores with hyphens "
            )
            data.columns = data.columns.str.replace("_", "-")

        if key_column == "Conditions":
            mandatory_cols = [
                ConditionColumns.COMPONENT_NAME,
                ConditionColumns.COMPONENT_TYPE,
                ConditionColumns.PARAMETER,
                ConditionColumns.VALUE,
            ]
            if not all(col in data.columns for col in mandatory_cols):
                msg = f"Missing mandatory columns in sheet '{sheet_name}': {mandatory_cols}"
                logger.error(msg)
                raise PipsimModellingError(msg)

        return data

    @property
    def cases(self) -> list:
        """Generates all possible cases from the sink profile and conditions."""

        return list(
            product(
                self.sink_profile.columns,
                self.conditions[ConditionColumns.CONDITIONS].unique(),
            )
        )

    def set_simulation_settings(self, condition: str) -> None:
        df = self.conditions.loc[
            self.conditions[ConditionColumns.CONDITIONS] == condition
        ]
        if df.empty:
            logger.warning(f"No Simulation settings found for condition: {condition}")
            return

        for _, row in df.iterrows():
            if (
                row[ConditionColumns.COMPONENT_TYPE]
                == Parameters.SimulationSetting.__name__
            ):
                attr = self.model.sim_settings.__dict__.get("_settings").get(
                    row[ConditionColumns.PARAMETER]
                )
                setattr(self.model.sim_settings, attr, row["Value"])

        logger.info(f"Set simulation settings for condition: {condition}")

    def set_parameters_dict(self, condition: str) -> None:

        data = self.conditions.loc[
            self.conditions[ConditionColumns.CONDITIONS] == condition
        ]

        if data.empty:
            logger.warning(f"No parameters found for condition: {condition}")
            return

        result = {}
        for component_name, parameter, value in zip(
            data[ConditionColumns.COMPONENT_NAME],
            data[ConditionColumns.PARAMETER],
            data[ConditionColumns.VALUE],
        ):
            if not pd.isnull(component_name) and not pd.isnull(parameter):
                component_name = str(component_name).strip()
                if component_name not in result:
                    result[component_name] = {}
                result[component_name][parameter] = value

        self.model.set_values(dict=result)

        logger.info(f"Set parameters for condition: {condition}")

    def set_sink_data(self, case: str, parameter: str = Parameters.Sink.LIQUIDFLOWRATE):

        # Get the missing sinks
        sinks_in_model = set(
            self.model.get_values(component=ModelComponents.SINK).keys()
        )
        sinks_in_excel = set(self.sink_profile.index)

        if (sinks_in_excel - sinks_in_model) or (sinks_in_model - sinks_in_excel):
            raise PipsimModellingError("Sinks in model and excel do not match.")

        # Transform sink profile to dictionary
        sink_data = self.sink_profile.loc[:, [case]]
        sink_data.columns = [parameter]

        # DeActivate sinks with minimum flowrate
        sink_data[Parameters.ModelComponent.ISACTIVE] = (
            sink_data[parameter] > self.MINIMUM_FLOWRATE
        )
        sink_data[Parameters.Sink.FLOWRATETYPE] = parameter

        sink_data_dict = sink_data.to_dict("index")

        self.model.set_values(dict=sink_data_dict)

        logger.info(f"Set sink data for case: {case}")

    def save_as_new_model(self, case: str, condition: str) -> None:
        folder_path = Path(self.excel_path).parent / "Models"
        folder_path.mkdir(exist_ok=True)
        new_file = Path(folder_path) / f"{case}_{condition}_{self.model.filename}"
        self.model.save(str(new_file))
        logger.info(f"Model saved as {new_file}")

    def close_model(self):
        self.model.close()
        logger.info("------------Network Simulation Object Closed----------------\n")

    def build_model(
        self, case, condition, sink_parameter=Parameters.Sink.LIQUIDFLOWRATE
    ):
        logger.info(f"Building model for case: {case}, condition: {condition}\n")
        self.set_simulation_settings(condition)
        self.set_parameters_dict(condition)
        self.set_sink_data(case, sink_parameter)
        self.save_as_new_model(case, condition)
        self.close_model()


# Other methods in the module------------------------------------------------------------
def _collect_flowline_geometry(df, source_model) -> list:
    """
    Helper function to collect flowline geometry from the source model
    used in the copy_flowline_data function
    """
    flowline_geometry = []
    detailed_flowlines = df.loc[:, df.loc["DetailedModel"] == True].columns.to_list()
    for flowline in detailed_flowlines:
        try:
            flowline_geometry.append(
                {flowline: source_model.get_geometry(context=flowline)}
            )
        except Exception as e:
            logger.error(f"Error getting geometry for {flowline}: {e}")
            # logger.error(traceback.format_exc())
    return flowline_geometry


def copy_flowline_data(source_model_path: str, destination_folder_path: str) -> None:
    """
    Copy flowline data from the source model to all target models in the destination folder.

    Args:
        source_model_path (str): The path to the source model file.
        destination_folder_path (str): The path to the destination folder containing target model files.
    """

    if not Path(source_model_path).exists():
        raise PipsimModellingError(f"Source model file not found: {source_model_path}")
    if not Path(destination_folder_path).exists():
        raise PipsimModellingError(
            f"Destination folder not found: {destination_folder_path}"
        )

    logger.info(
        f"Copying flowline data from {Path(source_model_path).name} "
        f"to all models in {destination_folder_path}....."
    )
    logger.info(
        f"Total number of models in the destination folder: {len(list(Path(destination_folder_path).glob('*.pips')))}"
    )

    source_model = Model.open(source_model_path)
    logger.info(f"Getting flowline data from {Path(source_model_path).name}.....")
    source_values = source_model.get_values(component=ModelComponents.FLOWLINE)
    df = pd.DataFrame(source_values)
    flowline_geometry = _collect_flowline_geometry(df, source_model)
    source_model.close()

    target_files = list(Path(destination_folder_path).glob("*.pips"))

    for idx, target_model_path in enumerate(target_files, start=1):
        logger.info(
            f"Copying basic flowline data from to {Path(target_model_path).name}....."
        )
        logger.warning(
            """This step may take a while depending on the number of flowlines in the model.
            Please wait for the process to complete."""
        )
        target_model = Model.open(str(target_model_path))
        target_model.set_values(source_values)
        target_model.save()

        logger.info(
            f"Copying detailed flowline data to {Path(target_model_path).name}....."
        )

        for flowline in flowline_geometry:
            for name, geometry in flowline.items():
                target_model.set_geometry(context=name, value=geometry)
        target_model.save()
        target_model.close()
        logger.info(
            f"Flowline data copied successfully to {Path(target_model_path).name}",
            f"(Completed {idx} of {len(target_files)} models)",
        )
