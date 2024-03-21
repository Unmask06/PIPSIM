# simulation_modeller.py
"""
This module contains the class for building the model for network simulation using Pipesim model.
    DataClasses:
    - ModelConfig: Configuration for the model.
    - GlobalConditions: Global conditions for the model.
    
    Classes:
    - PipsimModeller: Builds the model for network simulation using the Pipesim model.
    - PipsimSimulator: Simulates the model for network simulation using the Pipesim model.
"""
import logging
import os
from dataclasses import dataclass, field

# import traceback
from pathlib import Path
from typing import Optional

import pandas as pd
from sixgill.definitions import Parameters, ProfileVariables, SystemVariables
from sixgill.pipesim import Model, Units

logger = logging.getLogger(__name__)


@dataclass
class PipsimModel:
    """Dataclass for model configuration."""

    model_filename: str
    case: str
    condition: str
    folder_path: str = ""
    model_path: str = field(init=False)
    model: Model = field(init=False)

    def __post_init__(self):
        if self.folder_path == "":
            self.folder_path = os.getcwd()

        self.model_path = str(Path(self.folder_path) / Path(self.model_filename))

        self.model = Model.open(filename=str(self.model_path), units=Units.FIELD)

        if self.model.tasks is not None:
            self.networksimulation = self.model.tasks.networksimulation


@dataclass
class ModelInput:
    """Dataclass for model inputs."""

    source_name: str
    pump_name: list
    well_profile: pd.DataFrame = field(default_factory=pd.DataFrame)
    ambient_temperature: Optional[float] = None
    source_pressure: Optional[float] = None
    source_temperature: Optional[float] = None
    differential_pressure: Optional[float] = None

    def none_check(self):
        if (
            self.ambient_temperature is None
            or self.source_pressure is None
            or self.source_temperature is None
            or self.differential_pressure is None
        ):
            raise PipsimModellingError(
                "Ambient temperature, source pressure, and "
                "source temperature are required for the model"
            )


class PipsimModellingError(Exception):
    """Raised when an error occurs in the modelling process."""


class PipsimModeller:
    """
    Builds the model for network simulation using the Pipesim model.
    """

    model: PipsimModel
    model_inputs: ModelInput
    boundary_conditions: pd.DataFrame
    values: pd.DataFrame
    category: pd.DataFrame

    def __init__(self, model: PipsimModel, model_inputs: ModelInput) -> None:
        self.model = model
        self.model_inputs = model_inputs

    def set_global_conditions(self) -> None:

        self.model_inputs.none_check()
        if self.model.model.sim_settings is not None:
            self.model.model.sim_settings.ambient_temperature = (
                self.model_inputs.ambient_temperature
            )

        self.model.model.set_values(
            {
                self.model_inputs.source_name: {
                    SystemVariables.PRESSURE: self.model_inputs.source_pressure,
                    SystemVariables.TEMPERATURE: self.model_inputs.source_temperature,
                },
                **{
                    pump: {
                        Parameters.SharedPumpParameters.PRESSUREDIFFERENTIAL: self.model_inputs.differential_pressure
                    }
                    for pump in self.model_inputs.pump_name
                },
            }
        )
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
        condition = self.model_inputs.well_profile[self.model.case] < 0.001
        no_flow_wells = self.model_inputs.well_profile.loc[condition, "Wells"]
        self.values.loc[[Parameters.ModelComponent.ISACTIVE], no_flow_wells] = False
        _deactivated_wells = self.values.loc[
            [Parameters.ModelComponent.ISACTIVE], no_flow_wells
        ].to_dict()
        self.model.model.set_values(dict=_deactivated_wells)
        self.model.networksimulation.reset_conditions()
        logger.info("Deactivated no flow wells")

    def populate_flowrates_in_model_from_excel(self):
        if self.well_lists is None:
            raise PipsimModellingError("Well lists not available")
        for well in self.well_lists:
            if (
                well in self.boundary_conditions.columns
                and well in self.model_inputs.well_profile["Wells"].to_list()
            ):
                _flowrate = self.model_inputs.well_profile.loc[
                    self.model_inputs.well_profile["Wells"] == well, self.model.case
                ]
                self.boundary_conditions.at["LiquidFlowRate", well] = _flowrate.values[
                    0
                ]
            else:
                logger.error(f"{well} not in the model")

        _bc_dict = self.boundary_conditions.loc[["LiquidFlowRate"]].to_dict()
        self.model.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        logger.info("Populated flowrates in model from excel")
        self.save_as_new_model()

    def save_as_new_model(self):
        new_file = (
            Path(self.model.folder_path)
            / f"{self.model.case}_{self.model.condition}_{self.model.model_filename}"
        )
        self.model.model.save(str(new_file))
        logger.info(f"Model saved as {new_file}")

    def close_model(self):
        self.model.model.close()
        logger.info("------------Network Simulation Object Closed----------------\n")

    def bulid_model_global_conditions(self):
        self.set_global_conditions()
        self.close_model()

    def build_model(self):
        self.set_global_conditions()
        self.get_boundary_conditions()
        self.get_all_values()
        self.get_well_values()
        self.activate_all_wells()
        self.deactivate_noflow_wells()
        self.populate_flowrates_in_model_from_excel()
        self.close_model()


class PipsimSimulator(PipsimModeller):
    pass
