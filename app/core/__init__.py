# init.py
""" init file for the core package. """


class ExcelInputError(Exception):
    def __init__(self, message, excel_path, sheet_name=None):
        super().__init__(message)
        self.excel_path = excel_path
        self.sheet_name = sheet_name

    def __str__(self):
        return (
            f"{self.args[0]} (Excel file: {self.excel_path}, "
            f"Sheet: {self.sheet_name})"
        )


class PipsimModellingError(Exception):
    """Raised when an error occurs in the modelling process."""

    def __init__(self, message, pipsim_path):
        super().__init__(message)
        self.pipsim_path = pipsim_path

    def __str__(self):
        return f"Modeling Error: {self.args[0]} (Model: {self.pipsim_path})"


class NetworkSimulationError(Exception):
    """Custom exception for network simulation errors."""

    def __init__(self, message, model_path):
        super().__init__(message)
        self.model_path = model_path

    def __str__(self):
        return f"Simulation Error: {self.args[0]} (Model: {self.model_path})"


from .excel_handling import ExcelHandler
from .input_validation import PipSimInput
from .inputdata import InputData
from .multi_case_modeller import MultiCaseModeller
from .network_simulation import NetworkSimulator
from .network_simulation_summary import NetworkSimulationSummary, SummaryError
from .unit_conversion import UnitConversion
