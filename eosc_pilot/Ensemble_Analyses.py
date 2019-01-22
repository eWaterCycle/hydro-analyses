# coding: utf-8

import os
import xarray as xr
import pandas as pd
import warnings
from dateutil.relativedelta import relativedelta

# todo select single or ensemble model run
# todo overwrite if observation data is not available



class EnsembleAnalyses(object):

    def __init__(self, forecast_dir, grdc_dir):
        self.initialized = False
        # Initalize ensemble_analyses class
        # Open specified forecast directory based
        self.forecast_dir = forecast_dir
        # If not specified open the last created folder in subdirectory
        if forecast_dir == "":
            all_subdirs = [d for d in os.listdir('.') if os.path.isdir(d)]
            try:
                latest_subdir = max(all_subdirs, key=os.path.getmtime)
            except:
                # no subdirectories to take the latest of
                latest_subdir = os.path.abspath('.')
            self.forecast_dir = latest_subdir

        # Open specified GRDC station directory
        self.grdc_dir = grdc_dir


    def forecast_read(self):
        # Create empty dataset and list
        forecast_ds = xr.Dataset()
        forecast_ds_stats = xr.Dataset()

        # Append all ensemble member in directory to xarray dataset
        for file in os.listdir(self.forecast_dir):
            # break up name and extension
            fName, fExt = os.path.splitext(file)

            # only use netcdf, ignore 'dischargeEns.nc file
            if fExt == '.nc' and fName != 'dischargeEns':
                fpath = os.path.join(self.forecast_dir, file)
                var_name = fName[:8]
                forecast_ds[var_name] = xr.open_dataarray(fpath)

            # Append forecast ensemble statistics to xarray dataset
            if fName == 'dischargeEns':
                fpath = os.path.join(self.forecast_dir, file)
                forecast_ds_stats = xr.open_dataset(fpath)

        self.forecast_ds = forecast_ds
        self.forecast_ds_stats = forecast_ds_stats

        self.initialized = True
        return self.forecast_ds, self.forecast_ds_stats


    def grdc_read(self, grdc_station_id, lat=None, lon=None):
        if not self.initialized:
            raise NotImplementedError('Run def forecast_read before def grdc_read')

        # Set grdc_station filename based on grdc_station_ID
        grdc_station_filename = str(grdc_station_id) + '.day'
        self.grdc_station_path = os.path.join(self.grdc_dir, grdc_station_filename)
        self.grdc_station_id = grdc_station_id


        # Read all GRDC station metadata with grdc_metadata_reader function
        if not os.path.isfile(self.grdc_station_path):
            raise NotImplementedError('Could not find file', self.grdc_station_path)
        self.metadata = grdc_metadata_reader(self.grdc_station_path)

        # Overwrite GRDC metadata lat/lon with specified lat/lon when present
        self.grdc_lat = lat
        self.grdc_lon = lon

        # Import GRDC data into dataframe and modify dataframe format
        grdc_station_df = pd.read_table(self.grdc_station_path, skiprows= 40, delimiter=';')
        grdc_station_df = grdc_station_df.rename(columns={'YYYY-MM-DD':'date', ' Original':'discharge'})
        grdc_station_df = grdc_station_df.reset_index().set_index(pd.DatetimeIndex(grdc_station_df['date']))
        grdc_station_df = grdc_station_df.drop(columns=['hh:mm', ' Calculated', ' Flag', 'index', 'date'])

        # Select GRDC station data that matches the forecast results Date
        grdc_station_select = grdc_station_df.loc[pd.to_datetime(str(self.forecast_ds.time.min().values)).strftime("%Y-%m-%d"):pd.to_datetime(str(self.forecast_ds.time.max().values)).strftime("%Y-%m-%d")]

        # Raise warning and use 10 year old data when data mismatch between forecast results and GRDC station observation occurs
        if grdc_station_select.empty:
            warnings.warn('GRDC station does not contain observations for forecast date. From the forecast date 10 years are subtracted in order to find observation data')
            # todo Change hardcoded - 10 years Remove or give alternative year statement
            tstart = pd.to_datetime(self.forecast_ds.time.min().values) - relativedelta(years=10)
            tstart = tstart.strftime("%Y-%m-%d")
            tend = pd.to_datetime(self.forecast_ds.time.max().values) - relativedelta(years=10)
            tend = tend.strftime("%Y-%m-%d")

            grdc_station_select = grdc_station_df.loc[str(tstart):str(tend)]

        self.grdc_station_select = grdc_station_select


        return self.metadata, self.grdc_station_select


def grdc_metadata_reader(grdc_station_path):
    """
    # Initiating a dictionary that will contain all GRDC attributes.
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
    f = open(grdc_station_path);
    allLines = f.read();
    f.close()

    # split the content of the file into several lines
    allLines = allLines.replace("\r", "")
    allLines = allLines.split("\n")

    # get grdc ids (from files) and check their consistency with their
    # file names
    id_from_file_name = int(os.path.basename(grdc_station_path).split(".")[0])
    id_from_grdc = None
    if id_from_file_name == int(allLines[8].split(":")[1].strip()):
        id_from_grdc = int(allLines[8].split(":")[1].strip())
    else:
        print("GRDC station " + str(id_from_file_name) + " (" + str(grdc_station_path) + \
              ") is NOT used.")

    if id_from_grdc != None:

        attributeGRDC["grdc_file_name"] = grdc_station_path
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
