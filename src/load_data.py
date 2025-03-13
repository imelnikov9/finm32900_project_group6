import wrds
import pandas as pd
import os
from settings import config
from pathlib import Path


DATA_DIR = config("DATA_DIR")
START_DATE = config("START_DATE")
END_DATE = config("END_DATE")

def load_crsp_index():
    """
    Load the CRSP value-weighted index data from the CSV file saved by pull_CRSP_index.py.
    Adjusts the dates from the last business day of the month to the first day of the following month.
    
    Returns:
        df (DataFrame): Contains the adjusted 'date' and 'value_weighted_return'.
    """
    csv_path = DATA_DIR / "crsp_value_weighted_index.csv"
    df = pd.read_csv(csv_path, parse_dates=["date"])
    
    # Adjust dates: convert each date to the first day of the following month.
    # For example, if date is 4/29/1930, it will become 5/1/1930.
    df['date'] = df['date'].apply(lambda d: (d.replace(day=1) + pd.DateOffset(months=1)))
    
    return df

def load_fred_data():
    """
    Load the FRED data saved as a Parquet or CSV file.
    Returns the TB3MS series as a pandas Series with dates as index.
    """
    parquet_path = DATA_DIR / "fred.parquet"
    csv_path = DATA_DIR / "fred.csv"

    if parquet_path.exists():
        df = pd.read_parquet(parquet_path)
    else:
        df = pd.read_csv(csv_path, parse_dates=["DATE"]).set_index("DATE")

    df = df['TB3MS'] / 1200
    df = df[(df.index >= START_DATE) & (df.index <= END_DATE)]
    
    # Define your date range to fill 0's
    start_date = '1930-01-01'
    end_date = '1933-12-31'

    # Apply the replacement only for rows within the date range
    df.loc[(df.index >= start_date) & (df.index <= end_date)] = df.loc[(df.index >= start_date) & (df.index <= end_date)].fillna(0)
    
    df = df.dropna()

    return df

def load_and_compute_excess_returns():
    """
    Loads CRSP market returns and FRED risk-free rate (TB3MS), aligns them by date,
    and computes excess returns = market return minus TB3MS.
    
    Returns:
        excess_returns (Series): Excess returns with dates as index.
    """
    # Load CRSP data and set date as index
    crsp_df = load_crsp_index()
    crsp_df = crsp_df.set_index("date")
    # Ensure the market return is numeric
    market_return = pd.to_numeric(crsp_df["value_weighted_return"], errors='coerce')
    
    # Load the risk-free rate (TB3MS) from FRED
    tb3ms = load_fred_data()
    
    # Align the two series on common dates
    common_dates = market_return.index.intersection(tb3ms.index)
    market_return = market_return.loc[common_dates]
    tb3ms = tb3ms.loc[common_dates]
    
    # Optionally, if TB3MS is in percent (e.g. 3.5 for 3.5%), convert to decimal:
    # tb3ms = tb3ms / 100.0
    
    # Compute excess returns
    excess_returns = market_return - tb3ms
    return excess_returns

def load_ken_french(dataset_name="6_Portfolios_2x3", weighting="value-weighted"):
    """
    Load Ken French portfolio data from the Excel file saved by pull_ken_french_data.py.
    If weighting is 'BE_FYt-1_to_ME_June_t', then shift the date index backward by 7 months 
    to align the valuation ratio with the time the information is available.
    """
    excel_name = f"{dataset_name.replace('/', '_')}.xlsx"
    excel_path = DATA_DIR / excel_name
    
    if weighting == "value-weighted":
        sheet_name = "0"
    elif weighting == "equal-weighted":
        sheet_name = "1"    
    elif weighting == "BE_FYt-1_to_ME_June_t":
        sheet_name = "7"
    else:
        raise ValueError("Invalid weighting: must be 'value-weighted', 'equal-weighted', or 'BE_FYt-1_to_ME_June_t'.")

    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    
    # If using the BE_FYt-1_to_ME_June_t measure, shift the dates backward by 7 months 
    # so that the valuation ratio is aligned with the time it would be available for forecasting.
    if weighting == "BE_FYt-1_to_ME_June_t":
        # First, ensure that the date column is datetime and set as the index if it exists.
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"])
            df = df.set_index("Date")
        # Shift the index by subtracting 7 months
        df.index = df.index - pd.DateOffset(months=7)
    
    return df


#df_6 = load_ken_french("6_Portfolios_2x3", weighting="value-weighted")
#df_25 = load_ken_french("25_Portfolios_5x5", weighting="value-weighted")
#df_100 = load_ken_french("100_Portfolios_10x10", weighting="value-weighted")

