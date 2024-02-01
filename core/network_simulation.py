# Network Simulation.py
import logging
import traceback
from pathlib import Path

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units

from .excel_handling import ExcelHandler
from .unit_conversion import UnitConversion


def dict_to_df(dict: dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(dict)


class NetworkSimulation:
    def __init__(self, folder_directory, model_filename, excel_filename) -> None:
        self.logger = logging.getLogger(NetworkSimulation.__name__)
        self.folder_directory = folder_directory
        self.model_path = f"{folder_directory}\\{model_filename}"
        self.model_filename = model_filename
        self.excel_filename = excel_filename
        self.excel_path = f"{folder_directory}\\{excel_filename}"
        self.logger.info(
            f"------------Network Simulation Object Created----------------\n"
            f"Model Path: {self.model_path}\n"
        )

    def initialize_excel_handler(self, pipsim_input_sheet, conditions_sheet):
        self.excel_handler = ExcelHandler(
            folder_directory=self.folder_directory, excel_filename=self.excel_filename
        )
        self.all_conditions = self.excel_handler.get_all_condition(
            sheet_name=conditions_sheet
        )
        self.conditions = self.all_conditions.index.to_list()
        self.all_profiles = self.excel_handler.get_all_profiles(
            sheet_name=pipsim_input_sheet
        )
        self.cases = self.all_profiles.columns.to_list()

    def prepare_model(self, case=None, condition=None):
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

    def open_model(self):
        self.model: Model = Model.open(filename=self.model_path, units=Units.FIELD)

    def set_global_conditions(self, source_name, pump_name):
        (
            AMBIENT_TEMPERATURE,
            SOURCE_PRESSURE,
            SOURCE_TEMPERATURE,
            DIFFERENTIAL_PRESSURE,
        ) = self.condition.iloc[0]

        self.model.sim_settings.ambient_temperature = AMBIENT_TEMPERATURE

        self.model.set_values(
            {
                source_name: {
                    "Pressure": SOURCE_PRESSURE,
                    "Temperature": SOURCE_TEMPERATURE,
                },
                **{
                    pump: {"PressureDifferential": DIFFERENTIAL_PRESSURE}
                    for pump in pump_name
                },
            }
        )
        self.logger.info(f"Set Global Conditions")

    def get_boundary_conditions(self):
        self.logger.info(f"Getting boundary conditions.....")
        boundary_conditions_dict: dict = (
            self.model.tasks.networksimulation.get_conditions()
        )
        self.boundary_conditions: pd.DataFrame = pd.DataFrame.from_dict(
            boundary_conditions_dict
        )

    def get_well_values(self):
        self.logger.info(f"Getting well values.....")
        values_dict = self.model.get_values(parameters=["IsActive"], show_units=True)
        self.values = pd.DataFrame.from_dict(values_dict)
        required_cols = ["Unit"] + self.well_lists
        self.well_values = self.values[required_cols].dropna(
            how="all", axis=0, subset=required_cols[1:]
        )

    def activate_all_wells(self):
        self.well_values.loc["IsActive"] = self.well_values.loc["IsActive"].apply(
            lambda x: True if x == False else x
        )
        self.model.set_values(dict=self.well_values[self.well_lists].to_dict())
        self.model.tasks.networksimulation.reset_conditions()
        self.get_boundary_conditions()
        self.logger.info(f"Activated all wells")

    def deactivate_noflow_wells(self):
        condition = self.profile[self.case] < 0.001
        self.no_flow_wells = self.profile.loc[condition, self.case].index.to_list()
        self.values.loc[["IsActive"], self.no_flow_wells] = False
        _deactivated_wells = self.values.loc[["IsActive"], self.no_flow_wells].to_dict()
        self.model.set_values(dict=_deactivated_wells)
        self.model.tasks.networksimulation.reset_conditions()
        self.logger.info(f"Deactivated no flow wells")

    def _specify_system_profiles_variables(self):
        self.system_variables = [
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        self.profile_variables = [
            ProfileVariables.PRESSURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
        ]

    def populate_flowrates_in_model_from_excel(self):
        for well in self.well_lists:
            if well in self.boundary_conditions.columns:
                _flowrate = self.profile.loc[well, self.case]
                self.boundary_conditions.at["LiquidFlowRate", well] = _flowrate
            else:
                self.logger.error(f"{well} not in the model")

        _bc_dict = self.boundary_conditions.loc[["LiquidFlowRate"]].to_dict()
        self.model.tasks.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        self.logger.info(f"Populated flowrates in model from excel")
        self.saveAs_newModel()

    def run_simulation(self):
        if len(self.model.tasks.networksimulation.validate()) > 0:
            raise Exception("Model Validation Unsuccessful")

        self._specify_system_profiles_variables()
        self.results = self.model.tasks.networksimulation.run(
            system_variables=self.system_variables,
            profile_variables=self.profile_variables,
        )

    def process_results(self):
        self.node_results = pd.DataFrame.from_dict(self.results.node)
        self.node_results["Type"] = [
            self.boundary_conditions.loc["BoundaryNodeType", well]
            if well in self.boundary_conditions.columns
            else None
            for well in self.node_results.index
        ]
        node_results_unit = self.node_results.loc[["Unit"]]

        self.node_results.dropna(subset=["Type"], inplace=True)
        self.node_results = pd.concat([node_results_unit, self.node_results], axis=0)

        units = pd.DataFrame(self.results.profile_units, index=["Units"])
        dfs = []
        for branch in sorted(self.results.profile.keys()):
            try:
                res = self.results.profile
                branch_df = dict_to_df(res[branch])
                branch_equipement = branch_df["BranchEquipment"][0]
                branch_df["BranchEquipment"] = branch_df["BranchEquipment"].fillna(
                    branch_equipement
                )
                branch_dff = branch_df.iloc[[-1]]
                dfs.append(branch_dff)
            except Exception as e:
                logging.error(f"{branch}")
        combined_df = pd.concat(dfs)
        combined_df.reset_index(drop=True, inplace=True)
        self.profile_results = pd.concat([units, combined_df], axis=0)

        if self.node_results.empty:
            raise Exception("Simulation run Unsuccessful")
        else:
            self.logger.info(f"Simulation run Successful")

        self._reorder_columns()

    def _reorder_columns(self):
        new_node_cols = [
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        new_profile_cols = [
            "BranchEquipment",
            ProfileVariables.PRESSURE,
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
        self.logger.info(f"Converting units.....")
        if unit_conversion:
            node_conversions = {
                SystemVariables.PRESSURE: ("psia", "barg"),
                SystemVariables.TEMPERATURE: ("degF", "degC"),
            }
            profile_conversions = {
                SystemVariables.PRESSURE: ("psia", "barg"),
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

    def write_results_to_excel(self, update=True):
        if update == False:
            sheet_name = f"{self.case}_{self.condition.index.to_list()[0]}"
        else:
            sheet_name = self.model_filename.split(".")[0].split("_BAB")[0]
        node_results_sheet_name = f"{sheet_name}_NR"
        profile_results_sheet_name = f"{sheet_name}_PR"
        self.excel_handler.write_excel(
            df=self.node_results,
            sheet_name=node_results_sheet_name,
            clear_sheet=True,
            workbook="Node Results.xlsx",
        )
        self.excel_handler.write_excel(
            df=self.profile_results,
            sheet_name=profile_results_sheet_name,
            clear_sheet=True,
            workbook="Profile Results.xlsx",
        )
        self.logger.info(f"Results written to excel")

    def saveAs_newModel(self, update=False):
        if update == False:
            new_file = (
                Path(self.folder_directory)
                / f"{self.case}_{self.condition.index.to_list()[0]}_{self.model_filename}"
            )
            self.model.save(new_file)
            self.logger.info(f"Model saved as {new_file}")
        else:
            self.model.save()
            self.logger.info(f"Model saved as {self.model_filename}")

    def close_model(self):
        self.model.close()
        self.logger.info(
            f"------------Network Simulation Object Closed----------------\n"
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
            self.get_well_values()
            self.activate_all_wells()
            self.deactivate_noflow_wells()
            self.populate_flowrates_in_model_from_excel()
            self.close_model()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            self.model.close()
            raise e

    def run_app(self, unit_conversion=True, update=True):
        try:
            self.open_model()
            self.get_boundary_conditions()
            self.run_simulation()
            self.process_results()
            self.convert_units(unit_conversion=unit_conversion)
            self.write_results_to_excel(update=update)
            self.saveAs_newModel(update=update)
            self.close_model()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            self.model.close()
            raise e