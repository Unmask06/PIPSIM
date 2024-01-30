import os
import logging
import traceback

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units

from network_simulation import NetworkSimulation, dict_to_df

# Constants
FOLDER_DIRECTORY = r"c:\Users\IDM252577\Desktop\Python Projects\PIPSIM"
# MODEL_FILENAME = "BAB HP.pips"
EXCEL_FILE = "Water Injection Profile for BAB HP.xlsx"

SOURCE_NAME: str = "Sea Water Supply"
PUMP_NAME: list = ["HP Pump", "HP PUMP 2"]

# ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)

pipsim_files = [file for file in os.listdir(FOLDER_DIRECTORY) if file.endswith(".pips")]
pipsim_files = pipsim_files[1:]
for MODEL_FILENAME in pipsim_files:
    ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)
    ns.open_model()
    ns.get_boundary_conditions()
    ns.run_simulation()
    ns.model.save()
    ns.process_results()
    ns.do_units_conversion = True
    ns.convert_units()
    ns.write_results_to_excel(update=True)
