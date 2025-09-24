from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import json
import io
from typing import Dict, Any, List
import os

# Import your existing functions
from main import get_companies_summary, get_winners, read_csv_safely
from validation import WinnersResponse, validate_csv_structure

app = FastAPI(
    title="Stock Market Daily Winners API",
    description="""
    API to analyze stock market data and find daily winners
    
    ### Features:
    - Process local CSV file of stock prices
    - Upload CSV files for analysis
    - Get top 3 daily winners with percentage changes
    
    """,
    version="1.0.0",
)


def process_dataframe(df_raw: pd.DataFrame) -> WinnersResponse:
    """
    Core processing function that takes a DataFrame and returns winners.
    This function is used by both endpoints to go from csv input to a winners list in JSON format.
    """
    try:
        # Convert Date to datetime and sort
        df_raw["Date"] = pd.to_datetime(df_raw["Date"])
        df_raw = df_raw.sort_values(by="Date", ascending=True)

        # Process the data using existing functions
        df_companies = get_companies_summary(df_raw)
        result = get_winners(df_companies)

        return WinnersResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")


@app.get("/")
async def root():
    return {"message": "Stock Market Daily Winners API"}


@app.get(
    "/health",
    tags=["Health"],
    summary="Basic Health Check",
    description="Returns basic API health status",
)
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Stock Market Daily Winners API",
        "version": "1.0.0",
    }


@app.post(
    "/get_daily_winners_from_file",
    tags=["Upload"],
    summary="Upload a CSV file and get the top 3 daily winners based on price change percentage.",
)
async def get_daily_winners_from_file(file: UploadFile = File(...)) -> WinnersResponse:
    """
    Upload a CSV file and get the top 3 daily winners based on price change percentage.

    Expected CSV format:
    - Columns:
       - Date (datetime. )
       - Kod (string. Company code)
       - Kurs (int. Price of the stock)
    - Delimiter: semicolon (;)
    - Date format: YYYY-MM-DD HH:MM:SS

    CSV format is validated before analysis.
    """

    # Validate file type
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV")

    try:
        # Read uploaded file content
        content = await file.read()

        # Convert bytes to string and then to pandas DataFrame
        csv_string = content.decode("utf-8")

        # Read CSV with all columns as strings initially for validation
        df_raw = pd.read_csv(io.StringIO(csv_string), delimiter=";", dtype=str)

        # Validate CSV structure and content
        validate_csv_structure(df_raw)

        # Now read again with proper dtypes for processing
        df_raw = pd.read_csv(io.StringIO(csv_string), delimiter=";")

        # Use the core processing function
        return process_dataframe(df_raw)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing uploaded file: {str(e)}"
        )


@app.get(
    "/get_daily_winners",
    tags=["Local"],
    summary="Process a CSV file from the local folder and get the top 3 daily winners.",
)
async def get_daily_winners() -> WinnersResponse:
    """
    Process a CSV file from the local folder and get the top 3 daily winners.
    The file 'data1.csv' is used and reloaded on every call to stay up to date.

    """

    try:
        filename = "data1.csv"
        file_path = f"data/{filename}"
        # Add .csv extension if not present
        if not file_path.endswith(".csv"):
            file_path = f"{file_path}.csv"

        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")

        # Read the local CSV file safely
        df_raw = read_csv_safely(file_path)

        # Use the core processing function
        return process_dataframe(df_raw)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"File '{file_path}' not found")
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing local file: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
