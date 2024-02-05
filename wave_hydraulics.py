import json
import logging
import os
import traceback
from pathlib import Path
from typing import Dict, List

import pandas as pd
import xlwings as xw
from pydantic import ValidationError
from sixgill.definitions import *
from sixgill.pipesim import Model, Units

from core import NetworkSimulation, PipSimInput

logger = logging.getLogger("Hydraulics")

with open("inputs.json", "r") as f:
    config = json.load(f)

try:
    config = PipSimInput(**config)
    FOLDER_DIRECTORY = config.FOLDER_DIRECTORY
    MODEL_FILENAME = config.MODEL_FILENAME
    EXCEL_FILE = config.EXCEL_FILE
    PIPSIM_INPUT_SHEET = config.PIPSIM_INPUT_SHEET
    CONDITIONS_SHEET = config.CONDITIONS_SHEET
    SOURCE_NAME = config.SOURCE_NAME
    PUMP_NAME = config.PUMP_NAME
except (ValidationError, KeyError) as e:
    logging.error(e)


def wave_create_model():
    ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)
    ns.initialize_excel_handler(PIPSIM_INPUT_SHEET, CONDITIONS_SHEET)
    for case in ns.cases:
        for condition in ns.conditions:
            ns.create_model(
                source_name=SOURCE_NAME,
                pump_name=PUMP_NAME,
                case=case,
                condition=condition,
            )


def wave_run_model():
    pipsim_files = [
        file for file in os.listdir(FOLDER_DIRECTORY) if file.endswith(".pips")
    ]
    pipsim_files = pipsim_files[1:]
    for MODEL_FILENAME in pipsim_files:
        ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)
        ns.initialize_excel_handler(PIPSIM_INPUT_SHEET, CONDITIONS_SHEET)
        ns.run_existing_model(source_name=SOURCE_NAME, pump_name=PUMP_NAME)



while True:
    response = input(
        "Do you want to \n (1) create a new model,\n (2) run an existing model, (3) create and run a new model?\n (4) to exit: "
    )

    if response == "1":
        wave_create_model()

    elif response == "2":
        wave_run_model()

    elif response == "3":
        wave_create_model()
        wave_run_model()

    elif response == "4":
        break

    else:
        print("Invalid option. Please choose 1, 2,3 or 4")
