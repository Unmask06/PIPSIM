# init.py
""" init file for the core package. """

class ExcelInputError(Exception):
    """Base class for exceptions in this module."""


class PipsimModellingError(Exception):
    """Raised when an error occurs in the modelling process."""


class NetworkSimulationError(Exception):
    """Custom exception for network simulation errors."""


from .excel_handling import ExcelHandler
from .input_validation import PipSimInput
from .inputdata import InputData
from .network_simulation import NetworkSimulator
from .network_simulation_summary import NetworkSimulationSummary, SummaryError
from .simulation_modeller import MultiCaseModeller
from .unit_conversion import UnitConversion
