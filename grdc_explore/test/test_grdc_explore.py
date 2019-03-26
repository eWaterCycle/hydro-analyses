# coding: utf-8
import os
import pytest

import numpy as np
import pandas as pd
from pandas.io.parsers import EmptyDataError

from grdc_explore import dataframe_from_stationId, valid_series, \
     fill_with_empty_rows, fill_nans, replace_nans

grdc_data = os.path.join(os.path.dirname(__file__), "grdc_data")


def test_dataframe_from_stationId():
    df = dataframe_from_stationId(grdc_data, '30_datalines')
    assert len(df) == 30


def test_dataframe_file_too_short():
    with pytest.raises(EmptyDataError):
        dataframe_from_stationId(grdc_data, 'too_short')


def test_dataframe_wrong_column_name():
    with pytest.raises(KeyError):
        dataframe_from_stationId(grdc_data, 'wrong_column')


def test_dataframe_missing_file():
    with pytest.raises(Exception):
        dataframe_from_stationId(grdc_data, 'missing_file')


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
    results = [10, 2, 3, 4]
    assert all([a == b for a, b in zip(results,
               series['Number of days in series'].values)])


def test_valid_1_invalid():
    num_invalid_days = 2
    series = valid_series(cleaned, num_invalid_days)
    results = [28]
    print(series['Number of days in series'].values)
    assert all([a == b for a, b in zip(results,
               series['Number of days in series'].values)])


def test_fill_with_empty_rows():
    input_df = df_1.drop(columns=['date'])
    input_df = input_df.replace(-999., np.nan)
    input_df = input_df.dropna(axis=0, how='any')
    output_df = fill_with_empty_rows(input_df, input_df.index[0],
                                     input_df.index[-1])
    assert len(input_df) == 24
    assert len(output_df) == 28


def test_fill_nans():
    before = 1.1
    after = 5.5
    posts = 3
    results = [2.2, 3.3, 4.4]
    filling = fill_nans(before, after, posts)
    assert all([a == pytest.approx(b) for a, b in zip(results, filling)])


def test_replace_nans():
    df = pd.DataFrame([[1.,      1.],
                       [np.nan,  2.],
                       [3.,      3.],
                       [4.,      np.nan],
                       [5.,      np.nan],
                       [6.,      np.nan],
                       [7.,      7.]],
                       columns=['miss one', 'miss three'])
    df['date'] = pd.date_range('2019-03-22', periods=7, freq='D')
    df = df.reset_index().set_index(pd.DatetimeIndex(df['date']))
    df = df.drop(columns=['date'])
    filled = replace_nans(df)
    results = [1., 2., 3., 4., 5., 6., 7.]
    assert all([a == b for a, b in zip(results,
               filled['miss one'].values)])
    assert all([a == b for a, b in zip(results,
               filled['miss three'].values)])
