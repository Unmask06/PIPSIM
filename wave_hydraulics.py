"""wave_hydraulics"""
import json
import logging
import os
import sys

# import traceback
from pydantic import ValidationError

from core import (
    NetworkSimulation,
    NetworkSimulationError,
    NetworkSimulationSummary,
    PipSimInput,
    SummaryError,
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


def wave_create_model(config: PipSimInput) -> None:
    """Create a new model based on the given configuration."""
    ns = NetworkSimulation(
        config.FOLDER_DIRECTORY, config.MODEL_FILENAME, config.EXCEL_FILE
    )
    ns.initialize_excel_handler(config.PIPSIM_INPUT_SHEET, config.CONDITIONS_SHEET)
    for case in ns.cases:
        for condition in ns.conditions:
            ns.create_model(
                source_name=config.SOURCE_NAME,
                pump_name=config.PUMP_NAME,
                case=case,
                condition=condition,
            )


def wave_run_model(config: PipSimInput) -> None:
    """Run an existing model based on the given configuration."""
    pipsim_files = [
        file for file in os.listdir(config.FOLDER_DIRECTORY) if file.endswith(".pips")
    ]
    pipsim_files.remove(str(config.MODEL_FILENAME))
    for model_filename in pipsim_files:
        try:
            ns = NetworkSimulation(
                config.FOLDER_DIRECTORY, model_filename, config.EXCEL_FILE
            )
            ns.initialize_excel_handler(
                config.PIPSIM_INPUT_SHEET, config.CONDITIONS_SHEET
            )
            ns.run_existing_model()
        except NetworkSimulationError as e:
            logger.error(f"Error in running model {model_filename}: {e}")
            continue


def wave_summarize_results(config: PipSimInput) -> None:
    """Summarize the results of the model Node and Profile Results."""
    try:
        netsimsum = NetworkSimulationSummary()
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
        # traceback.print_exc()
        sys.exit(1)


def exit_program() -> None:
    logger.info("Exiting the program.")
    sys.exit(0)


def main() -> None:
    config = load_config("inputs.json")

    while True:
        response = input(
            "Do you want to \n"
            "(1) create a new model \n"
            "(2) run an existing model \n"
            "(3) Create summary for the results\n"
            "(4) to exit: "
        )

        action = {
            "1": wave_create_model,
            "2": wave_run_model,
            "3": wave_summarize_results,
            "4": exit_program,
        }
        try:
            if response == "4":
                action[response]()
            else:
                action[response](config)
        except KeyError:
            print("Invalid option. Please choose 1, 2, 3, or 4.")
            continue


if __name__ == "__main__":
    main()
