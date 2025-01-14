# model_input.py
"""
This module contains the dataclasses for model configuration and model inputs.

DataClasses:
- PipsimModel: Dataclass for model configuration.
- ModelInput: Dataclass for model inputs.

Raises:
- PipsimModellingError: Raised when an error occurs in the modelling process.

"""

import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import pandas as pd
from sixgill.pipesim import Model, Units

from project import TextHandler

logger = logging.getLogger(__name__)
logger.addHandler(TextHandler())

class PipsimModellingError(Exception):
    """Raised when an error occurs in the modelling process."""


@dataclass
class PipsimModel:
    """Dataclass for Pipsim Model configuration."""

    model_filename: str
    quick_try: bool = False
    case: Optional[str] = None
    condition: Optional[str] = None
    folder_path: Optional[str] = None
    model_path: str = field(init=False)
    model: Model = field(init=False)

    FILENAME_PATTERN = r"([^_]+)_([^_]+)_([^.]+)(.[a-z]*)"

    def __post_init__(self):
        if self.folder_path is None:
            self.folder_path = os.getcwd()

        self.model_path = str(Path(self.folder_path) / Path(self.model_filename))

        self.model = Model.open(filename=str(self.model_path), units=Units.FIELD)

        if self.model.tasks is not None:
            self.networksimulation = self.model.tasks.networksimulation

        self._get_case_condition()

        logger.info(
            f"Model {self.model_filename} loaded successfully.\n"
            f"case: {self.case}\n condition: {self.condition}\n"
            f"base model: {self.base_model_filename}"
        )

    def _get_case_condition(self):
        """
        Get the case and condition from the model filename.
        """
        if self.quick_try:
            self.case = "quick_try"
            self.condition = "quick_try"
            self.base_model_filename = self.model_filename
            return

        if self.case is None or self.condition is None:
            filename = str(Path(self.model_filename).stem + Path(self.model_filename).suffix)
            match = re.match(self.FILENAME_PATTERN, filename)
            if match:
                self.case = match.group(1)
                self.condition = match.group(2)
                self.base_model_filename = match.group(3) + match.group(4)
            else:
                raise PipsimModellingError(
                    "Model filename must follow the pattern: 'case_condition_basefilename'"
                )
        elif self.case is not None and self.condition is not None:
            self.base_model_filename = self.model_filename


@dataclass
class ModelInput:
    """Dataclass for Pipsim model inputs."""

    source_name: str = ""
    pump_name: list = field(default_factory=list)
    well_profile: pd.DataFrame = field(default_factory=pd.DataFrame)
    ambient_temperature: Optional[float] = None
    source_pressure: Optional[float] = None
    source_temperature: Optional[float] = None
    differential_pressure: Optional[float] = None

    def none_check(self):
        if (
            self.ambient_temperature is None
            or self.source_pressure is None
            or self.source_temperature is None
            or self.differential_pressure is None
        ):
            raise PipsimModellingError(
                """
                Ambient temperature, source pressure, and
                source temperature are required for the model
                """
            )
