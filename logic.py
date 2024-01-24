'''
    Pipesim Python Toolkit Use Case Example
    Copyright 2023 SLB, all rights reserved

    The example is an integrated Excel / Python script for running a
    network simulation. The boundary conditions can be modified along
    with the equipment data.

'''
import sys
# Shared Python script and bat file are required for this example to work
sys.path.insert(0, '../_CommonScripts/')

import importlib
start_server_spec=importlib.util.find_spec("_server")
if start_server_spec is None:
    print("")
    sys.exit("The script has been terminated. Python scripts and .bat files from '_CommonScripts' folder are possibly missing. Copy them from 'Case Studies' folder and run the script again.")

from _server import start_server
        
# Import the functions for working with Pipesim
from sixgill.definitions import *
from sixgill.utilities import get_model_session, get_refers_to_range, range_to_dictionary
from sixgill.pipesim import Model
from manta.utils.logs import configure_logging
from manta.utils.logs import setup_console_logging
import subprocess

# Import the functions for working within Excel
import xlwings as xw
import pandas as pd

# Import the logging functionality and setup the message logger
import logging
logger = logging.getLogger(__name__)
import os


# And any other Python modules that we are going to use

# Going to define some referenced ranges in the workbook for ease of use
# Could be a cell reference (e.g. "A1") or a named range (e.g. "ModelFolder")

# Worksheet names
NETSIM_WORKSHEET = 'Network Simulation'
EQUIPMENT_WORKSHEET = 'Equipment Data'
RESULTS_WORKSHEET = 'Simulation Results'

# Where in the workbook the model folder and file name are maintained
PYTHON_FOLDER = "PythonFolder"
MODEL_FOLDER = "ModelFolder"
MODEL_FILE   = "ModelFile"

# Data locations on the worksheets
BOUNDARY_TABLE = "BoundaryConditions"
SIMULATION_STATUS = "SimulationStatus"
RESULTS_SYSTEM = "SystemResults"
RESULTS_NODE = "NodeResults"
RESULTS_PROFILE = "ProfileResults"
CHOKE_VALVES = "ChokeValves"
PUMPS = "Pumps"
COMPRESSORS = "Compressors"

SIMULATION_ID = None

# -----------------------------------------------------------------------------
# Connecting to the model
# -----------------------------------------------------------------------------
global model

def connect_model():
    folder = os.path.expanduser(get_refers_to_range(MODEL_FOLDER).value)
    file = get_refers_to_range(MODEL_FILE).value
    filename = os.path.join(folder, file)
    return get_model_session(filename)
    
# -----------------------------------------------------------------------------
# Updating the boundary conditions
# -----------------------------------------------------------------------------
def get_boundary_conditions():
    model = connect_model()
    ''' Retrieve the model boundaries and update the spreadsheet '''
    folder = os.path.expanduser(get_refers_to_range(MODEL_FOLDER).value)
    pythonFolder = os.path.expanduser(get_refers_to_range(PYTHON_FOLDER).value)
    file = get_refers_to_range(MODEL_FILE).value
    xw.sheets(NETSIM_WORKSHEET).clear_contents()
    get_refers_to_range("NSTitle").value = "Model Details"
    get_refers_to_range("Boundary").value = "Boundary Conditions"
    get_refers_to_range("ModelName").value = "Model Name"
    get_refers_to_range("ModelDirectory").value = "Model Directory"
    get_refers_to_range("PTK_Directory").value = "Python Directory"
    get_refers_to_range(MODEL_FOLDER).value = folder
    get_refers_to_range(MODEL_FILE).value = file
    get_refers_to_range(PYTHON_FOLDER).value = pythonFolder

    # Get DataFrame containing current network boundary conditions
    boundary_conditions = model.tasks.networksimulation.get_conditions()
    
    # Write the DataFrame contents to the worksheet
    bk = xw.books.active
    bk.sheets(NETSIM_WORKSHEET).activate()
    get_refers_to_range(BOUNDARY_TABLE).value = pd.DataFrame.from_dict(boundary_conditions)


def update_boundary_conditions():
    model = connect_model()
    ''' Update the model with the boundaries from the spreadsheet '''

    # Read in values from the Excel table of boundary conditions
    bk = xw.books.active
    bk.sheets(NETSIM_WORKSHEET).activate()
    boundary_conditions = get_refers_to_range(BOUNDARY_TABLE).expand().value
    boundary_dict = range_to_dictionary(boundary_conditions)

    # Update the boundary conditions in the model
    model.tasks.networksimulation.set_conditions(boundaries=boundary_dict)


# -----------------------------------------------------------------------------
#  Update Equipment Data
# -----------------------------------------------------------------------------
def get_equipment_data():
    model = connect_model()
    ''' Write the equipment data on to the equipment data sheet '''

    xw.sheets(EQUIPMENT_WORKSHEET).activate()

    #Clear contents of the worksheet
    xw.sheets(EQUIPMENT_WORKSHEET).clear_contents()
    get_refers_to_range("EDTitle").value = "Equipment Data"
    get_refers_to_range("Chokes").value = "Chokes"
    get_refers_to_range("PTitle").value = "Pumps"
    get_refers_to_range("CTitle").value = "Compressors"

    # Write out the choke data
    chokes = model.get_values(Choke=ALL, parameters=[
        Parameters.Choke.NAME, Parameters.Choke.BEANSIZE,
        Parameters.Choke.DISCHARGECOEFFICIENT
        ])

    get_refers_to_range(CHOKE_VALVES).value = pd.DataFrame(chokes)

    # Write out the pump data
    pumps = model.get_values(Pump=ALL, parameters=[
        Parameters.Pump.NAME, Parameters.Pump.PRESSUREDIFFERENTIAL,
        Parameters.Pump.POWER, Parameters.Pump.EFFICIENCY
        ])
    get_refers_to_range(PUMPS).value = pd.DataFrame(pumps)

    # Write out the compressor data
    compressors = model.get_values(Compressor=ALL, parameters=[
        Parameters.Compressor.NAME, Parameters.Compressor.PRESSUREDIFFERENTIAL,
        Parameters.Compressor.POWER, Parameters.Compressor.EFFICIENCY
        ])
    get_refers_to_range(COMPRESSORS).value = pd.DataFrame(compressors)


def update_equipment_data():
    model = connect_model()
    ''' Update the model with the data on to the equipment data sheet '''
    
    xw.sheets(EQUIPMENT_WORKSHEET).activate()

    # Update the chokes
    chokes = get_refers_to_range(CHOKE_VALVES).expand().value
    model.set_values(range_to_dictionary(chokes))

    # Update the pumps
    pumps = get_refers_to_range(PUMPS).expand().value
    model.set_values(range_to_dictionary(pumps))

    # Update the compressors
    compressors = get_refers_to_range(COMPRESSORS).expand().value
    model.set_values(range_to_dictionary(compressors))



# -----------------------------------------------------------------------------
# Network simulation
# -----------------------------------------------------------------------------
def run_network_simulation():
    model = connect_model()
    ''' Run a network simulation '''

    # Ensure that the results sheet is activated
    xw.sheets(RESULTS_WORKSHEET).activate()

    # Decide what variables that we want to include
    system_variables = [
        SystemVariables.PRESSURE,
        SystemVariables.TEMPERATURE,
        SystemVariables.VOLUME_FLOWRATE_LIQUID_STOCKTANK,
        SystemVariables.VOLUME_FLOWRATE_OIL_STOCKTANK,
        SystemVariables.VOLUME_FLOWRATE_WATER_STOCKTANK,
        SystemVariables.VOLUME_FLOWRATE_GAS_STOCKTANK,
        SystemVariables.GOR_STOCKTANK,
        SystemVariables.WATER_CUT_STOCKTANK,
        SystemVariables.WATER_CUT_INSITU,
        SystemVariables.WELLHEAD_VOLUME_FLOWRATE_FLUID_INSITU,
        SystemVariables.OUTLET_VOLUME_FLOWRATE_GAS_STOCKTANK,
        SystemVariables.OUTLET_VOLUME_FLOWRATE_OIL_STOCKTANK,
        SystemVariables.OUTLET_VOLUME_FLOWRATE_WATER_STOCKTANK,
        SystemVariables.SYSTEM_OUTLET_TEMPERATURE,
        SystemVariables.BOTTOM_HOLE_PRESSURE,
        SystemVariables.OUTLET_GLR_STOCKTANK,
        SystemVariables.OUTLET_WATER_CUT_STOCKTANK
    ]

    profile_variables = [
        ProfileVariables.TEMPERATURE,
        ProfileVariables.PRESSURE,
        ProfileVariables.ELEVATION,
        ProfileVariables.TOTAL_DISTANCE
    ]
    # Run the network simulation
    # Use the "run_simulation" to wait for the simulation to finish before continuing
    results = model.tasks.networksimulation.run(
                                profile_variables=profile_variables,
                                system_variables=system_variables)
    global RESULTS
    RESULTS = results    


# -----------------------------------------------------------------------------
# Get results back to Excel
# -----------------------------------------------------------------------------
def get_simulation_results():
    model = connect_model()
    ''' Get the simulation results once the simulation has finished '''

    xw.sheets(RESULTS_WORKSHEET).activate()

    #Clear contents of the worksheet
    xw.sheets(RESULTS_WORKSHEET).clear_contents()
    get_refers_to_range("Status").value = "Status:"
    get_refers_to_range("Title").value = "Simulation Results"

    results = RESULTS
    # Write the equipment names

    # System variable results
    system_df = pd.DataFrame.from_dict(results.system, orient="index")
    system_df.index.name = "Variable"
    get_refers_to_range(RESULTS_SYSTEM).value = system_df

    # Node results
    node_df = pd.DataFrame.from_dict(results.node, orient="index")
    node_df.index.name = "Variable"
    get_refers_to_range(RESULTS_NODE).value = node_df

    # Profile results
    col = get_refers_to_range(RESULTS_PROFILE).column
    row = get_refers_to_range(RESULTS_PROFILE).row

    units = pd.DataFrame(results.profile_units, index=["Units"])
    for branch in sorted(results.profile.keys()):
        profile = results.profile[branch]
        profile_df = pd.DataFrame.from_dict(profile)
        xw.Range((row, col)).value = pd.concat([units, profile_df])
        xw.Range((row,col)).expand('right').api.Font.Bold = True
        xw.Range((row,col)).expand('right').color = (200,200,200)
        xw.Range((row,col)).expand('down').api.Font.Bold = True
        xw.Range((row,col)).expand('down').color = (200,200,200)
        xw.Range((row, col-1)).value = branch
        xw.Range((row, col-1)).api.Font.Bold = True
        row += len(profile_df.index) + 3

# -----------------------------------------------------------------------------
#  Save the model
# -----------------------------------------------------------------------------


def save_model():
    model = connect_model()
    ''' Save the model '''
    # Save all model changes to current file
    model.save()

def handlePort(port):
    get_refers_to_range("PortNumber").value = port

def handleMessage(message):
    my_globals = globals()
    if message in my_globals:
        print("---------------------------------------")
        print("calling {} ...".format(message))
        my_globals[message]()
        print("Finished {}".format(message))
        return True
    
    print("Function {} is not defined".format(message))
    return False

if __name__ == '__main__':
    start_server(handlePort, handleMessage)    