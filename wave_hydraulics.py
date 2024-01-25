import logging
import traceback

import pandas as pd
import xlwings as xw
from sixgill.definitions import *
from sixgill.pipesim import Model, Units

from network_simulation import NetworkSimulation, dict_to_df

# Constants
FOLDER_DIRECTORY = r"c:\Users\IDM252577\Desktop\Python Projects\PIPSIM"
MODEL_FILENAME = "BAB HP.pips"
EXCEL_FILE = "Water Injection Profile for BAB HP.xlsx"

SOURCE_NAME: str = "Sea Water Supply"
PUMP_NAME: list = ["HP Pump", "HP PUMP 2"]

ns = NetworkSimulation(FOLDER_DIRECTORY, MODEL_FILENAME, EXCEL_FILE)

for case in ns.all_profiles.columns:
    for condition in ns.all_conditions.index:
        try:
            ns.run_app(source_name=SOURCE_NAME, pump_name=PUMP_NAME, case=case, condition=condition)
        except:
            traceback.print_exc()
            continue
