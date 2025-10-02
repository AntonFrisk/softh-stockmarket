import json
import pandas as pd
from IPython.display import display
import shutil
import tempfile
import os


def read_csv_safely(file_path):
    """
    Safely read CSV by creating a temporary copy first.
    Prevents conflicts with concurrent writes.
    """
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".csv", delete=False
    ) as temp_file:
        temp_path = temp_file.name

    try:
        # Copy original file to temp location
        shutil.copy2(file_path, temp_path)
        # Read from the copy
        df = pd.read_csv(temp_path, delimiter=";")
        return df
    finally:
        # Always clean up temp file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def parse_csv(file_path):
    df_raw = read_csv_safely(file_path)
    df_raw["Date"] = pd.to_datetime(df_raw["Date"])
    df_raw = df_raw.sort_values(by="Date", ascending=True)
    return df_raw


def get_companies_summary(df_raw):

    latest_data = df_raw.groupby("Kod").last().reset_index()

    # Calculate previous day timestamp vectorized
    latest_data["previous_day_end"] = (
        pd.to_datetime(latest_data["Date"]) - pd.Timedelta(days=1)
    ).dt.floor("D") + pd.Timedelta(hours=23, minutes=59)

    # More robust approach: for each company, find previous price
    def get_previous_price(company_code, prev_timestamp):
        company_data = df_raw[df_raw["Kod"] == company_code]
        before_timestamp = company_data[company_data["Date"] < prev_timestamp]
        if not before_timestamp.empty:
            return before_timestamp.iloc[-1]["Kurs"], before_timestamp.iloc[-1]["Date"]
        else:
            return None, None

    # Apply the function to get previous prices
    previous_results = latest_data.apply(
        lambda row: get_previous_price(row["Kod"], row["previous_day_end"]),
        axis=1,
        result_type="expand",
    )
    previous_results.columns = ["previous_price", "previous_timestamp"]

    # Combine latest and previous data
    df_companies = pd.concat(
        [latest_data[["Kod", "Kurs", "Date"]], previous_results], axis=1
    )

    # Rename columns to match original format
    df_companies = df_companies.rename(
        columns={"Kod": "kod", "Kurs": "latest_price", "Date": "latest_timestamp"}
    )

    # Calculate change percentage
    df_companies["change_percentage"] = (
        (df_companies["latest_price"] - df_companies["previous_price"])
        / df_companies["previous_price"]
        * 100
    )
    df_companies["change_percentage"] = df_companies["change_percentage"].round(2)

    # filter on latest_timestamp to only include rows where latest_timestamp is within the same day as the most recent row
    most_recent_date = df_companies["latest_timestamp"].max()
    most_recent_day = most_recent_date.date()
    start = pd.Timestamp(most_recent_day)  # e.g., 2025-10-02 00:00:00
    end = start + pd.Timedelta(days=1)  # 2025-10-03 00:00:00
    df_companies = df_companies[
        (df_companies["latest_timestamp"] >= start)
        & (df_companies["latest_timestamp"] < end)
    ]

    # Sort by change percentage descending
    df_companies = df_companies.sort_values(by="change_percentage", ascending=False)

    # display(df_companies)  # Commented out for API compatibility

    # change percentage to float and latest price to int
    df_companies["change_percentage"] = df_companies["change_percentage"].astype(float)
    df_companies["latest_price"] = df_companies["latest_price"].astype(int)

    return df_companies


def get_winners(df_companies):
    winners = []
    number_of_winners = 3
    for i in range(number_of_winners):
        dict_winner = {
            "rank": i + 1,
            "name": str(df_companies.iloc[i]["kod"]),
            "percent": float(
                df_companies.iloc[i]["change_percentage"]
            ),  # Now Python float
            "latest": int(df_companies.iloc[i]["latest_price"]),  # Now Python int
        }
        winners.append(dict_winner)

    output_dict = {
        "winners": winners,
    }

    return output_dict


def main():
    """
    Demo the data pipeline for stock market daily ranking.
    """
    print("--------------------------------")
    # Resolve absolute path to the project root and data directory
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    file_name = "data4"
    file_path = f"{DATA_DIR}/{file_name}.csv"
    # read csv file with semicolon as delimiter
    df_raw = parse_csv(file_path)
    display(df_raw.head(10))

    # get list of unique companies
    # companies = df_raw["Kod"].unique()
    # print(f"Companies: {companies}")

    # Get latest data for each company
    df_companies = get_companies_summary(df_raw)

    # get winners
    output_dict = get_winners(df_companies)
    output_json = json.dumps(output_dict, indent=2)
    print("\nResponse:\n", output_json)

    # save to json to data folder (uncomment this to save json file)
    # with open(f"{DATA_DIR}/winners_{file_name}.json", "w") as f:
    #     json.dump(output_dict, f, indent=4)
    #     print(f"📂 Saved 'winners_{file_name}.json' to {DATA_DIR}")


if __name__ == "__main__":
    main()
