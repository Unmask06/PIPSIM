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
from typing import Any

import pandas as pd
from sixgill.definitions import Parameters, ProfileVariables, SystemVariables
from sixgill.pipesim import Model, Units

from core import NetworkSimulationError


@dataclass
class ModelConfig:
    """Dataclass for model configuration."""

    model_filename: Path
    case: str
    condition: str
    folder_path: str = ""
    model_path: Path = field(init=False)

    def __post_init__(self):
        if self.folder_path == "":
            self.folder_path = os.getcwd()

        self.model_path = Path(self.folder_path) / Path(self.model_filename)

        self.model = Model.open(filename=str(self.model_path), units=Units.FIELD)

        if self.model.tasks is not None:
            self.networksimulation = self.model.tasks.networksimulation


@dataclass
class ModelInputs:
    """Dataclass for model inputs."""

    source_name: str
    pump_name: list
    ambient_temperature: float
    source_pressure: float
    source_temperature: float
    differential_pressure: float
    well_profile: pd.DataFrame = field(default_factory=pd.DataFrame)


class PipsimModeller:
    """
    Builds the model for network simulation using the Pipesim model.
    """

    def __init__(self, config: ModelConfig, model_inputs: ModelInputs) -> None:
        self.logger = logging.getLogger(__class__.__name__)
        self.config = config
        self.model_inputs = model_inputs

    def set_global_conditions(self):

        if self.config.model.sim_settings is not None:
            self.config.model.sim_settings.ambient_temperature = (
                self.model_inputs.ambient_temperature
            )

        self.config.model.set_values(
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
        self.logger.info("Set Global Conditions")

    def get_boundary_conditions(self):
        """
        Retrieves all boundary conditions from the model and stores them in a DataFrame.

        Returns:
            self.boundary_conditions:DataFrame: DataFrame containing all boundary conditions.
        """
        self.logger.info("Getting boundary conditions.....")
        self.boundary_conditions: pd.DataFrame = pd.DataFrame.from_dict(
            self.config.networksimulation.get_conditions()
        )

    def get_all_values(self):
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Returns:
            self.values:DataFrame: DataFrame containing all values.
            self.model_inputs:DataFrame: DataFrame containing all components and their types.
        """
        self.logger.info("Getting all values.....")
        values_dict = self.config.model.get_values(show_units=True)
        data = []
        for key in values_dict.keys():
            value = values_dict.get(key)
            if value is not None and "InnerDiameter" in value:
                component_type = "FlowLine"
            elif value is not None and "Pressure" in value:
                component_type = "Well"
            elif value is not None and "TreatAsSource" in value:
                component_type = "Junction"
            else:
                component_type = None
            data.append({"component": key, "type": component_type})
        self.category = pd.DataFrame(data)
        self.values = pd.DataFrame.from_dict(values_dict)

    def get_well_values(self):
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Returns:
            self.well_values:DataFrame: DataFrame containing all wells.
        """
        self.logger.info("Getting well values.....")
        self.well_lists = self.category.loc[
            self.category["type"] == "Well", "component"
        ].to_list()
        required_cols = ["Unit"] + self.well_lists
        self.well_values = self.values[required_cols].dropna(
            how="all", axis=0, subset=required_cols[1:]
        )

    def activate_all_wells(self):
        self.well_values.loc["IsActive"] = True
        self.config.model.set_values(dict=self.well_values[self.well_lists].to_dict())
        self.config.networksimulation.reset_conditions()
        self.get_boundary_conditions()
        self.logger.info("Activated all wells")

    def deactivate_noflow_wells(self):
        condition = self.model_inputs.well_profile[self.config.case] < 0.001
        no_flow_wells = self.model_inputs.well_profile.loc[
            condition, self.config.case
        ].index.to_list()

        self.values.loc[["IsActive"], no_flow_wells] = False
        _deactivated_wells = self.values.loc[["IsActive"], no_flow_wells].to_dict()
        self.config.model.set_values(dict=_deactivated_wells)
        self.config.networksimulation.reset_conditions()
        self.logger.info("Deactivated no flow wells")

    def populate_flowrates_in_model_from_excel(self):
        if self.well_lists is None:
            raise NetworkSimulationError("Well lists not available")
        for well in self.well_lists:
            if well in self.boundary_conditions.columns:
                _flowrate = self.model_inputs.well_profile.loc[well, self.config.case]
                self.boundary_conditions.at["LiquidFlowRate", well] = _flowrate
            else:
                self.logger.error(f"{well} not in the model")

        _bc_dict = self.boundary_conditions.loc[["LiquidFlowRate"]].to_dict()
        self.config.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        self.logger.info("Populated flowrates in model from excel")
        self.save_as_new_model()

    def save_as_new_model(self, update=False):
        if update is False:
            new_file = (
                Path(self.config.folder_path)
                / f"{self.config.case}_{self.config.condition}_{self.config.model_filename}"
            )
            self.config.model.save(str(new_file))
            self.logger.info(f"Model saved as {new_file}")
        else:
            self.config.model.save()
            self.logger.info(f"Model saved as {self.config.model_filename}")

    def close_model(self):
        self.config.model.close()
        self.logger.info(
            "------------Network Simulation Object Closed----------------\n"
        )

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
