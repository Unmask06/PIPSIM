# Network Simulation.py
import logging
import traceback

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units


def dict_to_df(dict: dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(dict)


class NetworkSimulation:
    def __init__(self, folder_directory, model_filename, excel_filename) -> None:
        self.folder_directory = folder_directory
        self.model_path = f"{folder_directory}\\{model_filename}"
        self.model_filename = model_filename
        self.excel_filename = excel_filename
        self.excel_path = f"{folder_directory}\\{excel_filename}"
        self.conversion_specs = {}
        self._load_data_from_excel()
        self._prepare_model()

    def _load_data_from_excel(self):
        self.input_df = pd.read_excel(
            self.excel_path, sheet_name="PIPSIM Input", header=3, index_col=0
        )
        self.conditions = pd.read_excel(
            self.excel_path, sheet_name="Conditions", header=2, index_col=0
        )
        self.units_used = pd.read_excel(
            self.excel_path, sheet_name="Units", header=0, index_col=0
        ).to_dict()

    def _prepare_model(self):
        self.model: Model = Model.open(filename=self.model_path, units=Units.FIELD)
        self.well_lists = self.input_df.index.to_list()
        self.cases = self.input_df.columns.to_list()

    def get_boundary_conditions(self):
        boundary_conditions_dict: dict = (
            self.model.tasks.networksimulation.get_conditions()
        )
        self.boundary_conditions: pd.DataFrame = pd.DataFrame.from_dict(
            boundary_conditions_dict
        )

    def get_well_values(self):
        values_dict = self.model.get_values(show_units=True)
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
    
    def deactivate_noflow_wells(self, case=None):
        if case is None:
            case = self.cases[0]
        condition = self.input_df[case] < 0.001
        self.no_flow_wells = self.input_df.loc[condition, case].index.to_list()
        self.values.loc[["IsActive"], self.no_flow_wells] = False
        _deactivated_wells = self.values.loc[["IsActive"], self.no_flow_wells].to_dict()
        self.model.set_values(dict=_deactivated_wells)
        self.model.tasks.networksimulation.reset_conditions()

    def _specify_system_profiles_variables(self):
        self.system_variables = [
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        self.profile_variables = [
            ProfileVariables.TEMPERATURE,
            ProfileVariables.PRESSURE,
            ProfileVariables.ELEVATION,
            ProfileVariables.TOTAL_DISTANCE,
        ]

    def populate_flowrates_in_model_from_excel(self, case=None):
        if case is None:
            case = self.cases[0]

        for well in self.well_lists:
            if well in self.boundary_conditions.columns:
                _flowrate = self.input_df.loc[well, case]
                self.boundary_conditions.at["LiquidFlowRate", well] = _flowrate
            else:
                print(f"{well} not in the model")

        _bc_dict = self.boundary_conditions.loc[["LiquidFlowRate"]].to_dict()
        self.model.tasks.networksimulation.set_conditions(boundaries=_bc_dict)
        self.get_boundary_conditions()
        self.saveAs_newModel()

    def run_simulation(self):
        self._specify_system_profiles_variables()
        self.results = self.model.tasks.networksimulation.run(
            system_variables=self.system_variables,
            profile_variables=self.profile_variables,
        )

        self.node_results = pd.DataFrame.from_dict(self.results.node)
        self.profile_results = pd.DataFrame.from_dict(self.results.profile)

        if self.node_results.empty:
            raise Exception("Simulation run Unsuccesful")

    def process_results(self):
        pass

    def write_results_to_excel(self, case=None):
        if case is None:
            case = self.cases[0]
        wb = xw.Book(self.excel_path)
        sheet_name = case + "_Results"
        if sheet_name not in [sheet.name for sheet in wb.sheets]:
            wb.sheets.add(sheet_name)
        ws = wb.sheets(sheet_name)
        ws.clear_contents()

        ws.range("B2").value = self.node_results

    def saveAs_newModel(self, case=None):
        if case is None:
            case = self.cases[0]
        new_file = self.folder_directory + "\\" + case + "_" + self.model_filename
        self.model.save(new_file)
