from rapid_process import run_ecmwf_rapid_process
#main process
#------------------------------------------------------------------------------
if __name__ == "__main__":
    run_ecmwf_rapid_process(
        rapid_executable_location='/home/cecsr/work/rapid/src/rapid',
        rapid_io_files_location='/home/cecsr/rapid-io',
        ecmwf_forecast_location ="/home/cecsr/ecmwf",
        era_interim_data_location="/home/cecsr/era_interim_watershed",
        subprocess_log_directory='/home/cecsr/condor/', #path to store HTCondor/multiprocess logs
        main_log_directory='/home/cecsr/logs/',
        data_store_url='https://ciwckan.chpc.utah.edu',
        data_store_api_key='8dcc1b34-0e09-4ddc-8356-df4a24e5be87',
        data_store_owner_org="brigham-young-university",
	app_instance_id=None,
        sync_rapid_input_with_ckan=False, #make rapid input sync with your app
        download_ecmwf=True,
        ftp_host="ftp.ecmwf.int",
        ftp_login="safer",
        ftp_passwd="neo2008",
        ftp_directory="tcyc",
        upload_output_to_ckan=True,
        initialize_flows=True,
        create_warning_points=True,
        delete_output_when_done=True,
        #autoroute_executable_location='/home/cecsr/scripts/AutoRouteGDAL/source_code/autoroute',
        #autoroute_io_files_location='/home/cecsr/autoroute-io',
        #geoserver_url='http://localhost:8181/geoserver/rest',
        #geoserver_username='admin',
        #geoserver_password='password',
        mp_mode='htcondor', #valid options are htcondor and multiprocess,
        mp_execute_directory='',#required if using multiprocess modep
	date_string = None
    )
