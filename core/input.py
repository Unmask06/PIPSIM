from pathlib import Path
import logging

from pydantic import BaseModel, Field, ValidationError, field_validator

logger = logging.getLogger(__name__)


class PipSimInput(BaseModel):
    FOLDER_DIRECTORY: Path
    MODEL_FILENAME: str
    EXCEL_FILE: str
    SOURCE_NAME: str
    PUMP_NAME: list[str]


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
