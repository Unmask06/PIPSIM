from pathlib import Path
import logging
from typing import List
import xlwings as xw

from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger("Input Validation")

class CustomException(Exception):
    pass


class PipSimInput(BaseModel):
    FOLDER_DIRECTORY: Path
    MODEL_FILENAME: str
    EXCEL_FILE: str
    PIPSIM_INPUT_SHEET: str
    CONDITIONS_SHEET:str
    SOURCE_NAME: str
    PUMP_NAME: List[str]

    @field_validator("FOLDER_DIRECTORY")
    def check_folder_directory(cls, v):
        if not Path(v).is_dir():
            raise ValueError("Folder directory does not exist")
        return v

    @field_validator("MODEL_FILENAME")
    def check_model_filename(cls, v, values):
        if not Path(values.data["FOLDER_DIRECTORY"] / v).is_file():
            raise ValueError("Model file does not exist")
        return v

    @field_validator("EXCEL_FILE")
    def check_excel_file(cls, v, values):
        if not Path(values.data["FOLDER_DIRECTORY"] / v).is_file():
            raise ValueError("Excel file does not exist")
        return v
    
    @field_validator("PIPSIM_INPUT_SHEET", "CONDITIONS_SHEET")
    def check_pipsim_input_sheet(cls, v, values):
        excel_file_path = values.data["FOLDER_DIRECTORY"] / values.data["EXCEL_FILE"]
        with xw.App(visible=False) as app:
            wb = xw.Book(excel_file_path)
            sheet_names = [sheet.name for sheet in wb.sheets]
            if not v in sheet_names:
                raise ValueError(f"Sheet '{v}' does not exist in {values.data['EXCEL_FILE']}")
        logger.info("PIPSIM Input Validation Successful")
        return v