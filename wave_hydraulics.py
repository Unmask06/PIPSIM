import json
import logging
import os
import traceback
from pathlib import Path

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units

from core import NetworkSimulation, PipSimInput

with open("config.json", "r") as f:
    config = json.load(f)

try:
    config = PipSimInput(**config)
    FOLDER_DIRECTORY = config.FOLDER_DIRECTORY
    MODEL_FILENAME = config.MODEL_FILENAME
    EXCEL_FILE = config.EXCEL_FILE
    SOURCE_NAME = config.SOURCE_NAME
    PUMP_NAME = config.PUMP_NAME
except Exception as e:
    logging.error(e)

# Constants


# ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)

# pipsim_files = [file for file in os.listdir(FOLDER_DIRECTORY) if file.endswith(".pips")]
# pipsim_files = pipsim_files[1:]
# for MODEL_FILENAME in pipsim_files:
#     ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)
#     ns.open_model()
#     ns.get_boundary_conditions()
#     ns.run_simulation()
#     ns.model.save()
#     ns.process_results()
#     ns.do_units_conversion = True
#     ns.convert_units()
#     ns.write_results_to_excel(update=True)
