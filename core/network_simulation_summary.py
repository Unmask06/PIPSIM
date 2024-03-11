# network_simulation_summary.py
import logging
from os import error
from pathlib import Path

import numpy as np
import pandas as pd
import xlwings as xw
from sixgill.definitions import *  # type: ignore

from core import ExcelHandler, NetworkSimulation

parameters = [
    ProfileVariables.EROSIONAL_VELOCITY_RATIO,
    ProfileVariables.MEAN_VELOCITY_FLUID,
]


class NetworkSimulationSummary:
    def __init__(
        self,
        node_result_xl: str = NetworkSimulation.NODE_RESULTS_FILE,
        profile_result_xl: str = NetworkSimulation.PROFILE_RESULTS_FILE,
    ) -> None:
        self.logger = logging.getLogger(__name__)

        if not Path(node_result_xl).is_file():
            raise FileNotFoundError(f"File not found: {node_result_xl}")
        if not Path(profile_result_xl).is_file():
            raise FileNotFoundError(f"File not found: {profile_result_xl}")

        self.node_result_xl = node_result_xl
        self.profile_result_xl = profile_result_xl

    @staticmethod
    def get_min_max_parameter(
        df: pd.DataFrame, case: str, parameter: str, equipment_column: str
    ):
        df[parameter] = pd.to_numeric(df[parameter], errors="coerce")
        min_parameter_idx = df[parameter].idxmin()
        max_parameter_idx = df[parameter].idxmax()

        df.loc[min_parameter_idx, "Min/Max"] = "Minimum"
        df.loc[max_parameter_idx, "Min/Max"] = "Maximum"
        df["Case"] = case

        max_min_results = pd.concat(
            [df.loc[[min_parameter_idx]], df.loc[[max_parameter_idx]]]
        )
        max_min_results = max_min_results[
            [equipment_column, parameter, "Min/Max", "Case"]
        ]

        return max_min_results

    @staticmethod
    def get_pump_operating_point(
        df: pd.DataFrame, case: str, suction_node: str, discharge_node: str
    ):
        try:
            pump_op_df = pd.DataFrame(
                data=np.nan,
                columns=[
                    "Case",
                    "Suction Pressure",
                    "Discharge Pressure",
                    "Pump Head",
                    "Pump Flow",
                ],
                index=[0],
            )
            pump_op_df["Case"] = case

            pump_op_df["Suction Pressure"] = df.loc[
                df["BranchEquipment"] == suction_node, "Pressure"
            ].values[0]

            pump_op_df["Discharge Pressure"] = df.loc[
                df["BranchEquipment"] == discharge_node, "Pressure"
            ].values[0]

            pump_op_df["Pump Head"] = (
                pump_op_df["Discharge Pressure"] - pump_op_df["Suction Pressure"]
            )
        except IndexError:
            err_msg = (
                f"Error in getting pump operating points for '{suction_node}' and '{discharge_node}' in {case}.\n"
                "Check if the Pump and Strainer in 'inputs.json' file is in the Profile Results.xlsx are present in the profile results."
            )
            raise IndexError(err_msg)

        return pump_op_df

    def get_node_summary(self):
        self.logger.info("Getting Node Summary.....")
        with xw.App(visible=False) as app:
            node_wb = xw.Book(self.node_result_xl)
            node_sheets = [
                sheet.name for sheet in node_wb.sheets if sheet.name != "Node Summary"
            ]

            node_summary_list = []
        for sht in node_sheets:
            try:
                node_df = pd.read_excel(self.node_result_xl, sheet_name=sht, header=1)
                node_df = node_df.loc[node_df["Type"] == "Sink"]
                node_df = NetworkSimulationSummary.get_min_max_parameter(
                    df=node_df, case=sht, parameter="Pressure", equipment_column="Node"
                )
                node_summary_list.append(node_df)
            except Exception as e:
                err = f"Error in getting node summary for {sht}: {e}"
                raise Exception(err)

        node_summary = pd.concat(node_summary_list, ignore_index=True)
        self.node_summary = node_summary
        self.node_summary["Operation"] = np.where(
            self.node_summary["Case"].str.contains("-EO"),
            "Early Operation",
            "Late Operation",
        )
        self.node_summary.sort_values(by=["Operation", "Pressure"], inplace=True)
        self.node_summary.reset_index(drop=True, inplace=True)

    def get_profile_summary(self):
        self.logger.info("Getting Profile Summary.....")
        profile_wb = xw.Book(self.profile_result_xl)
        self.profile_sheets = [
            sheet.name
            for sheet in profile_wb.sheets
            if sheet.name not in parameters + ["Pump Operating Points"]
        ]
        self.profile_summary_list = {}
        for parameter in parameters:
            try:
                profile_summaries = []
                for sht in self.profile_sheets:
                    try:
                        profile_df = pd.read_excel(
                            self.profile_result_xl, sheet_name=sht, header=1
                        )
                        profile_df = NetworkSimulationSummary.get_min_max_parameter(
                            df=profile_df,
                            case=sht,
                            parameter=parameter,
                            equipment_column="BranchEquipment",
                        )
                        profile_summaries.append(profile_df)
                    except KeyError as ke:
                        if not sht in parameters:
                            error_msg = f"Error in getting profile summary for parameter: {parameter} in {sht}"
                            logging.warning(error_msg)

                summary_df = pd.concat(profile_summaries, ignore_index=True)

                self.profile_summary_list[parameter] = summary_df
                
            except Exception as e:
                logging.error(f"Error in getting profile summary for {parameter}: {e}")
                raise e

    def get_pump_operating_points(self, suction_node, discharge_node):
        self.logger.info("Getting Pump Operating Points.....")
        pump_operating_points_dfs = []
        for sht in self.profile_sheets:
            try:
                df = pd.read_excel(self.profile_result_xl, sheet_name=sht, header=1)
                pump_op_df = NetworkSimulationSummary.get_pump_operating_point(
                    df, sht, suction_node, discharge_node
                )
                pump_operating_points_dfs.append(pump_op_df)
            except KeyError as ke:
                logging.error(f"Error in getting pump operating points for {sht}: {ke}")
        self.pump_operating_points = pd.concat(
            pump_operating_points_dfs, ignore_index=True
        )
        self.pump_operating_points["Operation"] = np.where(
            self.pump_operating_points["Case"].str.contains("-EO"),
            "Early Operation",
            "Late Operation",
        )
        self.pump_operating_points.sort_values(by=["Operation", "Case"], inplace=True)
        self.pump_operating_points.reset_index(drop=True, inplace=True)

    def write_node_summary(self):
        self.logger.info("Writing Node Summary.....")
        ExcelHandler.write_excel(
            self.node_summary,
            self.node_result_xl,
            "Node Summary",
            range="A2",
            clear_sheet=True,
        )

    def write_profile_summary(self):
        self.logger.info("Writing Profile Summary.....")
        for parameter, df in self.profile_summary_list.items():
            df.sort_values(by=[parameter], inplace=True)
            df.reset_index(drop=True, inplace=True)
            ExcelHandler.write_excel(
                df,
                self.profile_result_xl,
                sheet_name=parameter,
                range="A2",
                clear_sheet=True,
            )

    def write_pump_operating_points(self):
        self.logger.info("Writing Pump Operating Points.....")
        ExcelHandler.write_excel(
            self.pump_operating_points,
            self.profile_result_xl,
            sheet_name="Pump Operating Points",
            range="A2",
            clear_sheet=True,
        )
