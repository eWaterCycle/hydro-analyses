# -*- coding: utf-8 -*-
"""
Created on Mon Mar 18 14:13:59 2019

@author: j.p.m.aerts@tudelft.nl
"""

import os
import urllib.request as urllib2
import pandas as pd

def download_usgs_data(excel_usgs_id, output_format, startDT, endDT, parameterCd):
    # More information: https://waterservices.usgs.gov/rest/IV-Test-Tool.html
    # output_format e.g. ('json', 'rdb')
    # startDT e.g. ('1980-01-01')
    # endDT e.g.('2018-12-31')
    # parameterCd e.g. ('00060') discharge, cubic feet per second
    
    streamgauges = pd.read_excel(excel_usgs_id, dtype=str)
    streamgauges_id = streamgauges['USGS_ID']
    
    for id in streamgauges_id:
            url = "https://waterservices.usgs.gov/nwis/iv/?format="+output_format+",1.0&sites="+id+"&startDT="+startDT+"&endDT="+endDT+"&parameterCd="+parameterCd+"&siteStatus=all"
            out = id + "."+ output_format
            urllib2.urlretrieve(url,out)
            
            log = print(id+' Downloaded')
    return log



def convert_unit_timestep(workingfolder):
    # Converts cubic feet to cubic meters per second
    # Changes format of table to [datetime, discharge]
    for file in os.listdir(workingfolder):   # loop through for each file in the folder
        fName, fExt = os.path.splitext(file) # break up file name and extension
        if fExt.lower() == '.rdb': #only use rdb files
            df = pd.read_table(file, skiprows=37, usecols=[2,4], header=None, names =['datetime', 'discharge']) #Read rdb table and set column headers
            
            df['discharge'] = df['discharge'].replace('Ice',0) # Remove strings from series
            df['discharge'] = df['discharge'].apply(lambda x: float(x)) # Convert series to float
            df['discharge'] = df['discharge'].apply(lambda x: x/35.315) # Convert to cubic meters per second
            df['datetime'] = pd.to_datetime(df['datetime'], infer_datetime_format=True) # Convert to datetime
            df.index = pd.to_datetime(df['datetime'], infer_datetime_format=True) # Convert to datetime and set index
            df = df.drop(columns='datetime') # Drop obsolete column
            df = df.resample('H').sum() # Resample to hourly values
            
            df.to_excel(fName+"_hourly.xlsx")
            log = print(fName+"_hourly.xlsx"+" Converted")
    return log



workingfolder = os.chdir(r"C:\Users\LocalAdmin\Desktop\spatial_temporal_scaling_study\workingfolder") #Set workingfolder
download_usgs_data('streamgauges.xlsx','rdb','1980-01-01','2018-12-31','00060')
convert_unit_timestep(workingfolder)