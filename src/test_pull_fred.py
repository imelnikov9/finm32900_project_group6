import pandas as pd
import pytest
from settings import config
import pull_fred
DATA_DIR = config("DATA_DIR")

# Test to confirm that the function returns a pandas DataFrame with the expected columns
def test_pull_fred_functionality():
    df = pull_fred.pull_fred()
    # Test if the function returns a pandas DataFrame
    assert isinstance(df, pd.DataFrame)

    # Test if the DataFrame has the expected columns
    expected_columns = ['CPIAUCNS', 'GDP', 'GDPC1', 'TB3MS']
    assert all(col in df.columns for col in expected_columns)


# Test to confirm that the data has valid start and end dates
def test_pull_fred_data_validity():
    df = pull_fred.pull_fred()
    
    # Test if the default date range has the expected start date and end date
    assert df.index.min() == pd.Timestamp('1930-01-01')
    assert df.index.max() >= pd.Timestamp('2023-12-31')

    # Test if the average annualized growth rate is close to 3.08%
    ave_annualized_growth = 4 * 100 * df.loc['1913-01-01': '2023-09-01', 'GDPC1'].dropna().pct_change().mean()
    assert abs(ave_annualized_growth - 3.08) < 0.1
