# network_simulation.py
"""
    This module contains the NetworkSimulator class for performing network simulation 
    using the Pipesim model.
"""

import logging
import traceback
from pathlib import Path

import pandas as pd
from sixgill.definitions import ProfileVariables, SystemVariables

from .excel_handling import ExcelHandler
from .simulation_modeller import ModelInput, PipsimModel, PipsimModeller
from .unit_conversion import UnitConversion

logger = logging.getLogger(__name__)


class NetworkSimulationError(Exception):
    """
    Exception raised for errors in the NetworkSimulation class.
    """


class NetworkSimulator(PipsimModeller):
    """
    Performs network simulation using the Pipesim model.

    """

    node_results: pd.DataFrame
    profile_results: pd.DataFrame
    system_variables: list
    profile_variables: list
    NODE_RESULTS_FILE: str = "Node Results.xlsx"
    PROFILE_RESULTS_FILE: str = "Profile Results.xlsx"

    def __init__(self, model: PipsimModel, model_input: ModelInput) -> None:
        super().__init__(model=model, model_input=model_input)

    def _specify_system_profiles_variables(self):
        self.system_variables = [
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.FLOWRATE,
        ]
        self.profile_variables = [
            ProfileVariables.PRESSURE,
            ProfileVariables.TEMPERATURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
            ProfileVariables.DENSITY_GAS_INSITU,
            ProfileVariables.MASS_FLOWRATE_GAS_INSITU,
            ProfileVariables.VISCOSITY_GAS_INSITU,
            ProfileVariables.VELOCITY_GAS,
            ProfileVariables.FLOWRATE_GAS_INSITU,
        ]

    def run_simulation(self):
        if len(self.model.networksimulation.validate()) > 0:
            raise NetworkSimulationError("Model Validation Unsuccessful")

        self._specify_system_profiles_variables()
        self.results = self.model.networksimulation.run(
            system_variables=self.system_variables,
            profile_variables=self.profile_variables,
        )

    def process_node_results(self):
        if self.results is not None:
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
        self.node_results = self.node_results.iloc[1:]
        self.node_results.sort_values(
            by=[SystemVariables.TYPE, "Node"], ascending=[False, True], inplace=True
        )
        self.node_results.dropna(subset=[SystemVariables.TYPE], inplace=True)
        self.node_results = pd.concat([node_results_unit, self.node_results], axis=0)
        self.node_results.reset_index(drop=True, inplace=True)

    def process_profile_results(self):
        if self.results is None:
            raise NetworkSimulationError("Simulation run Unsuccessful")
        units = pd.DataFrame(self.results.profile_units, index=["Units"])
        dfs = []
        for branch in sorted(self.results.profile.keys()):
            try:
                res = self.results.profile
                branch_df: pd.DataFrame = pd.DataFrame.from_dict(res[branch])
                branch_df.loc[:, "BranchEquipment"] = branch_df.loc[
                    :, "BranchEquipment"
                ].ffill()
                df_unique = branch_df.drop_duplicates(
                    subset=["BranchEquipment"], keep="last"
                )
                df_unique["Branch"] = branch
                dfs.append(df_unique)
            except NetworkSimulationError:
                logging.error(f"{branch}")
        combined_df = pd.concat(dfs)
        combined_df.sort_values(by=["Branch", "BranchEquipment"], inplace=True)
        combined_df.reset_index(drop=True, inplace=True)
        self.profile_results = pd.concat([units, combined_df], axis=0)
        self.profile_results.reset_index(drop=True, inplace=True)
        logger.info("Simulation run Successful")

        self._reorder_columns()

    def _reorder_columns(self):
        new_node_cols = [
            "Node",
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.FLOWRATE,
        ]
        new_profile_cols = [
            "Branch",
            "BranchEquipment",
            ProfileVariables.PRESSURE,
            ProfileVariables.TEMPERATURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
            ProfileVariables.DENSITY_GAS_INSITU,
            ProfileVariables.MASS_FLOWRATE_GAS_INSITU,
            ProfileVariables.VISCOSITY_GAS_INSITU,
            ProfileVariables.VELOCITY_GAS,
            ProfileVariables.FLOWRATE_GAS_INSITU,
        ]

        self.node_results = self.node_results[new_node_cols]
        self.profile_results = self.profile_results[new_profile_cols]

    def convert_units(self, unit_conversion=True):
        logger.info("Converting units.....")
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
                ProfileVariables.DENSITY_GAS_INSITU: ("lbm/ft3", "kg/m3"),
                ProfileVariables.MASS_FLOWRATE_GAS_INSITU: ("lbm/s", "kg/s"),
            }

            self.node_results = UnitConversion.convert_units(
                dataframe=self.node_results, conversions=node_conversions
            )
            self.profile_results = UnitConversion.convert_units(
                dataframe=self.profile_results, conversions=profile_conversions
            )

    def write_results_to_excel(self):
        sheet_name = Path(self.model.model_filename).stem
        if len(sheet_name) > 31:
            sheet_name = sheet_name[:31]
        node_results_sheet_name = sheet_name
        profile_results_sheet_name = sheet_name
        ExcelHandler.write_excel(
            df=self.node_results,
            sheet_name=node_results_sheet_name,
            clear_sheet=True,
            sht_range="A2",
            workbook=self.NODE_RESULTS_FILE,
        )

        ExcelHandler.write_excel(
            df=self.profile_results,
            sheet_name=profile_results_sheet_name,
            clear_sheet=True,
            workbook=self.PROFILE_RESULTS_FILE,
        )

        logger.info("Results written to excel")

    def run_existing_model(
        self,
        unit_conversion=True,
    ):
        try:
            self.get_boundary_conditions()
            self.run_simulation()
            self.process_node_results()
            self.process_profile_results()
            self.model.model.save()
            self.close_model()
            self.convert_units(unit_conversion=unit_conversion)
            self.write_results_to_excel()

        except Exception as e:
            # logger.error(traceback.format_exc())
            logger.error(e)
            self.model.model.close()
            traceback.print_exc()
            raise e
