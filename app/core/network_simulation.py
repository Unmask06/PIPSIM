# network_simulation.py
"""
This module contains the NetworkSimulator class for performing network simulation 
using the Pipesim model.
"""

import logging
import traceback
from pathlib import Path
from typing import List, Optional

import pandas as pd
from sixgill.definitions import (
    ModelComponents,
    Parameters,
    ProfileVariables,
    SystemVariables,
)
from sixgill.pipesim import Model, Units

from app.core import NetworkSimulationError
from app.core.excel_handling import ExcelHandler, ExcelHandlerError

logger = logging.getLogger(__name__)


class NetworkSimulator:
    """
    Performs network simulation using the Pipesim model.

    Attributes:
        model_path (str): Path to the Pipesim model file.
        system_variables (list): List of system variables to retrieve.
        profile_variables (list): List of profile variables to retrieve.
        node_results (Optional[pd.DataFrame]): DataFrame containing node simulation results.
        profile_results (Optional[pd.DataFrame]): DataFrame containing profile simulation results.
    """

    NODE_RESULTS_xl = "Node_Results.xlsx"
    PROFILE_RESULTS_xl = "Profile_Results.xlsx"
    node_results_file: str
    profile_results_file: str
    boundary_conditions: pd.DataFrame
    MIN_FLOWRATE = 0.01

    def __init__(
        self,
        model_path: str,
        system_variables: Optional[List[str]] = None,
        profile_variables: Optional[List[str]] = None,
        unit: str = Units.METRIC,
        folder: str = "",
    ) -> None:
        logger.info("🚀 Intializing Network Simulation Workflow !!")
        self.model_path = model_path
        self.model = Model.open(model_path, units=unit)
        self.system_variables = system_variables or [
            SystemVariables.TYPE,
            SystemVariables.PRESSURE,
            SystemVariables.TEMPERATURE,
            SystemVariables.DELTA_PRESSURE,
            SystemVariables.TYPE,
        ]
        self.profile_variables = profile_variables or [
            ProfileVariables.PRESSURE,
            ProfileVariables.TEMPERATURE,
            ProfileVariables.MEAN_VELOCITY_FLUID,
            ProfileVariables.EROSIONAL_VELOCITY,
        ]
        self.unit = unit
        self.node_results: Optional[pd.DataFrame] = None
        self.profile_results: Optional[pd.DataFrame] = None
        self.folder = folder

    def deactivate_lowflow_sinks(self) -> None:
        """Deactivates low flow sinks in the Pipesim model."""
        sinks = self.model.get_values(component=ModelComponents.SINK)
        for sink_name, sink_data in sinks.items():
            try:
                flowrate_type = sink_data.get(Parameters.Sink.FLOWRATETYPE)
                if not sink_data.get(flowrate_type):
                    continue
                if sink_data.get(flowrate_type) < self.MIN_FLOWRATE:
                    sink_data[Parameters.Sink.ISACTIVE] = False
                    sinks[sink_name] = sink_data
                    logger.info(f"Deactivated sink: {sink_name} due to low flowrate.")
            except Exception as e:
                logger.error(f"Error deactivating sink {sink_name}: {e}")
        self.model.set_values(dict=sinks)
        self.model.save()

    def run_simulation(self) -> None:
        """Runs the network simulation using Pipesim."""
        if self.model.tasks.networksimulation.validate():  # type: ignore
            raise NetworkSimulationError(
                "Model validation unsuccessful.", self.model_path
            )

        self.model.tasks.networksimulation.reset_conditions()  # type: ignore
        self.results = self.model.tasks.networksimulation.run(  # type: ignore
            system_variables=self.system_variables,
            profile_variables=self.profile_variables,
        )
        logger.info("Simulation completed successfully.")

    def process_node_results(self) -> None:
        """Processes the node results from the simulation."""
        if not hasattr(self, "results") or self.results is None:
            raise NetworkSimulationError(
                "Simulation results not available.", self.model_path
            )

        self.node_results = pd.DataFrame.from_dict(self.results.node)

        if self.node_results.empty:
            raise NetworkSimulationError(
                "Simulation produced no node results.", self.model_path
            )

        self.node_results.reset_index(inplace=True)
        self.node_results.rename(columns={"index": "Node"}, inplace=True)

        self.node_results[SystemVariables.TYPE] = self.node_results["Node"].apply(
            lambda well: (
                self.boundary_conditions.loc["BoundaryNodeType", well]
                if well in self.boundary_conditions.columns
                else None
            )
        )

        unit_row = self.node_results.loc[self.node_results["Node"] == "Unit"].index
        unit_row = self.node_results.loc[unit_row]
        self.node_results = self.node_results.drop(unit_row.index)
        self.node_results.sort_values(
            by=[SystemVariables.TYPE, "Node"], ascending=[False, True], inplace=True
        )
        self.node_results = pd.concat([unit_row, self.node_results], ignore_index=True)

        cols = ["Node"] + [
            col
            for col in self.node_results.columns
            if col not in ["Node", SystemVariables.TYPE]
        ]
        self.node_results = self.node_results[cols]

        logger.info("Node results processed successfully.")

    def process_profile_results(self) -> None:
        """Processes the profile results from the simulation."""
        if not hasattr(self, "results") or self.results is None:
            raise NetworkSimulationError(
                "Simulation results not available.", self.model_path
            )

        units = pd.DataFrame(self.results.profile_units, index=["Units"])
        dfs = []

        for branch, branch_data in sorted(self.results.profile.items()):
            try:
                branch_df = pd.DataFrame.from_dict(branch_data)
                branch_df["BranchEquipment"] = branch_df["BranchEquipment"].ffill()
                unique_rows = branch_df.drop_duplicates(
                    subset=["BranchEquipment"], keep="last"
                )
                unique_rows.insert(0, "Branch", branch)
                dfs.append(unique_rows)
            except Exception as e:
                logger.error(f"Error processing branch {branch}: {e}")

        combined_df = pd.concat(dfs, ignore_index=True)
        combined_df.sort_values(by=["Branch", "BranchEquipment"], inplace=True)
        self.profile_results = pd.concat([units, combined_df], ignore_index=True)

        cols = ["Branch", "BranchEquipment"] + [
            col
            for col in self.profile_results.columns
            if col not in ["Branch", "BranchEquipment"]
        ]
        self.profile_results = self.profile_results[cols]
        logger.info("Profile results processed successfully.")

    def write_results_to_excel(self) -> None:
        """Writes simulation results to Excel files."""
        if self.node_results is None or self.profile_results is None:
            raise NetworkSimulationError(
                "Results are not available to write to Excel.", self.model_path
            )

        sheet_name = Path(self.model_path).stem[:31]

        results_dir = Path(self.folder) / "Results"
        if not results_dir.exists():
            results_dir.mkdir()

        self.node_results_file = str(results_dir / self.NODE_RESULTS_xl)
        self.profile_results_file = str(results_dir / self.PROFILE_RESULTS_xl)

        ExcelHandler.write_excel(
            df=self.node_results,
            sheet_name=sheet_name,
            clear_sheet=True,
            sht_range="A2",
            workbook=self.node_results_file,
        )

        ExcelHandler.write_excel(
            df=self.profile_results,
            sheet_name=sheet_name,
            clear_sheet=True,
            workbook=self.profile_results_file,
        )

        logger.info("Results written to Excel successfully.")

    def get_boundary_conditions(self) -> None:
        """Retrieves boundary conditions from the Pipesim model."""
        self.boundary_conditions = pd.DataFrame.from_dict(
            self.model.tasks.networksimulation.get_conditions()  # type: ignore
        )
        logger.info("Boundary conditions retrieved successfully.")

    def run_existing_model(self) -> None:
        """Runs an existing Pipesim model and processes results."""
        try:
            logger.info(f"Running simulation for model: \n {self.model_path}")
            self.get_boundary_conditions()
            self.deactivate_lowflow_sinks()
            self.run_simulation()
            self.process_node_results()
            self.process_profile_results()
            self.write_results_to_excel()
            self.model.save()
            logger.info("✅ Network simulation completed successfully.")

        except (NetworkSimulationError, ExcelHandlerError) as e:
            logger.error(e)

        except Exception as e:
            logger.error(f"An error occurred during simulation: {e}")
        finally:
            self.model.close()
