# Network Simulation.py
import logging
import traceback
from pathlib import Path

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units


def dict_to_df(dict: dict) -> pd.DataFrame:
    return pd.DataFrame.from_dict(dict)


class ExcelHandler:
    def __init__(self, folder_directory, excel_filename) -> None:
        self.excel_filename = excel_filename
        self.excel_path = f"{folder_directory}\\{excel_filename}"

    def write_excel(
        self,
        df,
        sheet_name,
        range="A1",
        clear_sheet=False,
    ):
        wb = xw.Book(self.excel_path)
        if sheet_name not in [sheet.name for sheet in wb.sheets]:
            wb.sheets.add(sheet_name)
        ws = wb.sheets(sheet_name)
        if clear_sheet:
            ws.clear_contents()
        ws.range(range).value = df

    def get_all_condition(self):
        conditions = pd.read_excel(
            self.excel_path,
            sheet_name="Conditions",
            header=1,
            index_col=0,
            usecols="A:E",
        )
        return conditions

    def get_all_profiles(self):
        profiles = pd.read_excel(
            self.excel_path, sheet_name="PIPSIM Input", header=3, index_col=0
        )
        return profiles


class NetworkSimulation:
    def __init__(self, folder_directory, model_filename, excel_filename) -> None:
        self.logger = logging.getLogger(__name__)
        self.folder_directory = folder_directory
        self.model_path = f"{folder_directory}\\{model_filename}"
        self.model_filename = model_filename
        self.excel_filename = excel_filename
        self.excel_path = f"{folder_directory}\\{excel_filename}"
        self.excel_handler = ExcelHandler(
            folder_directory=self.folder_directory, excel_filename=self.excel_filename
        )
        self.all_conditions = self.excel_handler.get_all_condition()
        self.all_profiles = self.excel_handler.get_all_profiles()
        self.logger.info(
            f"------------Network Simulation Object Created----------------\n"
        )

    def prepare_model(self, case=None, condition=None, do_units_conversion=False):
        if case is None:
            case = self.all_profiles.columns[0]
            self.logger.info(f"case not specified, using {case}")
        if condition is None:
            condition = self.all_conditions.index[0]
            self.logger.info(f"condition not specified, using {condition}")
        self.condition = self.all_conditions.loc[[condition]]
        self.case = case
        self.profile = self.all_profiles[[self.case]].fillna(0)
        self.model: Model = Model.open(filename=self.model_path, units=Units.FIELD)
        self.well_lists = self.profile.index.to_list()
        self.do_units_conversion = do_units_conversion
        self.logger.info(
            f"Model prepared\n Case:{self.case}\n Condition: {self.condition.index[0]}"
        )

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
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        ]
        self.profile_variables = [
            ProfileVariables.PRESSURE,
            ProfileVariables.PRESSURE_GRADIENT_FRICTION,
            ProfileVariables.EROSIONAL_VELOCITY_RATIO,
            ProfileVariables.EROSIONAL_VELOCITY,
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

    def convert_units(self):
        self.logger.info(f"Converting units.....")
        if self.do_units_conversion:
            # Convert units in self.node_results
            self.node_results.iloc[
                1:, self.node_results.columns.get_loc("Pressure")
            ] = (
                self.node_results.iloc[
                    1:, self.node_results.columns.get_loc("Pressure")
                ]
                - 14.7
            ) / 14.5038
            self.node_results.iloc[
                0, self.node_results.columns.get_loc("Pressure")
            ] = "barg"

            self.node_results.iloc[
                1:, self.node_results.columns.get_loc("Temperature")
            ] = (
                self.node_results.iloc[
                    1:, self.node_results.columns.get_loc("Temperature")
                ]
                - 32
            ) / 1.8
            self.node_results.iloc[
                0, self.node_results.columns.get_loc("Temperature")
            ] = "C"

            # Convert units in self.profile_results

            # Pressure psia to barg
            self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("Pressure")
            ] = (
                self.profile_results.iloc[
                    1:, self.profile_results.columns.get_loc("Pressure")
                ]
                - 14.7
            ) / 14.5038
            self.profile_results.iloc[
                0, self.profile_results.columns.get_loc("Pressure")
            ] = "barg"

            # PressureGradientFriction psi/ft to bar/100m
            self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("PressureGradientFriction")
            ] = self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("PressureGradientFriction")
            ] * (
                14.5038 / (0.3048 / 100)
            )
            self.profile_results.iloc[
                0, self.profile_results.columns.get_loc("PressureGradientFriction")
            ] = "bar/100m"

            # Elevation ft to m
            self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("Elevation")
            ] = (
                self.profile_results.iloc[
                    1:, self.profile_results.columns.get_loc("Elevation")
                ]
                * 0.3048
            )
            self.profile_results.iloc[
                0, self.profile_results.columns.get_loc("Elevation")
            ] = "m"

            # ErosionalVelocity ft/s to m/s
            self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("ErosionalVelocity")
            ] = (
                self.profile_results.iloc[
                    1:, self.profile_results.columns.get_loc("ErosionalVelocity")
                ]
                * 0.3048
            )
            self.profile_results.iloc[
                0, self.profile_results.columns.get_loc("ErosionalVelocity")
            ] = "m/s"

            # TotalDistance ft to m
            self.profile_results.iloc[
                1:, self.profile_results.columns.get_loc("TotalDistance")
            ] = (
                self.profile_results.iloc[
                    1:, self.profile_results.columns.get_loc("TotalDistance")
                ]
                * 0.3048
            )
            self.profile_results.iloc[
                0, self.profile_results.columns.get_loc("TotalDistance")
            ] = "m"

    def write_results_to_excel(self):
        sheet_name = f"{self.case}_{self.condition.index.to_list()[0]}"
        node_results_sheet_name = f"{sheet_name}_NR"
        profile_results_sheet_name = f"{sheet_name}_PR"
        self.excel_handler.write_excel(
            df=self.node_results,
            sheet_name=node_results_sheet_name,
            range="A1",
            clear_sheet=True,
        )
        self.excel_handler.write_excel(
            df=self.profile_results,
            sheet_name=profile_results_sheet_name,
            range="A1",
            clear_sheet=True,
        )
        self.logger.info(f"Results written to excel")

    def saveAs_newModel(self):
        new_file = (
            Path(self.folder_directory)
            / f"{self.case}_{self.condition.index.to_list()[0]}_{self.model_filename}"
        )
        self.model.save(new_file)
        self.logger.info(f"Model saved as {new_file}")

    def close_model(self):
        self.model.close()
        self.logger.info(
            f"------------Network Simulation Object Closed----------------\n"
        )

    def run_app(
        self,
        source_name,
        pump_name,
        case=None,
        condition=None,
        do_units_conversion=False,
    ):
        try:
            self.prepare_model(
                case=case, condition=condition, do_units_conversion=do_units_conversion
            )
            self.set_global_conditions(source_name=source_name, pump_name=pump_name)
            self.get_boundary_conditions()
            self.get_well_values()
            self.activate_all_wells()
            self.deactivate_noflow_wells()
            self.populate_flowrates_in_model_from_excel()
            self.run_simulation()
            self.process_results()
            self.convert_units()
            self.write_results_to_excel()
            self.saveAs_newModel()
            self.close_model()
        except Exception as e:
            self.logger.error(traceback.format_exc())
            self.logger.error(e)
            self.model.close()
            raise e
