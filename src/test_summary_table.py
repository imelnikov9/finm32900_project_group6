import pytest
import pandas as pd
import numpy as np
from noteb.ipynb import summary_df

def test_summary_table_exists():
    """Test that the summary DataFrame is loaded and not empty."""
    assert isinstance(summary_df, pd.DataFrame), "summary_df is not a DataFrame"
    assert not summary_df.empty, "summary_df is empty"

def test_summary_table_structure():
    """Test that summary_df contains expected columns."""
    expected_columns = ["In-Sample R²", "Out-of-Sample R²"]
    assert all(col in summary_df.columns for col in expected_columns), f"Missing expected columns: {expected_columns}"


def test_summary_table_expected_rows():
    """Check that portfolio categories exist in the index."""
    expected_indices = ["6 Portfolios In Sample", "25 Portfolios In Sample", "100 Portfolios In Sample"]
    missing = [idx for idx in expected_indices if idx not in summary_df.index]
    assert not missing, f"Missing expected rows: {missing}"

if __name__ == "__main__":
    pytest.main()
