# simulation_modeller.py
"""
This module contains the class for building the model for network simulation using Pipesim model.
  
    Classes:
    - PipsimModeller: Builds the model for network simulation using the Pipesim model.

    Methods:
    - copy_flowline_data: Copy flowline data from the source model to the target model.
    
    Raises:
    - PipsimModellingError: Raised when an error occurs in the modelling process.
"""
import logging
from pathlib import Path

import pandas as pd
from sixgill.definitions import ModelComponents, Parameters
from sixgill.pipesim import Model, Units

from app.core import ExcelInputError, PipsimModellingError
from app.core.helper import generate_dict_from_class

logger = logging.getLogger(__name__)


class MultiCaseModeller:
    """
    Builds the model for network simulation using the Pipesim model for multiple cases.

    Attributes:
        model (Model): The Pipesim model object.
        excel_path (str): The path to the excel file.
        sink_profile (pd.DataFrame): The sink profile data.
        conditions (pd.DataFrame): The conditions data.

    Main Methods:
        - build_model: Builds the model for network simulation using the Pipesim model.

    Properties:
        cases (list): Generates all possible cases from the sink profile and conditions.
    """

    model: Model
    boundary_conditions: pd.DataFrame
    values: pd.DataFrame
    category: pd.DataFrame
    well_values: pd.DataFrame
    well_lists: list

    MINIMUM_FLOWRATE = 0.001  # Minimum flowrate for a well to be active (STBD)

    class RequiredColumns:
        """
        Class containing the required columns for the sink profile DataFrame.
        """

        COMPONENT_NAME = "Component Name"
        COMPONENT_TYPE = "Component Type"
        PARAMETER = "Parameter"
        UNIT = "Unit"

    def __init__(
        self,
        base_model_path: str,
        excel_path: str,
        multi_case_sheet: str,
        units: str = Units.METRIC,
    ) -> None:
        logger.info("🚀 Initializing Multi-Case Modeller !!")
        self.base_model_path = base_model_path
        self.excel_path = excel_path
        self.multi_case_sheet = multi_case_sheet
        self.multi_case_data = self._validate_n_load_data()
        self.units = units

    def _validate_n_load_data(self) -> pd.DataFrame:
        """
        Validates and loads the data from the excel file.

        """

        try:
            data = pd.read_excel(self.excel_path, sheet_name=self.multi_case_sheet)

            # Check for mandatory columns
            self.required_columns = [
                self.RequiredColumns.COMPONENT_NAME,
                self.RequiredColumns.COMPONENT_TYPE,
                self.RequiredColumns.PARAMETER,
                self.RequiredColumns.UNIT,
            ]
            if not all(col in data.columns for col in self.required_columns):
                msg = f"Missing mandatory columns in sheet '{self.multi_case_sheet}': {self.required_columns}"
                raise ExcelInputError(msg, self.excel_path, self.multi_case_sheet)

            # Check for invalid component types and parameters
            component_type_params = generate_dict_from_class(Parameters)
            valid_component_types = set(component_type_params.keys())

            for idx, (component_type, parameter) in enumerate(
                zip(
                    data[self.RequiredColumns.COMPONENT_TYPE],
                    data[self.RequiredColumns.PARAMETER],
                )
            ):
                if component_type not in valid_component_types:
                    msg = f"Invalid component type '{component_type} used in row '{idx+2}'"
                    raise ExcelInputError(msg, self.excel_path, self.multi_case_sheet)
                if parameter not in component_type_params[component_type]:
                    msg = f"Invalid parameter '{parameter} used in row '{idx+2}'"
                    raise ExcelInputError(msg, self.excel_path, self.multi_case_sheet)

        except FileNotFoundError as e:
            raise ExcelInputError(
                "Excel file not found", excel_path=self.excel_path
            ) from e

        return data

    @property
    def cases(self) -> list:
        """Generates cases from multi-case data."""

        return list(set(self.multi_case_data.columns) - set(self.required_columns))

    def set_simulation_settings(self, case: str) -> None:
        df = self.multi_case_data.loc[
            self.multi_case_data[self.RequiredColumns.COMPONENT_TYPE]
            == Parameters.SimulationSetting.__name__,
            [self.RequiredColumns.PARAMETER, case],
        ]
        if df.empty:
            logger.warning(f"No Simulation settings found for condition: {case}")
            return

        for _, row in df.iterrows():
            try:
                attr = self.model.sim_settings.__dict__.get("_settings").get(  # type: ignore
                    row[self.RequiredColumns.PARAMETER]
                )
                setattr(self.model.sim_settings, attr, row[case])
            except AttributeError:
                logger.warning(
                    f"Invalid Simulation setting parameter: {row[self.RequiredColumns.PARAMETER]}"
                )
                continue

        reset = self.model.tasks.networksimulation.reset_conditions()  # type: ignore
        self.model.save()

        if reset:
            logger.info(f"Set simulation settings for condition: {case}")
        else:
            logger.warning(f"Failed to set simulation settings for condition: {case}")

    def set_parameters_dict(self, case: str) -> None:

        data = self.multi_case_data.dropna(
            subset=[self.RequiredColumns.COMPONENT_NAME, case]
        ).loc[
            :,
            [
                self.RequiredColumns.COMPONENT_NAME,
                self.RequiredColumns.PARAMETER,
                case,
            ],
        ]

        if data.empty:
            logger.warning(f"No parameters found for condition: {case}")
            return

        result = {}
        for component_name, parameter, value in zip(
            data[self.RequiredColumns.COMPONENT_NAME],
            data[self.RequiredColumns.PARAMETER],
            data[case],
        ):
            try:
                component_name = str(component_name).strip()
                if component_name not in result:
                    result[component_name] = {}
                result[component_name][parameter] = value
            except Exception as e:
                logger.error(
                    f"Error setting parameters: {e} for {component_name} with value {value}"
                )

        self.model.set_values(dict=result)
        reset = self.model.tasks.networksimulation.reset_conditions()  # type: ignore

        if reset:
            logger.info(f"Set parameters for condition: {case}")
        else:
            logger.warning(f"Failed to set parameters for condition: {case}")

    def save_as_new_model(self, case: str) -> None:
        folder_path = Path(self.excel_path).parent.absolute() / "Models"
        folder_path.mkdir(exist_ok=True)

        if self.model.filename is None:
            raise PipsimModellingError("Model filename is None", self.model.filename)
        new_file = folder_path / f"{case}_{Path(self.model.filename).name}"
        self.model.save(str(new_file))
        logger.info(f"Model saved as {new_file}")

    def build_model(self, case: str) -> None:
        """
        Builds a simulation model for a given case and condition.

        Args:
            case: Sink profile case abbreviation.
        """
        logger.info(f"⏳ Building model for case: {case}")
        self.model = Model.open(self.base_model_path, units=self.units)
        self.set_simulation_settings(case)
        self.set_parameters_dict(case)
        self.save_as_new_model(case)
        self.model.close()
        logger.info(f"✅ Completed building model for case: {case} \n")

    def build_all_models(self) -> Path:
        """
        Builds simulation models for all possible cases and conditions.

        Returns:
            Path: The path to the folder containing the models.
        """
        logger.info(f"🔃 Building models for {len(self.cases)} cases")

        for case in self.cases:
            self.build_model(case)

        model_path = Path(self.excel_path).parent.absolute() / "Models"

        logger.info(
            f"✌ All models built successfully. \n 📂 Models saved in {model_path}"
        )
        return model_path


# Other methods in the module------------------------------------------------------------
def _collect_flowline_geometry(df: pd.DataFrame, source_model: Model) -> list:
    """
    Helper function to collect flowline geometry from the source model
    used in the copy_flowline_data function
    """
    flowline_geometry = []
    detailed_flowlines = df.loc[
        :,
        df.loc[Parameters.Flowline.DETAILEDMODEL]
        == True,  # pylint: disable=singleton-comparison
    ].columns.to_list()
    for flowline in detailed_flowlines:
        try:
            flowline_geometry.append(
                {flowline: source_model.get_geometry(context=flowline)}
            )
        except Exception as e:
            logger.error(f"Error getting geometry for {flowline}: {e}")
    return flowline_geometry


def copy_flowline_data(source_model_path: str, destination_folder_path: str):
    """
    Copy flowline data from the source model to all target models in the destination folder.

    Args:
        source_model_path (str): The path to the source model file.
        destination_folder_path (str): The path to the destination folder containing target model files.
    """

    if not Path(source_model_path).exists():
        raise PipsimModellingError("Source model file not found", source_model_path)
    if not Path(destination_folder_path).exists():
        raise PipsimModellingError(
            "Destination folder not found", destination_folder_path
        )

    logger.info(
        f"Copying flowline data from {Path(source_model_path).name} "
        f"to all models in {destination_folder_path}....."
    )
    logger.info(
        "Total number of flowlines in the destination folder: %d",
        len(list(Path(destination_folder_path).glob("*.pips"))),
    )

    source_model = Model.open(source_model_path)
    logger.info(f"Getting flowline data from {Path(source_model_path).name}.....")
    source_values = source_model.get_values(component=ModelComponents.FLOWLINE)
    df = pd.DataFrame(source_values)
    flowline_geometry = _collect_flowline_geometry(df, source_model)
    source_model.close()

    target_files = list(Path(destination_folder_path).glob("*.pips"))

    for idx, target_model_path in enumerate(target_files, start=1):
        logger.info(
            f"Copying basic flowline data from to {Path(target_model_path).name}....."
        )
        logger.warning(
            """This step may take a while depending on the number of flowlines in the model.
            Please wait for the process to complete."""
        )
        target_model = Model.open(str(target_model_path))
        target_model.set_values(source_values)
        target_model.save()

        logger.info(
            f"Copying detailed flowline data to {Path(target_model_path).name}....."
        )

        for flowline in flowline_geometry:
            for name, geometry in flowline.items():
                target_model.set_geometry(context=name, value=geometry)
        target_model.save()
        target_model.close()
        logger.info(
            "Flowline data copied successfully to %s (Completed %d of %d models)",
            Path(target_model_path).name,
            idx,
            len(target_files),
        )
