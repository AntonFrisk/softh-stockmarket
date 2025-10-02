from pydantic import BaseModel, ValidationError, ConfigDict
from typing import Dict, Any, List
import pandas as pd
from fastapi import HTTPException


# Pydantic models for type-safe responses
class Winner(BaseModel):
    rank: int
    name: str
    percent: float
    latest: int


class WinnersResponse(BaseModel):
    winners: List[Winner]


# Pydantic model for CSV row validation
class StockDataRow(BaseModel):
    model_config = ConfigDict(extra="allow")

    Date: str  # Will be converted to datetime later
    Kod: str  # Company code
    Kurs: float  # Stock price


def validate_csv_structure(df: pd.DataFrame, rows_to_check: int = None) -> None:
    """
    Validate CSV structure using Pydantic models.
    Raises HTTPException if validation fails.
    """
    required_columns = {"Date", "Kod", "Kurs"}

    # Check if required columns exist
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise HTTPException(
            status_code=400,
            detail=f"Missing required columns: {', '.join(missing_columns)}. Expected: Date, Kod, Kurs",
        )

    # Validate a sample of rows (a subset of the data, or all if not specified)
    if rows_to_check is None:
        sample_size = len(df)  # check all rows
    else:
        sample_size = rows_to_check  # check first n rows

    try:
        for i in range(sample_size):
            row_data = df.iloc[i][["Date", "Kod", "Kurs"]].to_dict()

            # Convert pandas NaN to None for validation
            for key, value in row_data.items():
                if pd.isna(value):
                    row_data[key] = None

            # Try to validate the row
            StockDataRow(**row_data)

            # Additional check for numeric Kurs column
            try:
                float(row_data["Kurs"])  # attempt to convert the price to a float
            except (ValueError, TypeError):
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid price value in row {i+1}: '{row_data['Kurs']}' is not a valid number",
                )

    except ValidationError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid data format in CSV. Row {i+1}: {str(e)}"
        )
