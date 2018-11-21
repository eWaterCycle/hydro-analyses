# coding: utf-8

import os
import numpy as np
import xarray as xr
import pandas as pd

data_var = []
data_stats = []

ds = xr.Dataset()
ds_stats = xr.Dataset()

class Station:

    #read metadata from grdc file and initialise the station
    def __init__(self, GRDC_dir, station_id, label):
        fileName = str(station_id) + '.day'
        filePath = os.path.join(GRDC_dir, fileName)
        self.station_id = station_id
        self.GRDCfilePath = filePath
        self.metadata = read_grdc(filePath)
        self.name = self.metadata['station_name']
        self.lat = self.metadata['grdc_latitude_in_arc_degree']
        self.lon = self.metadata['grdc_longitude_in_arc_degree']
        description = self.metadata['station_name']+" - "+self.metadata['river_name']+" - "+                      self.metadata['country_code']
        if label != "":
            print("Changing station label from '"+description+"' to '"+label+"'")
            description = label
        self.label = description

    def init_netcdf(netcdf_dir):
        # Initialize the netcdf data
        # Create empty lists and xarray dataset to be filled with netcdf

        # Loop files in working directory and create 1 xarray dataset
        # Each ensemble member is represented by one file with name
        # 'discharge*???.nc' where the 3 characters ??? identify the
        # ensemble member.
        # In addition the working directory contains files with ensemble
        # statistics with names 'discharge*Out.nc'
        for f in os.listdir(netcdf_dir):
            fName, fExt = os.path.splitext(f) # break up name and extension
            if fExt == '.nc': #only use netcdf file
                fpath = os.path.join(netcdf_dir, f)
                var_name = 'discharge' + fName[-3:]
            if var_name != 'dischargeOut':
                data_var.append(var_name)
                ds[var_name] = xr.open_dataarray(fpath)
            else:
                var_name = fName
                data_stats.append(var_name) # todo 20181121 not used
                ds_stats[var_name] = xr.open_dataarray(fpath)
        return data_var

    #Read netcdf simulation data
    def netcdf_data(self):
        #todo - make sure that station has already been initialised
        self.ds = ds.sel(lat=self.lat, lon=self.lon, method='nearest')
        self.ds_stats = ds_stats.sel(lat=self.lat, lon=self.lon, method='nearest')
        self.mean = self.ds_stats['dischargeEnsMeanOut']
        self.std = self.ds_stats['dischargeEnsStdOut']
        
        self.array = xr.Dataset.to_array(self.ds)
        
        self.min = self.array.min('variable')
        self.max = self.array.max('variable')
        self.std_low = self.std
        self.std_high = self.mean-self.std
        self.std_high = self.std_high + self.mean
        
    #Read grdc_data, drop columns and create 2 columns: date and discharge
    def grdc_data(self, first_date, last_date):
        #todo - make sure that station has already been initialised
        # format is 40 rows of comments and then title and data rows:
        # YYYY-MM-DD;hh:mm; Original; Calculated; Flag
        times = pd.date_range(first_date, last_date)
        # selects 9 days of discharge data
        times = pd.date_range('2017-11-22', periods=9) #todo this is a big hack!

        grdc = pd.read_table(self.GRDCfilePath, skiprows= 40, delimiter=';')
        grdc = grdc.rename(columns={'YYYY-MM-DD':'date', ' Original':'discharge'})
        grdc = grdc.reset_index().set_index(pd.DatetimeIndex(grdc['date']))
        grdc = grdc.drop(columns=['hh:mm', ' Calculated', ' Flag', 'index', 'date'])
        grdc_other = np.array([])
        grdc_other = np.append(grdc_other,grdc[first_date:last_date])

        return xr.DataArray(grdc_other, coords=[times], dims=['time'])

#read station metadata from the first 40 lines of a GRDC file
def read_grdc(filePath):
    # This function is based on earlier work by Rolf Hut.
    # https://github.com/RolfHut/GRDC2NetCDF/blob/master/GRDC2NetCDF.py
    # DOI: 10.5281/zenodo.19695
    # that function was based on earlier work by Edwin Sutanudjaja
    # from Utrecht University.
    # https://github.com/edwinkost/discharge_analysis_IWMI

    # initiating a dictionary that will contain all GRDC attributes:
    attributeGRDC = {}
    
    # read the file
    f = open(filePath) ; allLines = f.read() ; f.close()

    # split the content of the file into several lines
    allLines = allLines.replace("\r","") 
    allLines = allLines.split("\n")

    # get grdc ids (from files) and check their consistency with their file names  
    id_from_file_name =  int(os.path.basename(filePath).split(".")[0])
    id_from_grdc = None
    if id_from_file_name == int(allLines[ 8].split(":")[1].strip()):
        id_from_grdc = int(allLines[ 8].split(":")[1].strip())
    else:
        print("GRDC station "+str(id_from_file_name)+" ("+str(filePath)+\
              ") is NOT used.")

    if id_from_grdc != None:

        attributeGRDC["grdc_file_name"] = filePath
        attributeGRDC["id_from_grdc"] = id_from_grdc
        
        try: attributeGRDC["file_generation_date"] = \
                str(allLines[ 6].split(":")[1].strip())
        except: attributeGRDC["file_generation_date"] = "NA"

        try: attributeGRDC["river_name"] = \
                str(allLines[ 9].split(":")[1].strip())
        except: attributeGRDC["river_name"] = "NA"

        try: attributeGRDC["station_name"] = \
                str(allLines[10].split(":")[1].strip())
        except: attributeGRDC["station_name"] = "NA"

        try: attributeGRDC["country_code"] = \
                str(allLines[11].split(":")[1].strip())
        except: attributeGRDC["country_code"] = "NA"

        try: attributeGRDC["grdc_latitude_in_arc_degree"]  = \
                float(allLines[12].split(":")[1].strip())
        except: attributeGRDC["grdc_latitude_in_arc_degree"] = "NA"
            
        try: attributeGRDC["grdc_longitude_in_arc_degree"] = \
                float(allLines[13].split(":")[1].strip())
        except: attributeGRDC["grdc_longitude_in_arc_degree"] = "NA"

        try:
            attributeGRDC["grdc_catchment_area_in_km2"] = \
                float(allLines[14].split(":")[1].strip())
            if attributeGRDC["grdc_catchment_area_in_km2"] <= 0.0:
                attributeGRDC["grdc_catchment_area_in_km2"]  = "NA" 
        except:
            attributeGRDC["grdc_catchment_area_in_km2"] = "NA"

        try: attributeGRDC["altitude_masl"] = \
                float(allLines[15].split(":")[1].strip())
        except: attributeGRDC["altitude_masl"] = "NA"

        try: attributeGRDC["dataSetContent"] = \
                str(allLines[20].split(":")[1].strip())
        except: attributeGRDC["dataSetContent"] = "NA"

        try: attributeGRDC["units"] = str(allLines[22].split(":")[1].strip())
        except: attributeGRDC["units"] = "NA"

        try: attributeGRDC["time_series"] = \
                str(allLines[23].split(":")[1].strip())
        except: attributeGRDC["time_series"] = "NA"

        try: attributeGRDC["no_of_years"] = \
                int(allLines[24].split(":")[1].strip())
        except: attributeGRDC["no_of_years"] = "NA"

        try: attributeGRDC["last_update"] = \
                str(allLines[25].split(":")[1].strip())
        except: attributeGRDC["last_update"] = "NA"

            
        try: attributeGRDC["nrMeasurements"] = \
                int(str(allLines[38].split(":")[1].strip()))
        except: attributeGRDC["nrMeasurements"] = "NA"

    return attributeGRDC
