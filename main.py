import pandas as pd
from IPython.display import display



def main():
    print("--------------------------------")
    # read csv file with semicolon as delimiter
    df = pd.read_csv("data1.csv", delimiter=";")
    display(df.head())

    # get list of unique companies
    companies = df["Kod"].unique()
    print(companies)

    # for each company, get the last price and the date and save to a new df
    last_prices = []
    last_dates = []
    for company in companies:
        last_price = df[df["Kod"] == company]["Kurs"].iloc[-1]
        last_date = df[df["Kod"] == company]["Date"].iloc[-1]
        print(f"{company}: {last_price} on {last_date}")
        last_prices.append(last_price)
        last_dates.append(last_date)
    df_last_prices = pd.DataFrame({"kod": companies, "last_price": last_prices, "date": last_dates})
    display(df_last_prices.head())

if __name__ == "__main__":
    main()
