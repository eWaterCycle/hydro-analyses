from stations import Station

def test_create_file(tmp_path):
    p = tmp_path / "6435060.day"
    p.write_text(CONTENT)
    assert p.read_text() == CONTENT
    assert len(list(tmp_path.iterdir())) == 1

    station_id = 6435060
    label = 'Lobith (Rhine, Europe)'
    station = Station(tmp_path, station_id, label)

    assert station.station_id == station_id
    assert station.GRDCfilePath == str(tmp_path / "6435060.day")
    assert station.name == 'LOBITH'
    assert station.lat == 51.840003
    assert station.lon == 6.110003
    assert station.label == label
    assert station.metadata["id_from_grdc"] == station_id
    assert station.metadata["file_generation_date"] == '2014-04-23'
    assert station.metadata["river_name"] == 'RHINE RIVER'
    assert station.metadata["country_code"] == 'NL'
    assert station.metadata["grdc_catchment_area_in_km2"] == 160800.003
    assert station.metadata["altitude_masl"] == 8.53
    assert station.metadata["dataSetContent"] == 'MEAN DAILY DISCHARGE'
    assert station.metadata["units"] == 'm³/s'
    assert station.metadata["time_series"] == '1901-01 - 2012-12'
    assert station.metadata["no_of_years"] == 112
    assert station.metadata["last_update"] == '2013-08-26'
    assert station.metadata["nrMeasurements"] == 40908

CONTENT = '''# Title:                 GRDC STATION DATA FILE
#                        --------------
# Format:                DOS-ASCII
# Date format:           YYYY-MM-DD; YYYY-MM; YYYY; MM
# Field delimiter:       ;
#
# file generation data:  2014-04-23
#
# GRDC-No.:              6435060
# River:                 RHINE RIVER
# Station:               LOBITH
# Country:               NL
# Latitude (dec. °):       51.840003
# Longitude (de. °):        6.110003
# Catchment area (km²):   160800.003
# Altitude (m.a.s.l):           8.53
# Next d/s station:      -
# Remarks:               
#************************************************************
#
# Data Set Content:      MEAN DAILY DISCHARGE
#                        --------------------
# Unit:                  m³/s
# Time series:           1901-01 - 2012-12
# No. of years:          112
# Last update:           2013-08-26
#
# Table Header:
#     YYYY-MM-DD - Date
#     hh:mm      - Time
#     Original   - original (provided) data
#     Calculated - GRDC modified data
#     Flag       - modification flag
#        -999 - missing data, no correction
#           1 - corrected data, no method specified
#          99 - usage not recommended by the provider
#         900 - calculated from daily water level
#
# Data lines: 40908
# DATA
YYYY-MM-DD;hh:mm; Original; Calculated; Flag
1901-01-01;--:--;   2035.000;   2035.000; -999
1901-01-02;--:--;   2270.000;   2270.000; -999
1901-01-03;--:--;   2445.000;   2445.000; -999
1901-01-04;--:--;   2325.000;   2325.000; -999
1901-01-05;--:--;   2175.000;   2175.000; -999'''


