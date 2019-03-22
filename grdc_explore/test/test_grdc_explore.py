# coding: utf-8
import os
import pytest

import numpy as np
import pandas as pd
from pandas.io.parsers import EmptyDataError

from grdc_explore import dataframe_from_stationId, valid_series, fill_with_empty_rows, replace_nans

grdc_data = os.path.join(os.path.dirname(__file__), "grdc_data")

def test_dataframe_from_stationId():
    df = dataframe_from_stationId(grdc_data, '146')
    assert len(df) == 30

def test_dataframe_file_too_short():
    with pytest.raises(EmptyDataError):
        df = dataframe_from_stationId(grdc_data, 'too_short')

def test_dataframe_wrong_column_name():
    with pytest.raises(KeyError):
        df = dataframe_from_stationId(grdc_data, 'wrong_column')

def test_dataframe_missing_file():
    with pytest.raises(Exception):
        df = dataframe_from_stationId(grdc_data, 'missing_file')

# read in 2 grdc datafiles and combine the data for hte following tests
df_1 = dataframe_from_stationId(grdc_data, 'series_1')
df_2 = dataframe_from_stationId(grdc_data, 'series_2')
combined = df_1.drop(columns=['date']).\
        rename(columns={'discharge': 'discharge_1'})
combined = pd.merge(combined, df_2.drop(columns=['date']),
        how='outer', on='date', sort=True)
combined = combined.rename(columns={'discharge': 'discharge_2'})
combined = combined.replace(-999., np.nan)

cleaned = combined.dropna(axis=0, how='any')
    
def test_valid_series():
    num_invalid_days = 0
    series = valid_series(cleaned, num_invalid_days)
    results = [10, 2, 3, 6]
    assert all([a == b for a, b in zip(results,
        series['Number of days in series'].values)])
