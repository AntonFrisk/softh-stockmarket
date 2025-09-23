import pandas as pd
from IPython.display import display


def main():
    print("--------------------------------")
    # read csv file with semicolon as delimiter
    df = pd.read_csv("data1.csv", delimiter=";")

    # convert Date to datetime
    df["Date"] = pd.to_datetime(df["Date"])
    # sort by date descending
    df = df.sort_values(by="Date", ascending=True)
    display(df.head(10))

    # get list of unique companies
    companies = df["Kod"].unique()
    print(companies)

    # for each company, get the last price and the date and save to a new df
    latest_prices = []
    latest_timestamps = []
    previous_prices = []
    previous_timestamps = []
    for company in companies:
        latest_price = df[df["Kod"] == company]["Kurs"].iloc[-1]
        latest_timestamp = df[df["Kod"] == company]["Date"].iloc[-1]
        # get the 23:59 time for the day before latest_date
        previous_day_timestamp = pd.to_datetime(latest_timestamp) - pd.Timedelta(days=1)
        previous_day_timestamp = previous_day_timestamp.replace(
            hour=23, minute=59, second=0, microsecond=0
        )
        # get previous day price by finding firs occurence of date before last_date
        previous_price = df[df["Kod"] == company][df["Date"] < previous_day_timestamp][
            "Kurs"
        ].iloc[-1]
        previous_timestamp = df[df["Kod"] == company][
            df["Date"] < previous_day_timestamp
        ]["Date"].iloc[-1]
        print(f"{company}: {latest_price} on {latest_timestamp}")
        latest_prices.append(latest_price)
        latest_timestamps.append(latest_timestamp)
        previous_prices.append(previous_price)
        previous_timestamps.append(previous_timestamp)
    df_last_prices = pd.DataFrame(
        {
            "kod": companies,
            "last_price": latest_prices,
            "date": latest_timestamps,
            "previous_price": previous_prices,
            "previous_date": previous_timestamps,
        }
    )
    display(df_last_prices.head())


if __name__ == "__main__":
    main()
