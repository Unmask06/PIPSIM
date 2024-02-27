import json
import logging
import os
import sys
from typing import NoReturn

from pydantic import ValidationError

from core import ExcelHandler, NetworkSimulation, PipSimInput

logger = logging.getLogger("Hydraulics")


def load_config(file_path: str) -> PipSimInput:
    """Load and validate configuration from a JSON file."""
    try:
        with open(file_path, "r") as f:
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
            f"Error in the configuration file: \n {e} \n make sure to use '/' or '\\\\' in the file path"
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
            ns.run_existing_model(
                source_name=config.SOURCE_NAME, pump_name=config.PUMP_NAME
            )
        except Exception as e:
            logger.error(f"Error in running model {model_filename}: {e}")
            continue


def main() -> None:
    config = load_config("inputs.json")

    while True:
        response = input(
            "Do you want to \n (1) create a new model,\n (2) run an existing model,\n (3) create and run a new model?\n (4) to exit: "
        )

        if response == "1":
            wave_create_model(config)

        elif response == "2":
            wave_run_model(config)

        elif response == "3":
            wave_create_model(config)
            wave_run_model(config)

        elif response == "4":
            break

        else:
            print("Invalid option. Please choose 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
