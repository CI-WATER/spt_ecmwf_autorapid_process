# -*- coding: utf-8 -*-
##
##  generate_warning_points_from_return_periods.py
##  spt_ecmwf_autorapid_process
##
##  Created by Alan D. Snow and Scott D. Christensen.
##  Copyright © 2015-2016 Alan D Snow and Scott D. Christensen. All rights reserved.
##  License: BSD-3 Clause

import netCDF4 as nc
import numpy as np
import os
from json import dumps
from RAPIDpy.dataset import RAPIDDataset

def generate_warning_points(ecmwf_prediction_folder, return_period_file, out_directory, threshold=1):
    """
    Create warning points from return periods and ECMWD prediction data

    """

    #Get list of prediciton files

    prediction_files = sorted([os.path.join(ecmwf_prediction_folder,f) for f in os.listdir(ecmwf_prediction_folder) \
                              if not os.path.isdir(os.path.join(ecmwf_prediction_folder, f)) and f.lower().endswith('.nc')],
                              reverse=True)

    #get the comids in ECMWF files
    with RAPIDDataset(prediction_files[0]) as qout_nc:
        prediction_comids = qout_nc.get_river_id_array()
        comid_list_length = qout_nc.size_river_id
    
        first_half_size = 40 #run 6-hr resolution for all
        if qout_nc.is_time_variable_valid():
            if qout_nc.size_time == 41 or qout_nc.size_time == 61:
                #run at full or 6-hr resolution for high res and 6-hr for low res
                first_half_size = 41
            elif qout_nc.size_time == 85 or qout_nc.size_time == 125:
                #run at full resolution for all
                first_half_size = 65

    print "Extracting Forecast Data ..."
    #get information from datasets
    reach_prediciton_array_first_half = np.zeros((comid_list_length,len(prediction_files),first_half_size))
    reach_prediciton_array_second_half = np.zeros((comid_list_length,len(prediction_files),20))
    for file_index, prediction_file in enumerate(prediction_files):
        data_values_2d_array = []
        try:
            ensemble_index = int(os.path.basename(prediction_file)[:-3].split("_")[-1])
            #Get hydrograph data from ECMWF Ensemble
            with RAPIDDataset(prediction_file) as qout_nc:
                data_values_2d_array = qout_nc.get_qout()
        except Exception, e:
            print e
            #pass
        #add data to main arrays and order in order of interim comids
        if len(data_values_2d_array) > 0:
            for comid_index, comid in enumerate(prediction_comids):
                if(ensemble_index < 52):
                    reach_prediciton_array_first_half[comid_index][file_index] = data_values_2d_array[comid_index][:first_half_size]
                    reach_prediciton_array_second_half[comid_index][file_index] = data_values_2d_array[comid_index][first_half_size:]
                if(ensemble_index == 52):
                    if first_half_size == 65:
                        #convert to 3hr-6hr
                        streamflow_1hr = data_values_2d_array[comid_index][:90:3]
                        # get the time series of 3 hr/6 hr data
                        streamflow_3hr_6hr = data_values_2d_array[comid_index][90:]
                        # concatenate all time series
                        reach_prediciton_array_first_half[comid_index][file_index] = np.concatenate([streamflow_1hr, streamflow_3hr_6hr])
                    elif len(data_values_2d_array[comid_index]) == 125:
                        #convert to 6hr
                        streamflow_1hr = data_values_2d_array[comid_index][:90:6]
                        # calculate time series of 6 hr data from 3 hr data
                        streamflow_3hr = data_values_2d_array[comid_index][90:109:2]
                        # get the time series of 6 hr data
                        streamflow_6hr = data_values_2d_array[comid_index][109:]
                        # concatenate all time series
                        reach_prediciton_array_first_half[comid_index][file_index] = np.concatenate([streamflow_1hr, streamflow_3hr, streamflow_6hr])
                    else:
                        reach_prediciton_array_first_half[comid_index][file_index] = data_values_2d_array[comid_index][:]

    print "Extracting Return Period Data ..."
    return_period_nc = nc.Dataset(return_period_file, mode="r")
    riverid_var_name = 'COMID'
    if 'rivid' in return_period_nc.variables:
        riverid_var_name = 'rivid'
    return_period_comids = return_period_nc.variables[riverid_var_name][:]
    return_period_20_data = return_period_nc.variables['return_period_20'][:]
    return_period_10_data = return_period_nc.variables['return_period_10'][:]
    return_period_2_data = return_period_nc.variables['return_period_2'][:]
    return_period_lat_data = return_period_nc.variables['lat'][:]
    return_period_lon_data = return_period_nc.variables['lon'][:]
    return_period_nc.close()

    print "Analyzing Forecast Data with Return Periods ..."
    return_20_points = []
    return_10_points = []
    return_2_points = []
    for prediction_comid_index, prediction_comid in enumerate(prediction_comids):
        #get interim comid index
        return_period_comid_index = np.where(return_period_comids==prediction_comid)[0][0]
        #perform analysis on datasets
        all_data_first = reach_prediciton_array_first_half[prediction_comid_index]
        all_data_second = reach_prediciton_array_second_half[prediction_comid_index]

        return_period_20 = return_period_20_data[return_period_comid_index]
        return_period_10 = return_period_10_data[return_period_comid_index]
        return_period_2 = return_period_2_data[return_period_comid_index]
        #get mean
        mean_data_first = np.mean(all_data_first, axis=0)
        mean_data_second = np.mean(all_data_second, axis=0)
        mean_series = np.concatenate([mean_data_first,mean_data_second])
        mean_peak = np.amax(mean_series)
        if mean_peak > threshold:
            if mean_peak > return_period_20:
                return_20_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 1,
                                          })
            elif mean_peak > return_period_10:
                return_10_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 1,
                                          })
            elif mean_peak > return_period_2:
                return_2_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 1,
                                          })

        #get max
        max_data_first = np.amax(all_data_first, axis=0)
        max_data_second = np.amax(all_data_second, axis=0)
        max_series = np.concatenate([max_data_first,max_data_second])
        max_peak = np.amax(max_series)
        #get std dev
        std_dev_first = np.std(all_data_first, axis=0)
        std_dev_second = np.std(all_data_second, axis=0)
        std_dev = np.concatenate([std_dev_first,std_dev_second])
        #mean plus std
        mean_plus_std_series = mean_series + std_dev
        mean_plus_std_peak = min(np.amax(mean_plus_std_series), max_peak)
        if mean_plus_std_peak > threshold:
            if mean_plus_std_peak > return_period_20:
                return_20_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 0,
                                          })
            elif mean_plus_std_peak > return_period_10:
                return_10_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 0,
                                          })
            elif mean_plus_std_peak > return_period_2:
                return_2_points.append({ "lat" : return_period_lat_data[return_period_comid_index],
                                          "lon" : return_period_lon_data[return_period_comid_index],
                                          "size": 0,
                                          })

    print "Writing Output ..."
    with open(os.path.join(out_directory, "return_20_points.txt"), 'wb') as outfile:
        outfile.write(dumps(return_20_points))
    with open(os.path.join(out_directory, "return_10_points.txt"), 'wb') as outfile:
        outfile.write(dumps(return_10_points))
    with open(os.path.join(out_directory, "return_2_points.txt"), 'wb') as outfile:
        outfile.write(dumps(return_2_points))