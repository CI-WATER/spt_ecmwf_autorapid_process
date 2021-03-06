# -*- coding: utf-8 -*-
##
##  helper_functions.py
##  spt_ecmwf_autorapid_process
##
##  Created by Alan D. Snow.
##  Copyright © 2015-2016 Alan D Snow. All rights reserved.
##  License: BSD-3 Clause

import datetime
from glob import glob
import os
import re
from shutil import rmtree

#----------------------------------------------------------------------------------------
# HELPER FUNCTIONS
#----------------------------------------------------------------------------------------
def case_insensitive_file_search(directory, pattern):
    """
    Looks for file with pattern with case insensitive search
    """
    try:
        return os.path.join(directory,
                            [filename for filename in os.listdir(directory) \
                             if re.search(pattern, filename, re.IGNORECASE)][0])
    except IndexError:
        print pattern, "not found"
        raise

def clean_logs(condor_log_directory, main_log_directory, prepend="rapid_"):
    """
    This removed logs older than one week old
    """
    date_today = datetime.datetime.utcnow()
    week_timedelta = datetime.timedelta(7)
    #clean up condor logs
    condor_dirs = [d for d in os.listdir(condor_log_directory) if os.path.isdir(os.path.join(condor_log_directory, d))]
    for condor_dir in condor_dirs:
        try:
            dir_datetime = datetime.datetime.strptime(condor_dir[:11], "%Y%m%d.%H")
            if (date_today-dir_datetime > week_timedelta):
                rmtree(os.path.join(condor_log_directory, condor_dir))
        except Exception as ex:
            print ex
            pass

    #clean up log files
    main_log_files = [f for f in os.listdir(main_log_directory) if not os.path.isdir(os.path.join(main_log_directory, f))]
    for main_log_file in main_log_files:
        try:
            log_datetime = datetime.datetime.strptime(main_log_file, "{0}%y%m%d%H%M%S.log".format(prepend))
            if (date_today-log_datetime > week_timedelta):
                os.remove(os.path.join(main_log_directory, main_log_file))
        except Exception as ex:
            print ex
            pass

def find_current_rapid_output(forecast_directory, watershed, subbasin):
    """
    Finds the most current files output from RAPID
    """
    if os.path.exists(forecast_directory):
        basin_files = glob(os.path.join(forecast_directory,"Qout_%s_%s_*.nc" % (watershed, subbasin)))
        if len(basin_files) >0:
            return basin_files
    #there are none found
    return None

def get_valid_watershed_list(input_directory):
    """
    Get a list of folders formatted correctly for watershed-subbasin
    """
    valid_input_directories = []
    for directory in os.listdir(input_directory):
        if os.path.isdir(os.path.join(input_directory, directory)) \
            and len(directory.split("-")) == 2:
            valid_input_directories.append(directory)
        else:
            print directory, "incorrectly formatted. Skipping ..."
    return valid_input_directories

def get_date_timestep_from_forecast_folder(forecast_folder):
    """
    Gets the datetimestep from forecast
    """
    #OLD: Runoff.20151112.00.netcdf.tar.gz
    #NEW: Runoff.20160209.0.exp69.Fgrid.netcdf.tar
    forecast_split = os.path.basename(forecast_folder).split(".")
    forecast_date_timestep = ".".join(forecast_split[1:3])
    return re.sub("[^\d.]+", "", forecast_date_timestep)

def get_ensemble_number_from_forecast(forecast_name):
    """
    Gets the datetimestep from forecast
    """
    #OLD: 20151112.00.1.205.runoff.grib.runoff.netcdf
    #NEW: 52.Runoff.nc
    forecast_split = os.path.basename(forecast_name).split(".")
    if forecast_name.endswith(".205.runoff.grib.runoff.netcdf"):
        ensemble_number = int(forecast_split[2])
    else:
        ensemble_number = int(forecast_split[0])
    return ensemble_number

def get_watershed_subbasin_from_folder(folder_name):
    """
    Get's the watershed & subbasin name from folder
    """
    input_folder_split = folder_name.split("-")
    watershed = input_folder_split[0].lower()
    subbasin = input_folder_split[1].lower()
    return watershed, subbasin

def log(message, severity):
    """Logs, prints, or raises a message.

    Arguments:
        message -- message to report
        severity -- string of one of these values:
            CRITICAL|ERROR|WARNING|INFO|DEBUG
    """

    print_me = ['WARNING', 'INFO', 'DEBUG']
    if severity in print_me:
        print severity, message
    else:
        raise Exception(message)


if __name__=="__main__":
    #update_inital_flows_usgs('/home/alan/work/rapid-io/input/erdc_texas_gulf_region-huc_2_12/', '20150826.0')
    print datetime.datetime(2015, 9, 9, 18) - datetime.datetime(2015, 8, 26, 0)