import os
import numpy as np
import pandas as pd
from datetime import datetime

def dataframe_from_stationId(grdc_folder, station_id):
    ''' Search the grdc_folder for a file with name <station_id>.day,
    skip the header rows and return the dates and discharges in a dataframe'''
                
    filename = str(station_id) + ".day"
    grdc_file = os.path.join(grdc_folder, filename)

    grdc_data = pd.read_csv(grdc_file, skiprows=40, delimiter=';')
    grdc_data = grdc_data.rename(columns={'YYYY-MM-DD': 'date',
                                 ' Original': 'discharge'})
    grdc_data = grdc_data.reset_index().set_index(pd.DatetimeIndex(grdc_data['date']))
    grdc_data = grdc_data[['date', 'discharge']]
 
    return grdc_data

def valid_series(cleaned, num_invalid_days=0):
    ''' Search through a cleaned and sorted dataframe and return a dataframe with start
    end dates of series with (nearly) consecutive days of valid discharge data.
    num_invalid_days is the number of consecutive days in a series that may contain invalid data.
    
    Every row in the cleaned, input dataframe must have valid data points for all stations. '''

    series = pd.DataFrame(columns=['Start Date', 'End Date', 'Number of days in series'])

    init = True
    for index, row in cleaned.iterrows():
        date = datetime.strptime(str(index), "%Y-%m-%d %H:%M:%S")
        if init: # initialise the first time around
            start_date = date
            end_date = date
            init = False
        elif ((date - end_date).days <= num_invalid_days+1):
            # allowed number of days apart, extend set
            end_date = date
        else:  # end the current series
            series_length = (end_date - start_date).days
            if (series_length > 0):
                series = series.append({'Start Date': start_date,
                          'End Date': end_date,
                          'Number of days in series': series_length+1}, ignore_index=True)
            start_date = date
            end_date = start_date
            
    # end the final series
    series_length = (end_date - start_date).days
    if (series_length > 0): # 
        series = series.append({'Start Date': start_date, 'End Date': end_date,
                                'Number of days in series': series_length+1}, ignore_index=True)
    return series

def fill_with_empty_rows(original, first_day, last_day):
    ''' take a dataframe with a sorted Timestamp index (one row per day)
    and add missing days '''
    frame = original.copy()
    for day in (first_day + pd.to_timedelta(n, unit='d') for n in range((last_day-first_day).days + 1)):
        if day not in frame.index:
            frame.loc[day] = pd.Series([np.nan])
            frame = frame.sort_index()
    return(frame)

def fill_nans(value_before, value_after, num_vals):
    ''' Make a list of values, num_vals long, that are a linear interpolation between
    value_before and value_after. '''
    vals = []
    delta = (value_after - value_before) / (num_vals + 1)
    for i in range (num_vals):
        vals.append(value_before + ((i + 1) * delta))
    return vals

def replace_nans(original):
    ''' Return a copy of a dataframe, with the NaNs replaced by linearly interpolated values.
    The values are interpolated for each column/station in turn. '''
    
    interpolated = original.copy()
    for column in original:
        # for each station in turn, look for the invalid discharge values
        init = True
        interp_zone = False
        for index, value in original[column].iteritems():
            if init:
                assert(not np.isnan(value))
                # the first row should be valid as should the last
                low_idx = index
                low_val = value
                init = False
            elif (interp_zone):
                # in a NaN zone,
                # looking for the next valid value so it is possible to interpolate
                if (np.isnan(value)):
                    pass # already in a NaN zone before we got here
                else:
                    high_idx = index
                    high_val = value
                    fill_values = (fill_nans(low_val, high_val, (high_idx - low_idx).days - 1))
                    interpolated.loc[(low_idx + pd.Timedelta(days=1)):
                                     (high_idx - pd.Timedelta(days=1)), column] = fill_values
                    low_idx = index
                    low_val = value
                    interp_zone = False
            else:
                # in a valid value zone, checking for NaNs
                if (np.isnan(value)):
                    interp_zone = True
                else:
                    low_idx = index
                    low_val = value
    return interpolated
