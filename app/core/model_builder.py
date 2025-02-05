"""This module creates the components for the Pipsim model from an Excel file."""

import logging
from typing import List, Literal, NamedTuple, Optional

import pandas as pd
from sixgill.definitions import Parameters, Units
from sixgill.pipesim import Model, ModelComponents

from app.core import ExcelInputError

logger = logging.getLogger(__name__)


class PipsimComponents(NamedTuple):
    """
    A named tuple representing components in the PIPSIM model.

    Attributes:
        name (str): The name of the component.
        type (str): The type of the component.
    """

    name: str
    type: str


def create_component_name_df(excel_file_path: str, sheet_name: str) -> pd.DataFrame:
    """
    Create a DataFrame from the component names in the Excel file.

    Args:
        excel_file_path (str): The path to the Excel file.
        sheet_name (str): The name of the sheet containing the component names.

    Returns:
        pd.DataFrame: A DataFrame containing the component names.
    """
    component_name = pd.read_excel(excel_file_path, sheet_name=sheet_name)

    if len(component_name.columns) % 2 != 0:
        logger.warning(
            f"Odd number of columns in sheet '{sheet_name}' - dropping last column"
        )
        component_name = component_name.drop(component_name.columns[-1], axis=1)
    return component_name


class ModelBuilder:
    """
    Class for creating the components for the Pipsim model from an Excel file.
    Methods:
    create_model: Create the Pipsim model from the input data.
    """

    section_list: List[List[PipsimComponents]] = []

    def __init__(
        self,
        pipsim_file_path: str,
        component_name: pd.DataFrame,
        units: str = Units.METRIC,
    ) -> None:
        self.model = Model.open(pipsim_file_path, units=units)
        self.component_name = component_name

    def main(self) -> None:
        """Main method to create the Pipsim model from the input data."""
        self.create_model()
        self.model.save()
        self.model.close()
        logger.info("Pipsim model created")

    def create_model(self) -> None:
        """Main method to create the Pipsim model from the input data."""
        self.create_section_components()
        for idx, section in enumerate(self.section_list):
            self.build_section(section, x=4000, y=idx * 100)
        logger.info("Pipsim model created")

    def create_section_components(self) -> None:
        """
        Generates a List[List[PipsimComponents]]
        - where each inner list contains adjacent components in the data
        """
        self.section_list = []
        if self.component_name is None:
            logger.error("component_name is None. Cannot create section components.")
            return

        columns = self.component_name.columns
        for i in range(0, len(columns), 2):
            adjacent_columns = columns[i : i + 2]
            df_pair = self.component_name[adjacent_columns].dropna(axis=0, how="all")
            df_pair = self.insert_junctions(
                df_pair, i // 2, adjacent_columns[0], adjacent_columns[1]
            )
            component_list = [
                PipsimComponents(*row)
                for row in df_pair.itertuples(index=False, name=None)
            ]
            if component_list:
                self.section_list.append(component_list)

        logger.info(f"Section list created with {len(self.section_list)} sections")

    def insert_junctions(
        self, df: pd.DataFrame, section_number: int, loop_column: str, type_column: str
    ) -> pd.DataFrame:
        """
        Insert junctions between flowlines for a specific section.

        Args:
            df (pd.DataFrame): Input data for the section.
            section_number (int): Section identifier.
            loop_column (str): Column for loop names.
            type_column (str): Column for component types.

        Returns:
            pd.DataFrame: Updated DataFrame with junctions added.
        """
        if df.empty:
            logger.warning("Input DataFrame is empty; no junctions added.")
            return df

        new_rows = []
        j_counter = 1
        previous_row = None

        for index, row in df.iterrows():
            if index == 0 and row[type_column] == "Flowline":
                # Check and add a junction at the beginning if the first row is a Flowline
                new_rows.append(
                    {
                        loop_column: f"LJ({section_number}_{j_counter})",
                        type_column: "Junction",
                    }
                )
                j_counter += 1

            if (
                previous_row is not None
                and previous_row[type_column] == "Flowline"  # pylint: disable=E1136
                and row[type_column] == "Flowline"
            ):
                # Insert Junction immediately after the first Flowline row
                new_rows.append(
                    {
                        loop_column: f"LJ({section_number}_{j_counter})",
                        type_column: "Junction",
                    }
                )
                j_counter += 1

            new_rows.append(row.to_dict())
            previous_row = row.to_dict()  # Update the previous row

        if df.iloc[-1][type_column] == "Flowline":
            # Check and add a junction at the end if the last row is a Flowline
            new_rows.append(
                {
                    loop_column: f"LJ({section_number}_{j_counter})",
                    type_column: "Junction",
                }
            )

        return pd.DataFrame(new_rows)

    def connect_nodes(self, node1: PipsimComponents, node2: PipsimComponents) -> None:
        if node1 and node2:
            cond1 = self.model.find(component=node1.type, Name=node1.name)
            cond2 = self.model.find(component=node2.type, Name=node2.name)
            if not cond1 or not cond2:
                raise ValueError("Node not found")

        try:
            self.model.connect(node1.name, node2.name)
        except ValueError:
            logger.warning(
                f"Connection between {node1.name} and {node2.name} already exists"
            )

    def add_components(self, component, name, x=None, y=None) -> None:
        try:
            if (
                x is not None
                and y is not None
                and component != ModelComponents.FLOWLINE
            ):
                self.model.add(component, name, parameters={"X": x, "Y": y})
            else:
                self.model.add(component, name)
        except ValueError:
            logger.warning(f"Component {name} already exists in the model")

    def build_section(
        self,
        components: List[PipsimComponents],
        x=None,
        y=None,
        orientation="Horizontal",
    ) -> None:
        interval = 100
        for i, component in enumerate(components):
            try:
                if x is None or y is None:
                    self.add_components(component.type, component.name)
                else:
                    if orientation == "Horizontal":
                        component_x = x + i * interval
                        component_y = y
                    else:
                        component_x = x
                        component_y = y + i * interval

                    self.add_components(
                        component.type, component.name, component_x, component_y
                    )
                if i > 0:
                    self.connect_nodes(components[i - 1], component)
            except Exception as e:
                logger.error(
                    f"Error building section {i} in component {component.name} : {e}"
                )
