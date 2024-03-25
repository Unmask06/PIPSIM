"""wave_hydraulics"""

import json
import logging
import os
import sys

# import traceback
from pydantic import ValidationError

from core.input_validation import PipSimInput
from core.inputdata import InputData
from core.network_simulation import NetworkSimulationError, NetworkSimulator
from core.network_simulation_summary import NetworkSimulationSummary, SummaryError
from core.simulation_modeller import (
    ModelInput,
    PipsimModel,
    PipsimModeller,
    PipsimModellingError,
)

logger = logging.getLogger(__name__)


def load_config(file_path: str) -> PipSimInput:
    """Load and validate configuration from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            config_dict = json.load(f)
        config = PipSimInput(**config_dict)
        logger.info("Input file loaded successfully.")
        return config

    except ValidationError as e:
        logger.error(f"Error in the configuration file: \n {e}")
        sys.exit(1)

    except FileNotFoundError:
        logger.error(f"Configuration file '{file_path}' not found.")
        sys.exit(1)

    except json.decoder.JSONDecodeError as e:
        logger.error(
            f"Error in the configuration file: \n {e} \n"
            f"make sure to use '/' or '\\\\' in the file path"
        )
        sys.exit(1)


def load_input_data(config: PipSimInput) -> InputData:
    """Load and validate input data from an Excel file."""
    input_data = InputData(
        excelfile=config.EXCEL_FILE,
        well_profile_sheet=config.PIPSIM_INPUT_SHEET,
        well_profile_starting_range="A4",
        conditions_sheet=config.CONDITIONS_SHEET,
        conditions_starting_range="A2",
    )

    return input_data


def wave_create_model(config: PipSimInput, input_data: InputData) -> None:
    """Create a new model based on the given configuration."""
    for case, condition in input_data.case_conditions:

        ambient_temperature = input_data.get_parameter_for_condition(
            condition=condition, param="Ambient Temperature"
        )
        source_pressure = input_data.get_parameter_for_condition(
            condition=condition, param="Source Pressure"
        )
        source_temperature = input_data.get_parameter_for_condition(
            condition=condition, param="Temperature"
        )
        differential_pressure = input_data.get_parameter_for_condition(
            condition=condition, param="PressureDifferential"
        )

        model_input = ModelInput(
            source_name=config.SOURCE_NAME,
            pump_name=config.PUMP_NAME,
            well_profile=input_data.well_profile,
            ambient_temperature=ambient_temperature,
            source_pressure=source_pressure,
            source_temperature=source_temperature,
            differential_pressure=differential_pressure,
        )

        model = PipsimModel(
            model_filename=config.MODEL_FILENAME, case=case, condition=condition
        )

        try:
            pipsim_modeller = PipsimModeller(model=model, model_input=model_input)
            pipsim_modeller.build_model()
            logger.info(f"Model for {case} - {condition} created successfully.")
        except PipsimModellingError as e:
            logger.error(f"Error in creating model for {case} - {condition}: {e}")
            continue


def wave_run_model(config: PipSimInput) -> None:
    """Run an existing model based on the given configuration."""
    pipsim_files = [
        file for file in os.listdir(config.FOLDER_DIRECTORY) if file.endswith(".pips")
    ]
    pipsim_files.remove(str(config.MODEL_FILENAME))
    # pipsim_files = pipsim_files[:1]
    for model_filename in pipsim_files:
        try:
            model = PipsimModel(model_filename=model_filename)
            model_input = ModelInput()
            ns = NetworkSimulator(model=model, model_input=model_input)
            ns.run_existing_model()
        except PipsimModellingError as e:
            logger.error(f"Error in {model_filename}: {e}")
            continue
        except NetworkSimulationError as e:
            logger.error(f"Error in running model {model_filename}: {e}")
            continue


def wave_summarize_results(config: PipSimInput) -> None:
    """Summarize the results of the model Node and Profile Results."""
    try:
        node_result_xl = os.path.join(
            config.FOLDER_DIRECTORY, NetworkSimulator.NODE_RESULTS_FILE
        )
        profile_result_xl = os.path.join(
            config.FOLDER_DIRECTORY, NetworkSimulator.PROFILE_RESULTS_FILE
        )
        netsimsum = NetworkSimulationSummary(node_result_xl, profile_result_xl)
        netsimsum.get_node_summary()
        netsimsum.get_profile_summary()

        suction_node = config.STRAINER_NAME[0]
        discharge_node = config.PUMP_NAME[0]
        netsimsum.get_pump_operating_points(
            suction_node=suction_node, discharge_node=discharge_node
        )
        netsimsum.write_node_summary()
        netsimsum.write_profile_summary()
        netsimsum.write_pump_operating_points()
        logger.info("Summary written successfully.")
    except SummaryError as e:
        logger.error(f"Error in summarizing results: {e}")
        sys.exit(1)


def exit_program() -> None:
    logger.info("Exiting the program.")
    sys.exit(0)


def main() -> None:
    config = load_config("inputs.json")
    input_data = load_input_data(config)

    while True:
        response = input(
            "Do you want to \n"
            "(1) create a new model \n"
            "(2) run an existing model \n"
            "(3) Create summary for the results\n"
            "(0) to exit: "
        )
        if response == "0":
            exit_program()
        elif response == "1":
            wave_create_model(config, input_data)
        elif response == "2":
            wave_run_model(config)
        elif response == "3":
            wave_summarize_results(config)
        else:
            print("Invalid option. Please choose 1, 2, 3, or 0.")
            continue


if __name__ == "__main__":
    main()
