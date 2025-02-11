"""network_simulation_summary"""

import logging
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
import xlwings as xw
from sixgill.definitions import ProfileVariables, SystemVariables

from app.core import ExcelHandler, NetworkSimulator

logger = logging.getLogger(__name__)


class SummaryError(Exception):
    """Exception raised for errors in the summary generation."""

    def __init__(self, message, filename=None, sheetname=None):
        self.message = message
        self.filename = filename
        self.sheetname = sheetname
        super().__init__(f"{message} | File: {filename}, Sheet: {sheetname}")


class NetworkSimulationSummary:
    def __init__(
        self,
        node_result_xl: str,
        profile_result_xl: str,
        node_parameters: list,
        profile_parameters: list,
    ) -> None:
        if not Path(node_result_xl).is_file():
            raise FileNotFoundError(f"File not found: {node_result_xl}")
        if not Path(profile_result_xl).is_file():
            raise FileNotFoundError(f"File not found: {profile_result_xl}")

        self.node_result_xl = node_result_xl
        self.profile_result_xl = profile_result_xl
        self.node_parameters = node_parameters
        self.profile_parameters = profile_parameters
        self.node_summary
        self.profile_summary_list = {}
        self.node_results: Dict[str, pd.DataFrame] = pd.read_excel(
            node_result_xl, sheet_name=None
        )

    def validate_parameter(
        self, df: pd.DataFrame, parameter: str, filename: str, sheetname: str
    ):
        if parameter not in df.columns:
            raise SummaryError(
                f"Parameter '{parameter}' not found in DataFrame.", filename, sheetname
            )

    def get_min_max_parameters(
        self,
        df: pd.DataFrame,
        case: str,
        parameters: list,
        equipment_column: str,
        filename: str,
        sheetname: str,
    ):
        df = df.copy()
        result_list = []
        for parameter in parameters:
            self.validate_parameter(df, parameter, filename, sheetname)
            df[parameter] = pd.to_numeric(df[parameter], errors="coerce")
            min_idx = df[parameter].idxmin()
            max_idx = df[parameter].idxmax()
            df.loc[min_idx, "Min/Max"] = "Minimum"
            df.loc[max_idx, "Min/Max"] = "Maximum"
            df["Case"] = case
            result_list.append(
                df.loc[
                    [min_idx, max_idx], [equipment_column, parameter, "Min/Max", "Case"]
                ]
            )
        return pd.concat(result_list, ignore_index=True)

    def get_node_summary(self):
        logger.info("Getting Node Summary...")
        with xw.App(visible=False) as app:
            node_wb = xw.Book(self.node_result_xl)
            node_sheets = [
                sheet.name for sheet in node_wb.sheets if sheet.name != "Node Summary"
            ]
            node_summary_list = []
            for sht in node_sheets:
                try:
                    node_df = pd.read_excel(
                        self.node_result_xl, sheet_name=sht, header=1, index_col=0
                    )
                    node_summary_list.append(
                        self.get_min_max_parameters(
                            node_df,
                            sht,
                            self.node_parameters,
                            "Node",
                            self.node_result_xl,
                            sht,
                        )
                    )
                except SummaryError as exc:
                    logger.error(exc)
                    raise
        self.node_summary = pd.concat(node_summary_list, ignore_index=True)
        self.node_summary.sort_values(by=[ProfileVariables.PRESSURE], inplace=True)
        self.node_summary.reset_index(drop=True, inplace=True)

    def get_profile_summary(self):
        logger.info("Getting Profile Summary...")
        with xw.App(visible=False) as app:
            profile_wb = xw.Book(self.profile_result_xl)
            profile_sheets = [
                sheet.name
                for sheet in profile_wb.sheets
                if sheet.name not in self.profile_parameters + ["Pump Operating Points"]
            ]
            for parameter in self.profile_parameters:
                try:
                    profile_summaries = []
                    for sht in profile_sheets:
                        profile_df = pd.read_excel(
                            self.profile_result_xl,
                            sheet_name=sht,
                            header=1,
                            index_col=0,
                        )
                        profile_summaries.append(
                            self.get_min_max_parameters(
                                profile_df,
                                sht,
                                [parameter],
                                "BranchEquipment",
                                self.profile_result_xl,
                                sht,
                            )
                        )
                    self.profile_summary_list[parameter] = pd.concat(
                        profile_summaries, ignore_index=True
                    )
                except SummaryError as exc:
                    logger.error(exc)
                    raise

    def write_node_summary(self):
        if self.node_summary is not None:
            logger.info("Writing Node Summary...")
            ExcelHandler.write_excel(
                self.node_summary,
                self.node_result_xl,
                "Node Summary",
                sht_range="A2",
                clear_sheet=True,
            )

    def write_profile_summary(self):
        if self.profile_summary_list:
            logger.info("Writing Profile Summary...")
            for parameter, df in self.profile_summary_list.items():
                ExcelHandler.write_excel(
                    df,
                    self.profile_result_xl,
                    parameter,
                    sht_range="A2",
                    clear_sheet=True,
                )
