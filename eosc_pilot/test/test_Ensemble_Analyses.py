# coding: utf-8
import os
import pytest

from Ensemble_Analyses import EnsembleAnalyses
from Ensemble_Analyses import grdc_metadata_reader

#forecast_data = os.path.join(os.path.dirname(__file__), "forecast_data")
grdc_data = os.path.join(os.path.dirname(__file__), "grdc_data")

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
##todo check if forecast files may be added to github
#    analysis = EnsembleAnalyses(forecast_data, "")
#    data, stats = analysis.forecast_read()
#    assert len(data) == 2 #corresponds to number of files
#    assert len(stats) == 3 #always 3?
#    assert analysis.initialized == True

def test_no_forecast(tmpdir):
    analysis = EnsembleAnalyses(tmpdir, '')
    data, stats = analysis.forecast_read()
    assert len(data) == 0
    assert len(stats) == 0
    assert analysis.initialized == True

def test_read_grdc_without_forecast():
    analysis = EnsembleAnalyses("", grdc_data)
    analysis.initialized = True #fakes running forecast_read
    with pytest.raises(Exception):
        analysis.grdc_read(146, lat=11.1111, lon=22.2222)
    assert analysis.grdc_station_path == os.path.join(grdc_data,"146.day")
    assert analysis.grdc_station_id == 146
    todo assert analysis.metadata["grdc_latitude_in_arc_degree"] == 11.1111
    todo assert analysis.metadata["grdc_longitude_in_arc_degree"] == 22.2222
    
#def test_read_grdc_with_forecast():
##todo check if forecast files may be added to github
#    analysis = EnsembleAnalyses(forecast_data, grdc_data)
#    data, stats = analysis.forecast_read()
#    assert len(data) == 2 #corresponds to number of files
#    analysis.grdc_read(146)
#    assert analysis.metadata["grdc_latitude_in_arc_degree"] == 51.5055
#    assert analysis.metadata["grdc_longitude_in_arc_degree"] == 00.0754
#    # assert analysis.grdc_station_select[discharge] == ??

def test_grdc_without_initialisation(tmpdir):
    analysis = EnsembleAnalyses('', tmpdir)
    with pytest.raises(Exception):
        analysis.grdc_read(2)

def test_no_grdc(tmpdir):
    analysis = EnsembleAnalyses('', tmpdir)
    analysis.initialized = True #fakes running forecast_read
    with pytest.raises(Exception):
        analysis.grdc_read(2)

def test_grdc_metadata():
    grdc_data_file = os.path.join(grdc_data, "146.day")
    attributes = grdc_metadata_reader(grdc_data_file)
    assert attributes["grdc_file_name"] == grdc_data_file
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
       attributes = grdc_metadata_reader(os.path.join(grdc_data, "666.day"))

def test_inconsistent_metadata():
    attributes = grdc_metadata_reader(os.path.join(grdc_data, "10.day"))
    assert len(attributes) == 0

def test_missing_metadata():
    attributes = grdc_metadata_reader(os.path.join(grdc_data, "30.day"))
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
    attributes = grdc_metadata_reader(os.path.join(grdc_data, "40.day"))
    assert attributes["grdc_catchment_area_in_km2"] == "NA"
