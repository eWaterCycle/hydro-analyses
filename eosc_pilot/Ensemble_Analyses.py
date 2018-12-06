# coding: utf-8

import os
from dateutil.relativedelta import relativedelta
import numpy as np
import xarray as xr
import pandas as pd


# todo check if newest folder selection works for forecast
# todo select single or ensemble model run
# todo overwrite lat lon coordinates when needed
# todo Conditional: first use forecast_read -> Done
# todo overwrite if observation data is not available



class EnsembleAnalyses(object):

    def __init__(self, forecast_dir, grdc_dir):
        self.initialized = False
        # Initalize ensemble_analyses class

        # Open specified folder based on forecast_date
        self.forecast_dir = forecast_dir
        # If not specified open the newest folder in subdirectory
        if forecast_dir == "":
            all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
            latest_subdir = max(all_subdirs, key=os.path.getmtime)
            self.forecast_dir = latest_subdir

        # Open specified GRDC folder
        self.grdc_dir = grdc_dir


    def forecast_read(self):
        # Create empty dataset and list
        ds = xr.Dataset()
        data_var = []

        # loop through files and append all ensemble members to one dataset
        for f in os.listdir(self.forecast_dir):
            # break up name and extension
            fName, fExt = os.path.splitext(f)
            # only use netcdf, ignore 'dischargeEns.nc file
            if fExt == '.nc' and fName != 'dischargeEns':
                fpath = os.path.join(self.forecast_dir, f)
                var_name = fName[:8]
                data_var.append(var_name)
                ds[var_name] = xr.open_dataarray(fpath)
            if fName == 'dischargeEns':
                fpath = os.path.join(self.forecast_dir, f)
                ds_stats = xr.open_dataset(fpath)

        self.ds = ds
        self.ds_stats = ds_stats

        self.initialized = True
        return self.ds, self.ds_stats


    def grdc_read(self, station_id, lat=None, lon=None):
        if not self.initialized:
            self.forecast_read()

        grdc_fname = str(station_id) + '.day'
        self.grdc_fpath = os.path.join(self.grdc_dir, grdc_fname)
        self.station_id = station_id

        # initiating a dictionary that will contain all GRDC attributes:

        self.metadata = grdc_metadata_reader(self.grdc_fpath, self.station_id)
        self.name = self.metadata['station_name']
        self.grdc_lat = self.metadata['grdc_latitude_in_arc_degree']
        self.grdc_lon = self.metadata['grdc_longitude_in_arc_degree']
        description = self.metadata['station_name'] + " - " + \
                      self.metadata['river_name'] + " - " + \
                      self.metadata['country_code']
        


        # Import GRDC data into dataframe
        grdc = pd.read_table(self.grdc_fpath, skiprows= 40, delimiter=';')
        grdc = grdc.rename(columns={'YYYY-MM-DD':'date', ' Original':'discharge'})
        grdc = grdc.reset_index().set_index(pd.DatetimeIndex(grdc['date']))
        grdc = grdc.drop(columns=['hh:mm', ' Calculated', ' Flag', 'index', 'date'])

        grdc_select = grdc.loc[pd.to_datetime(str(self.ds.time.min().values)).strftime("%Y-%m-%d"):pd.to_datetime(str(self.ds.time.max().values)).strftime("%Y-%m-%d")]

        if grdc_select.empty:
            # todo Change hardcoded - 10 years Remove or give alternative year statement
            tstart = pd.to_datetime(self.ds.time.min().values) - relativedelta(years=10)
            tstart = tstart.strftime("%Y-%m-%d")
            tend = pd.to_datetime(self.ds.time.max().values) - relativedelta(years=10)
            tend = tend.strftime("%Y-%m-%d")

            grdc_select = grdc.loc[str(tstart):str(tend)]
            print("10 years are substracted from observation date")

        self.grdc_select = grdc_select


        return self.metadata, self.grdc_select


def grdc_metadata_reader(grdc_fpath, station_id):
    """
    This function is based on earlier work by Rolf Hut.   https://github.com/RolfHut/GRDC2NetCDF/blob/master/GRDC2NetCDF.py
    # DOI: 10.5281/zenodo.19695
    # that function was based on earlier work by Edwin Sutanudjaja
    # from Utrecht University.
    # https://github.com/edwinkost/discharge_analysis_IWMI
    # initiating a dictionary that will contain all GRDC attributes:
    # This function is based on earlier work by Rolf Hut.
    # https://github.com/RolfHut/GRDC2NetCDF/blob/master/GRDC2NetCDF.py
    # DOI: 10.5281/zenodo.19695
    # that function was based on earlier work by Edwin Sutanudjaja
    # from Utrecht University.
    # https://github.com/edwinkost/discharge_analysis_IWMI
    # Modified by Susan Branchett
    """

    # initiating a dictionary that will contain all GRDC attributes:
    attributeGRDC = {}

    # read the file
    f = open(grdc_fpath);
    allLines = f.read();
    f.close()

    # split the content of the file into several lines
    allLines = allLines.replace("\r", "")
    allLines = allLines.split("\n")

    # get grdc ids (from files) and check their consistency with their
    # file names
    id_from_file_name = int(os.path.basename(grdc_fpath).split(".")[0])
    id_from_grdc = None
    if id_from_file_name == int(allLines[8].split(":")[1].strip()):
        id_from_grdc = int(allLines[8].split(":")[1].strip())
    else:
        print("GRDC station " + str(id_from_file_name) + " (" + str(grdc_fpath) + \
              ") is NOT used.")

    if id_from_grdc != None:

        attributeGRDC["grdc_file_name"] = grdc_fpath
        attributeGRDC["id_from_grdc"] = id_from_grdc

        try:
            attributeGRDC["file_generation_date"] = \
                str(allLines[6].split(":")[1].strip())
        except:
            attributeGRDC["file_generation_date"] = "NA"

        try:
            attributeGRDC["river_name"] = \
                str(allLines[9].split(":")[1].strip())
        except:
            attributeGRDC["river_name"] = "NA"

        try:
            attributeGRDC["station_name"] = \
                str(allLines[10].split(":")[1].strip())
        except:
            attributeGRDC["station_name"] = "NA"

        try:
            attributeGRDC["country_code"] = \
                str(allLines[11].split(":")[1].strip())
        except:
            attributeGRDC["country_code"] = "NA"

        try:
            attributeGRDC["grdc_latitude_in_arc_degree"] = \
                float(allLines[12].split(":")[1].strip())
        except:
            attributeGRDC["grdc_latitude_in_arc_degree"] = "NA"

        try:
            attributeGRDC["grdc_longitude_in_arc_degree"] = \
                float(allLines[13].split(":")[1].strip())
        except:
            attributeGRDC["grdc_longitude_in_arc_degree"] = "NA"

        try:
            attributeGRDC["grdc_catchment_area_in_km2"] = \
                float(allLines[14].split(":")[1].strip())
            if attributeGRDC["grdc_catchment_area_in_km2"] <= 0.0:
                attributeGRDC["grdc_catchment_area_in_km2"] = "NA"
        except:
            attributeGRDC["grdc_catchment_area_in_km2"] = "NA"

        try:
            attributeGRDC["altitude_masl"] = \
                float(allLines[15].split(":")[1].strip())
        except:
            attributeGRDC["altitude_masl"] = "NA"

        try:
            attributeGRDC["dataSetContent"] = \
                str(allLines[20].split(":")[1].strip())
        except:
            attributeGRDC["dataSetContent"] = "NA"

        try:
            attributeGRDC["units"] = str(allLines[22].split(":")[1].strip())
        except:
            attributeGRDC["units"] = "NA"

        try:
            attributeGRDC["time_series"] = \
                str(allLines[23].split(":")[1].strip())
        except:
            attributeGRDC["time_series"] = "NA"

        try:
            attributeGRDC["no_of_years"] = \
                int(allLines[24].split(":")[1].strip())
        except:
            attributeGRDC["no_of_years"] = "NA"

        try:
            attributeGRDC["last_update"] = \
                str(allLines[25].split(":")[1].strip())
        except:
            attributeGRDC["last_update"] = "NA"

        try:
            attributeGRDC["nrMeasurements"] = \
                int(str(allLines[38].split(":")[1].strip()))
        except:
            attributeGRDC["nrMeasurements"] = "NA"

        return attributeGRDC