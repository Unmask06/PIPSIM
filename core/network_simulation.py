# network_simulation.py
"""
Performs network simulation using the Pipesim model.

This module contains the NetworkSimulation class 
which is responsible for performing network simulation using the Pipesim model.
    - Initializes the simulation.
    - Prepares the model.
    - Sets global conditions.
    - Retrieves boundary conditions and values.
    - Activates and deactivates wells.
    - Runs the simulation.
    - Processes node and profile results.
    - Converts units.
    - Writes results to Excel.
    - Saves the model.
    - Closes the model.

Classes:
- NetworkSimulation: Performs network simulation using the Pipesim model.

Exceptions:
- NetworkSimulationError: Exception raised for errors in the NetworkSimulation class.

Functions:
- dict_to_df: Converts a dictionary to a DataFrame.

"""

import logging
import re

# import traceback
from pathlib import Path
from typing import Any

import pandas as pd
from sixgill.definitions import Parameters, ProfileVariables, SystemVariables
from sixgill.pipesim import Model, Units

from .excel_handling import ExcelHandler
from .unit_conversion import UnitConversion


def dict_to_df(data: dict) -> pd.DataFrame:
    """
    Converts a dictionary to a DataFrame.

    """
    return pd.DataFrame.from_dict(data)


class NetworkSimulationError(Exception):
    """
    Exception raised for errors in the NetworkSimulation class.
    """


class NetworkSimulation:
    """
    Performs network simulation using the Pipesim model.

    """

    NODE_RESULTS_FILE = "Node Results.xlsx"
    PROFILE_RESULTS_FILE = "Profile Results.xlsx"

    def __init__(
        self,
        folder_directory: Path,
        model_filename: str,
        excel_filename: str,
        update_existing_model: bool = False,
    ) -> None:
        self.logger = logging.getLogger(NetworkSimulation.__name__)
        self.folder_directory = folder_directory
        self.model_path = Path(folder_directory) / model_filename
        self.model_filename = model_filename
        self.excel_filename = excel_filename
        self.excel_path = Path(folder_directory) / excel_filename
        self.update: bool = update_existing_model

        self.logger.info(
            f"------------Network Simulation Object Created----------------\n"
            f"Model Path: {self.model_path}\n"
        )

    def initialize_excel_handler(self, pipsim_input_sheet, conditions_sheet):
        self.excel_handler = ExcelHandler(
            folder_directory=self.folder_directory,
            excel_filename=self.excel_filename,
        )
        self.all_conditions = self.excel_handler.get_all_condition(
            sheet_name=conditions_sheet
        )
        self.conditions = self.all_conditions.index.to_list()
        self.all_profiles = self.excel_handler.get_all_profiles(
            sheet_name=pipsim_input_sheet
        )
        self.cases = self.all_profiles.columns.to_list()
        self.NODE_RESULTS_FILE = str(
            Path(self.folder_directory) / NetworkSimulation.NODE_RESULTS_FILE
        )
        self.PROFILE_RESULTS_FILE = str(
            Path(self.folder_directory) / NetworkSimulation.PROFILE_RESULTS_FILE
        )

    def prepare_model(self, case=None, condition=None):
        # for existing model
        if self.update:
            (case, condition) = NetworkSimulation._extract_case_and_condition(
                self.model_filename
            )
        # for new model
        elif self.update is False:
            if case is None:
                case = self.cases[0]
                self.logger.info(f"case not specified, using {case}")
            if condition is None:
                self.condition = self.conditions[0]
                self.logger.info(f"condition not specified, using {condition}")

        self.condition = self.all_conditions.loc[[condition]]
        self.case = case
        self.profile = self.all_profiles[[self.case]].fillna(0)
        self.well_lists = self.profile.index.to_list()
        self.logger.info(
            f"Model prepared\n Case:{self.case}\n Condition: {self.condition.index[0]}"
        )

    @staticmethod
    def _extract_case_and_condition(input_string):
        pattern = r"([^_]+)_([^_]+)_([^_]+)"

        match = re.match(pattern, input_string)

        if not match:
            raise NetworkSimulationError("Invalid input string")
        case = match.group(1) + "_" + match.group(2)
        condition = match.group(3)
        return (case, condition)

    def open_model(self):
        """
        Opens the model file specified in the configuration file.

        Returns:
            self.model:Model: Model object.
        """
        self.model = Model.open(filename=str(self.model_path), units=Units.FIELD)
        self._validate_model()

    def _validate_model(self):
        """
        Validates the model file specified in the configuration file.

        Returns:
            self.model:Model: Model object.
        """

        if self.model.tasks is not None:
            if getattr(self.model.tasks, "networksimulation", None) is None:
                raise NetworkSimulationError(
                    "Network Simulation Task not found in the model"
                )
            self.networksimulation: Any = self.model.tasks.networksimulation

    def set_global_conditions(self, source_name, pump_name):
        (
            ambient_temperature,
            source_pressure,
            source_temperature,
            differential_pressure,
        ) = self.condition.iloc[0]

        if self.model.sim_settings is not None:
            self.model.sim_settings.ambient_temperature = ambient_temperature

        self.model.set_values(
            {
                source_name: {
                    SystemVariables.PRESSURE: source_pressure,
                    SystemVariables.TEMPERATURE: source_temperature,
                },
                **{
                    pump: {
                        Parameters.SharedPumpParameters.PRESSUREDIFFERENTIAL: differential_pressure
                    }
                    for pump in pump_name
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
        boundary_conditions_dict: dict = self.networksimulation.get_conditions()
        self.boundary_conditions: pd.DataFrame = pd.DataFrame.from_dict(
            boundary_conditions_dict
        )

    def get_all_values(self):
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Returns:
            self.values:DataFrame: DataFrame containing all values.
            self.model_inputs:DataFrame: DataFrame containing all components and their types.
        """
        self.logger.info("Getting all values.....")
        values_dict = self.model.get_values(
            parameters=[
                Parameters.ModelComponent.ISACTIVE,
                SystemVariables.PRESSURE,
                Parameters.Junction.TREATASSOURCE,
                Parameters.Flowline.INNERDIAMETER,
            ],
            show_units=True,
        )
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
        self.model_inputs = pd.DataFrame(data)
        self.values = pd.DataFrame.from_dict(values_dict)

    def get_well_values(self):
        """
        Retrieves all values from the model and stores them in a DataFrame.

        Returns:
            self.well_values:DataFrame: DataFrame containing all wells.
        """
        self.logger.info("Getting well values.....")
        if self.well_lists is None:
            self.well_lists = self.model_inputs.loc[
                self.model_inputs["type"] == "Well", "component"
            ].to_list()
        required_cols = ["Unit"] + self.well_lists
        self.well_values = self.values[required_cols].dropna(
            how="all", axis=0, subset=required_cols[1:]
        )

    def activate_all_wells(self):
        self.well_values.loc["IsActive"] = True
        self.model.set_values(dict=self.well_values[self.well_lists].to_dict())
        self.networksimulation.reset_conditions()
        self.get_boundary_conditions()
        self.logger.info("Activated all wells")

    def deactivate_noflow_wells(self):
        condition = self.profile[self.case] < 0.001
        self.no_flow_wells = self.profile.loc[condition, self.case].index.to_list()
        self.values.loc[["IsActive"], self.no_flow_wells] = False
        _deactivated_wells = self.values.loc[["IsActive"], self.no_flow_wells].to_dict()
        self.model.set_values(dict=_deactivated_wells)
        self.networksimulation.reset_conditions()
        self.logger.info("Deactivated no flow wells")

    def _specify_system_profiles_variables(self):
        self.system_variables = [
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        self.profile_variables = [
            ProfileVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
            ProfileVariables.PRESSURE,
            ProfileVariables.TEMPERATURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
            ProfileVariables.VOLUME_FLOWRATE_WATER_INSITU,
        ]

    def populate_flowrates_in_model_from_excel(self):
        if self.well_lists is None:
            raise NetworkSimulationError("Well lists not available")
        for well in self.well_lists:
            if well in self.boundary_conditions.columns:
                _flowrate = self.profile.loc[well, self.case]
                self.boundary_conditions.at[
                    Parameters.Boundary.LIQUIDFLOWRATE, well
                ] = _flowrate
            else:
                self.logger.error(f"{well} not in the model")

        _bc_dict = self.boundary_conditions.loc[
            [Parameters.Boundary.LIQUIDFLOWRATE]
        ].to_dict()
        self.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        self.logger.info("Populated flowrates in model from excel")
        self.save_as_new_model()

    def run_simulation(self):
        if len(self.networksimulation.validate()) > 0:
            raise NetworkSimulationError("Model Validation Unsuccessful")

        self._specify_system_profiles_variables()
        self.results = self.networksimulation.run(
            system_variables=self.system_variables,
            profile_variables=self.profile_variables,
        )

    def process_node_results(self):
        self.node_results = pd.DataFrame.from_dict(self.results.node)

        if self.node_results.empty:
            raise NetworkSimulationError(
                "Simulation run Unsuccessful."
                "No results found. Check License availablity or model validity."
            )

        self.node_results.reset_index(inplace=True)
        self.node_results.rename(columns={"index": "Node"}, inplace=True)
        self.node_results[SystemVariables.TYPE] = [
            (
                self.boundary_conditions.loc["BoundaryNodeType", well]
                if well in self.boundary_conditions.columns
                else None
            )
            for well in self.node_results["Node"]
        ]
        node_results_unit = self.node_results.iloc[0:1]
        self.node_results.sort_values(
            by=[SystemVariables.TYPE, "Node"], ascending=[False, True], inplace=True
        )
        self.node_results.dropna(subset=[SystemVariables.TYPE], inplace=True)
        self.node_results = pd.concat([node_results_unit, self.node_results], axis=0)
        self.node_results.reset_index(drop=True, inplace=True)

    def process_profile_results(self):
        units = pd.DataFrame(self.results.profile_units, index=["Units"])
        dfs = []
        for branch in sorted(self.results.profile.keys()):
            try:
                res = self.results.profile
                branch_df: pd.DataFrame = dict_to_df(res[branch]).dropna(
                    subset=["BranchEquipment"]
                )
                branch_df.loc[:, "BranchEquipment"] = branch_df.loc[
                    :, "BranchEquipment"
                ].ffill()
                df_unique = branch_df.drop_duplicates(
                    subset=["BranchEquipment"], keep="last"
                )
                dfs.append(df_unique)
            except NetworkSimulationError:
                logging.error(f"{branch}")
        combined_df = pd.concat(dfs)
        combined_df.sort_values(by=["BranchEquipment"], inplace=True)
        combined_df.reset_index(drop=True, inplace=True)
        self.profile_results = pd.concat([units, combined_df], axis=0)
        self.profile_results.reset_index(drop=True, inplace=True)
        self.logger.info("Simulation run Successful")

        self._reorder_columns()

    def _reorder_columns(self):
        new_node_cols = [
            "Node",
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        new_profile_cols = [
            "BranchEquipment",
            ProfileVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
            ProfileVariables.VOLUME_FLOWRATE_WATER_INSITU,
            ProfileVariables.PRESSURE,
            ProfileVariables.TEMPERATURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
        ]

        self.node_results = self.node_results[new_node_cols]
        self.profile_results = self.profile_results[new_profile_cols]

    def convert_units(self, unit_conversion=True):
        self.logger.info("Converting units.....")
        if unit_conversion:
            node_conversions = {
                SystemVariables.PRESSURE: ("psia", "barg"),
                SystemVariables.TEMPERATURE: ("degF", "degC"),
            }
            profile_conversions = {
                ProfileVariables.PRESSURE: ("psia", "barg"),
                ProfileVariables.TEMPERATURE: ("degF", "degC"),
                ProfileVariables.PRESSURE_GRADIENT_FRICTION: ("psi/ft", "bar/100m"),
                ProfileVariables.ELEVATION: ("ft", "m"),
                ProfileVariables.MEAN_VELOCITY_FLUID: ("ft/s", "m/s"),
                ProfileVariables.EROSIONAL_VELOCITY: ("ft/s", "m/s"),
                ProfileVariables.TOTAL_DISTANCE: ("ft", "m"),
            }

            self.node_results = UnitConversion.convert_units(
                dataframe=self.node_results, conversions=node_conversions
            )
            self.profile_results = UnitConversion.convert_units(
                dataframe=self.profile_results, conversions=profile_conversions
            )

    def write_results_to_excel(self):
        sheet_name = f"{self.case}_{self.condition.index.to_list()[0]}"
        node_results_sheet_name = sheet_name
        profile_results_sheet_name = sheet_name
        ExcelHandler.write_excel(
            df=self.node_results,
            sheet_name=node_results_sheet_name,
            clear_sheet=True,
            sht_range="A2",
            workbook=self.NODE_RESULTS_FILE,
        )

        ExcelHandler.format_excel_general(
            workbook=self.NODE_RESULTS_FILE,
            sheet_name=node_results_sheet_name,
        )
        ExcelHandler.format_excel_profile_results(
            workbook=self.NODE_RESULTS_FILE,
            sheet_name=node_results_sheet_name,
        )

        ExcelHandler.write_excel(
            df=self.profile_results,
            sheet_name=profile_results_sheet_name,
            clear_sheet=True,
            workbook=self.PROFILE_RESULTS_FILE,
        )
        ExcelHandler.format_excel_general(
            workbook=self.PROFILE_RESULTS_FILE,
            sheet_name=profile_results_sheet_name,
        )
        ExcelHandler.format_excel_profile_results(
            workbook=self.PROFILE_RESULTS_FILE,
            sheet_name=profile_results_sheet_name,
        )

        self.logger.info("Results written to excel")

    def save_as_new_model(self, update=False):
        if update is False:
            new_file = (
                Path(self.folder_directory)
                / f"{self.case}_{self.condition.index.to_list()[0]}_{self.model_filename}"
            )
            self.model.save(str(new_file))
            self.logger.info(f"Model saved as {new_file}")
        else:
            self.model.save()
            self.logger.info(f"Model saved as {self.model_filename}")

    def close_model(self):
        self.model.close()
        self.logger.info(
            "------------Network Simulation Object Closed----------------\n"
        )

    def create_model(
        self,
        source_name,
        pump_name,
        case=None,
        condition=None,
    ):
        try:
            self.prepare_model(case=case, condition=condition)
            self.open_model()
            self.set_global_conditions(source_name=source_name, pump_name=pump_name)
            self.get_boundary_conditions()
            self.get_all_values()
            self.get_well_values()
            self.activate_all_wells()
            self.deactivate_noflow_wells()
            self.populate_flowrates_in_model_from_excel()
            self.close_model()
        except Exception as e:
            # self.logger.error(traceback.format_exc())
            self.logger.error(e)
            self.model.close()
            raise e

    def run_existing_model(
        self,
        source_name,
        pump_name,
        unit_conversion=True,
        update=True,
    ):
        try:
            self.update = update
            self.prepare_model()
            self.open_model()
            self.set_global_conditions(source_name=source_name, pump_name=pump_name)
            self.get_boundary_conditions()
            self.run_simulation()
            self.process_node_results()
            self.process_profile_results()
            self.convert_units(unit_conversion=unit_conversion)
            self.write_results_to_excel()
            self.save_as_new_model(update=update)
            self.close_model()
        except Exception as e:
            # self.logger.error(traceback.format_exc())
            self.logger.error(e)
            self.model.close()
            raise e
