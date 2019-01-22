# coding: utf-8
import pytest

from Ensemble_Analyses import EnsembleAnalyses
from Ensemble_Analyses import grdc_metadata_reader

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

#def test_read_forecast():
#todo

def test_no_forecast(tmp_path):
    analysis = EnsembleAnalyses(tmp_path, '')
    data, stats = analysis.forecast_read()
    assert len(data) == 0
    assert len(stats) == 0

#def test_read_grdc():
#todo

def test_grdc_before_forecast(tmp_path):
    analysis = EnsembleAnalyses('', tmp_path)
    with pytest.raises(Exception):
        analysis.grdc_read(2)

def test_no_grdc(tmp_path):
    analysis = EnsembleAnalyses('', tmp_path)
    analysis.initialized = True #fakes running forecast_read
    with pytest.raises(Exception):
        analysis.grdc_read(2)

def test_grdc_metadata():
    attributes = grdc_metadata_reader("146.day")
    assert attributes["grdc_file_name"] == "146.day"
    assert attributes["id_from_grdc"] == 146
    assert attributes["file_generation_date"] == "2019-01-22"
    assert attributes["river_name"] == "THAMES"
    assert attributes["station_name"] == "TOWER_BRIDGE"
    assert attributes["country_code"] == "UK"
    assert attributes["grdc_latitude_in_arc_degree"] == 51.5055
    assert attributes["grdc_longitude_in_arc_degree"] == 0.0754
    assert attributes["grdc_catchment_area_in_km2"] == 1.11
    assert attributes["altitude_masl"] == 2.2
    assert attributes["dataSetContent"] == "MADE UP TEST DATA"
    assert attributes["units"] == "pounds per square inch"
    assert attributes["time_series"] == "1967 until yesterday"
    assert attributes["no_of_years"] == 52
    assert attributes["last_update"] == "2019-01-22"
    assert attributes["nrMeasurements"] == 30

def test_no_metadata():
    with pytest.raises(Exception):
       attributes = grdc_metadata_reader("666.day")

def test_inconsistent_metadata():
    attributes = grdc_metadata_reader("10.day")
    assert len(attributes) == 0

def test_missing_metadata():
    attributes = grdc_metadata_reader("30.day")
    assert attributes["file_generation_date"] == "NA"
    assert attributes["river_name"] == "NA"
    assert attributes["station_name"] == "NA"
    assert attributes["country_code"] == "NA"
    assert attributes["grdc_latitude_in_arc_degree"] == "NA"
    assert attributes["grdc_longitude_in_arc_degree"] == "NA"
    assert attributes["grdc_catchment_area_in_km2"] == "NA"
    assert attributes["altitude_masl"] == "NA"
    assert attributes["dataSetContent"] == "NA"
    assert attributes["units"] == "NA"
    assert attributes["time_series"] == "NA"
    assert attributes["no_of_years"] == "NA"
    assert attributes["last_update"] == "NA"
    assert attributes["nrMeasurements"] == "NA"

def test_negative_catchment():
    attributes = grdc_metadata_reader("40.day")
    assert attributes["grdc_catchment_area_in_km2"] == "NA"
