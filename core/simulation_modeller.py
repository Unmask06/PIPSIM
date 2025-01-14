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

# import traceback
from pathlib import Path

import pandas as pd
from sixgill.definitions import ModelComponents, Parameters, SystemVariables
from sixgill.pipesim import Model

from .model_input import ModelInput, PipsimModel, PipsimModellingError

logger = logging.getLogger(__name__)


class PipsimModeller:
    """
    Builds the model for network simulation using the Pipesim model.
    """

    model: PipsimModel
    model_input: ModelInput
    boundary_conditions: pd.DataFrame
    values: pd.DataFrame
    category: pd.DataFrame
    well_values: pd.DataFrame
    well_lists: list

    MINIMUM_FLOWRATE = 0.001  # Minimum flowrate for a well to be active (STBD)

    def __init__(self, model: PipsimModel, model_input: ModelInput) -> None:
        self.model = model
        self.model_input = model_input

    def set_global_conditions(self) -> None:

        self.model_input.none_check()
        if self.model.model.sim_settings is not None:
            self.model.model.sim_settings.ambient_temperature = (
                self.model_input.ambient_temperature
            )

        self.model.model.set_values(
            {
                self.model_input.source_name: {
                    SystemVariables.PRESSURE: self.model_input.source_pressure,
                    SystemVariables.TEMPERATURE: self.model_input.source_temperature,
                },
                **{
                    pump: {
                        Parameters.SharedPumpParameters.PRESSUREDIFFERENTIAL: self.model_input.differential_pressure
                    }
                    for pump in self.model_input.pump_name
                },
            }
        )
        self.model.networksimulation.reset_conditions()
        logger.info("Set Global Conditions")

    def get_boundary_conditions(self) -> None:
        """
        Retrieves all boundary conditions from the model and stores them in a DataFrame.

        Stores the boundary conditions in the attribute 'boundary_conditions'.
        """
        logger.info("Getting boundary conditions.....")
        self.boundary_conditions: pd.DataFrame = pd.DataFrame.from_dict(
            self.model.networksimulation.get_conditions()
        )

    def get_all_values(self) -> None:
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Stores the values in the attribute 'values'.
        """
        logger.info("Getting all values.....")
        values_dict = self.model.model.get_values(
            parameters=[
                Parameters.ModelComponent.ISACTIVE,
                SystemVariables.PRESSURE,
                Parameters.Junction.TREATASSOURCE,
                Parameters.Flowline.INNERDIAMETER,
            ],
            show_units=True,
        )
        self.values = pd.DataFrame.from_dict(values_dict)
        self._catergorize_components(values_dict)

    def _catergorize_components(self, values_dict):  # TODO: improve this method
        """
        Categories the components in the model into their respective types.
        """
        keyword_to_component_type = {
            "InnerDiameter": "FlowLine",
            "Pressure": "Well",
            "TreatAsSource": "Junction",
        }

        data_list = []
        for key, value in values_dict.items():
            component_type = None

            for keyword, type_name in keyword_to_component_type.items():
                if value is not None and keyword in value:
                    component_type = type_name
                    break

            data_list.append({"component": key, "type": component_type})

        self.category = pd.DataFrame(data_list)

    def get_well_values(self) -> None:
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Returns:
            self.well_values:DataFrame: DataFrame containing all wells.
        """
        logger.info("Getting well values.....")
        self.well_lists = self.category.loc[
            self.category["type"] == "Well", "component"
        ].to_list()
        required_cols = ["Unit"] + self.well_lists
        self.well_values = self.values[required_cols].dropna(
            how="all", axis=0, subset=required_cols[1:]
        )

    def _set_well_activity(self, wells, active=True):  # TODO: use this method
        activity_values = {
            well: active for well in wells if well in self.values.columns
        }
        if activity_values:
            self.model.model.set_values(dict=activity_values)
            logger.info(
                f"{'Activated' if active else 'Deactivated'} wells: {list(activity_values.keys())}"
            )
        else:
            logger.info("No wells to update.")

    def activate_all_wells(self) -> None:  # TODO: use above method
        self.well_values.loc[Parameters.ModelComponent.ISACTIVE] = True
        self.model.model.set_values(dict=self.well_values[self.well_lists].to_dict())
        self.model.networksimulation.reset_conditions()
        self.get_boundary_conditions()
        logger.info("Activated all wells")

    def deactivate_noflow_wells(self):  # TODO: use above method
        condition = (
            self.model_input.well_profile[self.model.case] < self.MINIMUM_FLOWRATE
        )
        no_flow_wells = self.model_input.well_profile.loc[condition, "Wells"]
        self.values.loc[[Parameters.ModelComponent.ISACTIVE], no_flow_wells] = False
        _deactivated_wells = self.values.loc[
            [Parameters.ModelComponent.ISACTIVE], no_flow_wells
        ].to_dict()
        self.model.model.set_values(dict=_deactivated_wells)
        self.model.networksimulation.reset_conditions()
        self.get_boundary_conditions()
        logger.info("Deactivated no flow wells")

    def populate_flowrates_in_model_from_excel(self):
        if self.well_lists is None:
            raise PipsimModellingError("Well lists not available")
        for well in self.well_lists:
            if (
                well in self.boundary_conditions.columns
                and well in self.model_input.well_profile["Wells"].to_list()
            ):
                _flowrate = self.model_input.well_profile.loc[
                    self.model_input.well_profile["Wells"] == well, self.model.case
                ]
                self.boundary_conditions.at[Parameters.Boundary.LIQUIDFLOWRATE, well] = _flowrate.values[0]  # type: ignore

        _bc_dict = self.boundary_conditions.loc[["LiquidFlowRate"]].to_dict()
        self.model.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        logger.info("Populated flowrates in model from excel")

    def save_as_new_model(self):
        if self.model.folder_path is None:
            self.model.folder_path = str(Path.cwd())
        new_file = (
            Path(self.model.folder_path)
            / f"{self.model.case}_{self.model.condition}_{self.model.base_model_filename}"
        )
        self.model.model.save(str(new_file))
        logger.info(f"Model saved as {new_file}")

    def close_model(self):
        self.model.model.close()
        logger.info("------------Network Simulation Object Closed----------------\n")

    def build_model_global_conditions(self):
        self.set_global_conditions()
        self.save_as_new_model()
        self.close_model()

    def build_model(self):
        self.set_global_conditions()
        self.get_boundary_conditions()
        self.get_all_values()
        self.get_well_values()
        self.activate_all_wells()
        self.deactivate_noflow_wells()
        self.populate_flowrates_in_model_from_excel()
        self.save_as_new_model()
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
        raise PipsimModellingError(f"Destination folder not found: {destination_folder_path}")

    source_model = Model.open(source_model_path)
    logger.info(f"Getting flowline data from {Path(source_model_path).name}.....")
    source_values = source_model.get_values(component=ModelComponents.FLOWLINE)
    df = pd.DataFrame(source_values)
    flowline_geometry = _collect_flowline_geometry(df, source_model)
    source_model.close()

    for target_model_path in Path(destination_folder_path).glob("*.pips"):
        logger.info(
            f"Copying basic flowline data from to {Path(target_model_path).name}....."
        )
        target_model = Model.open(str(target_model_path))
        target_model.set_values(source_values)
        target_model.save()

        logger.info(
            f"Copying detailed flowline data from to {Path(target_model_path).name}....."
        )

        for i, flowline in enumerate(flowline_geometry):
            for name, geometry in flowline.items():
                target_model.set_geometry(context=name, value=geometry)
            if (i + 1) % 10 == 0:
                logger.info(f"Copied geometry for {i + 1} flowlines")
        target_model.save()
        target_model.close()
        logger.info(f"Flowline data copied successfully to {Path(target_model_path).name}")
