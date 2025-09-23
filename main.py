import json
import pandas as pd
from IPython.display import display


def parse_csv(file_name):
    df_raw = pd.read_csv(f"{file_name}.csv", delimiter=";")
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

    # Sort by change percentage descending
    df_companies = df_companies.sort_values(by="change_percentage", ascending=False)

    display(df_companies)

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
    print("--------------------------------")
    file_name = "data2"
    # read csv file with semicolon as delimiter
    df_raw = parse_csv(file_name)
    display(df_raw.head(10))

    # get list of unique companies
    # companies = df_raw["Kod"].unique()
    # print(f"Companies: {companies}")

    # Get latest data for each company
    df_companies = get_companies_summary(df_raw)

    # get winners
    output_dict = get_winners(df_companies)
    print(f"Winners: {output_dict}")

    # save to json
    with open(f"winners_{file_name}.json", "w") as f:
        json.dump(output_dict, f, indent=4)


if __name__ == "__main__":
    main()
