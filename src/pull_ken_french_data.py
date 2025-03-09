import warnings
from pathlib import Path

import pandas as pd
import pandas_datareader.data as web

from settings import config

DATA_DIR = config("DATA_DIR")
START_DATE = config("START_DATE")
END_DATE = config("END_DATE")


def pull_ken_french_excel(
    dataset_name="Portfolios_Formed_on_INV",
    data_dir=DATA_DIR,
    log=True,
    start_date=START_DATE,
    end_date=END_DATE,
):
    """
    Pulls the Ken French portfolio data..
    
    Parameters:
    - dataset_name (str): Name of the dataset to pull.
    - data_dir (str): Directory to save the Excel file.
    - log (bool): Whether to log the path of the saved Excel file.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.
    
    Returns:
    - Excel File: Contains date, return, and other key fields.
    """

    data_dir = Path(data_dir)
    # Suppress the specific FutureWarning about date_parser
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="The argument 'date_parser' is deprecated",
        )
        data = web.DataReader(
            dataset_name,
            "famafrench",
            start=start_date,
            end=end_date,
        )
        excel_path = (
            data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
        )  # Ensure the name is file-path friendly

        with pd.ExcelWriter(excel_path, engine="xlsxwriter") as writer:
            # Write the description to the first sheet
            if "DESCR" in data:
                description_df = pd.DataFrame([data["DESCR"]], columns=["Description"])
                description_df.to_excel(writer, sheet_name="Description", index=False)

            # Write each table in the data to subsequent sheets
            for table_key, df in data.items():
                if table_key == "DESCR":
                    continue  # Skip the description since it's already handled
                sheet_name = str(table_key)  # Naming sheets by their table_key
                df.to_excel(
                    writer, sheet_name=sheet_name[:31]
                )  # Sheet name limited to 31 characters
    if log:
        print(f"Excel file saved to {excel_path}")
    return excel_path


def load_returns(dataset_name, weighting="value-weighted", data_dir=DATA_DIR):
    data_dir = Path(data_dir)
    excel_path = data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
    if weighting == "value-weighted":
        sheet_name = "0"
    elif weighting == "equal-weighted":
        sheet_name = "1"
    else:
        raise ValueError(f"Invalid weighting: {weighting}")
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    return df


def load_sheet(dataset_name, sheet_name: str = "0", data_dir=DATA_DIR):
    """For example, for dataset_name = 'Portfolios_Formed_on_INV', the full data
    is the description and the 7 tables of returns and properties.

    Portfolios Formed on INV
    ------------------------

    This file was created by CMPT_EP_CFP_OP_INV_NI_AC_RETS using the 202412 CRSP
    database. It contains value- and equal-weighted returns for portfolios
    formed on INV. The portfolios are constructed at the end of June. INV,
    investment, is the change in total assets from the fiscal year ending in
    year t-2 to the fiscal year ending in t-1, divided by t-2 total assets.
    Annual returns are from January to December. Missing data are indicated by
    -99.99 or -999. The break points include utilities and include financials.
    The portfolios include utilities and include financials. Copyright 2024
    Eugene F. Fama and Kenneth R. French

    0 : Value Weight Returns -- Monthly (696 rows x 18 cols)
    1 : Equal Weight Returns -- Monthly (696 rows x 18 cols)
    2 : Value Weight Returns -- Annual from January to December (58 rows x 18 cols)
    3 : Equal Weight Returns -- Annual from January to December (58 rows x 18 cols)
    4 : Number of Firms in Portfolios (696 rows x 18 cols)
    5 : Average Firm Size (696 rows x 18 cols)
    6 : Value Weight Average of Natural Log of INV (58 rows x 18 cols)
    """
    if isinstance(sheet_name, int):
        sheet_name = str(sheet_name)

    data_dir = Path(data_dir)
    excel_path = data_dir / f"{dataset_name.replace('/', '_')}.xlsx"
    df = pd.read_excel(excel_path, sheet_name=sheet_name)
    if sheet_name == "Description":
        return df.iloc[0, 0]
    return df


def _demo():
    df = load_sheet("Portfolios_Formed_on_INV", sheet_name="0")
    df
    df_desc = load_sheet("25_Portfolios_OP_INV_5x5", sheet_name="Description")
    print(df_desc)

    ff_factors = load_sheet("F-F_Research_Data_Factors", sheet_name="0")
    ff_factors
    ff_factors_desc = load_sheet("F-F_Research_Data_Factors", sheet_name="Description")
    print(ff_factors_desc)

    ff_portfolios = load_sheet("6_Portfolios_2x3", sheet_name="0")
    ff_portfolios
    ff_portfolios_desc = load_sheet("6_Portfolios_2x3", sheet_name="Description")
    print(ff_portfolios_desc)


if __name__ == "__main__":
    _ = pull_ken_french_excel(
        dataset_name="6_Portfolios_2x3",
    )  # Save 6_Portfolios_2x3.xlsx
    _ = pull_ken_french_excel(
        dataset_name="25_Portfolios_5x5",
    )  # Save 25_Portfolios_5x5.xlsx
    _ = pull_ken_french_excel(
        dataset_name="100_Portfolios_10x10",
    )  # Save 100_Portfolios_10x10.xlsx
