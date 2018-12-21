# coding: utf-8
import pytest

from Ensemble_Analyses import EnsembleAnalyses

def test_set_directories():
    data = EnsembleAnalyses('C:\testdir\forecast_dir', 'D:/testdir/grdc_dir')
    assert data.forecast_dir == 'C:\testdir\forecast_dir'
    assert data.grdc_dir == 'D:/testdir/grdc_dir'

def test_set_empty_directories():
    data = EnsembleAnalyses("", "")
    assert data.forecast_dir != ''
    assert data.grdc_dir == ''

def test_set_2many_directories():
    with pytest.raises(Exception):
        data = EnsembleAnalyses('C:\forecast_dir', 'D:/grdc_dir', "E:/one2many")
