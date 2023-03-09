import os
import psutil
from pkg_resources import resource_stream
import json
import pandas as pd
import string
import numpy as np
import warnings
import requests
import datetime
import sys
sys.path.insert(0, ".\hardware")
from cpu_metrics import all_available_cpu
# from gpu_metrics import all_available_gpu


# class FileDoesNotExistsError(Exception):
#     pass


# class NotNeededExtensionError(Exception):
#     pass


def available_devices():
    all_available_cpu()
    # all_available_gpu()
    # need to add RAM


def is_file_opened(needed_file):
  
    result = False
    needed_file = os.path.abspath(needed_file)
    python_processes = []
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["name", "cpu_percent", "pid"])
            if "python" in pinfo["name"].lower() or "jupyter" in pinfo["name"].lower():
                python_processes.append(pinfo["pid"])
                flist = proc.open_files()
                if flist:
                    for nt in flist:
                        if needed_file in nt.path:
                            result = True
        except:
            pass
    return result


# class NoCountryCodeError(Exception):
#     pass

def define_carbon_index(emission_level=None, alpha_2_code=None, region=None):
    if alpha_2_code is None and region is not None:
        raise NoCountryCodeError("In order to set 'region' parameter, 'alpha_2_code' parameter should be set")
    carbon_index_table_name = '.\data\carbon_index.csv'
    if alpha_2_code is None:
        try:
            ip_dict = eval(requests.get("https://ipinfo.io/").content)
        except:
            ip_dict = eval(requests.get("https://ipinfo.io/").content.decode('ascii'))
        country = ip_dict['country']
        region = ip_dict['region']
    else:
        country = alpha_2_code
    if emission_level is not None:
        return (emission_level, f'({country}/{region})') if region is not None else (emission_level, f'({country})')
    data = pd.read_csv(carbon_index_table_name)
    result = data[data['alpha_2_code'] == country]
    if result.shape[0] < 1:
        result = data[data['country'] == 'World']
    elif result.shape[0] > 1 and region is None:
        result = result[result['region'] == 'Whole country']
    elif result.shape[0] > 1:
        if result[result['region'] == region].shape[0] > 0:
            result = result[result['region'] == region]
        else: 
            flag = False
            for alternative_names in data[data['alpha_2_code'] == country]["alternative_name"].values:
                if (
                    type(alternative_names) is str and 
                    region.lower() in alternative_names.lower().split(',') and 
                    region != ""
                ):
                    flag = True
                    result = data[data['alternative_name'] == alternative_names]
            
            if flag is False:
                warnings.warn(
                    message=f"""
    Your 'region' parameter value, which is '{region}', is not found in our region database for choosed country. 
    Please, check, if your region name is written correctly
    """
                )
                result = result[result['region'] == 'Whole country']
    result = result.values[0][-1]
    return (result, f'{country}/{region}') if region is not None else (result, f'{country}')


# class IncorrectPricingDict(Exception):
#     pass

def set_params(**params):
    dictionary = dict()
     # filename = resource_stream('SE_TOOL', 'data/config.txt').name
    filename='data/config.txt'
    for param in params:
        dictionary[param] = params[param]
    if "project_name" not in dictionary:
        dictionary["project_name"] = "default project name"
    if "experiment_description" not in dictionary:
        dictionary["experiment_description"] = "default experiment description"
    if "file_name" not in dictionary:
        dictionary["file_name"] = "emission.csv"
    if "measure_period" not in dictionary:
        dictionary["measure_period"] = 10
    if "pue" not in dictionary:
        dictionary["pue"] = 1
    with open(filename, 'w') as json_file:  # store all project details in config.txt
        json_file.write(json.dumps(dictionary))


def get_params():
    # filename = resource_stream('SE_TOOL', 'data/config.txt').name
    filename='data/config.txt'
    if not os.path.isfile(filename):
        with open(filename, "w"):
            pass
    with open(filename, "r") as json_file:
        if os.path.getsize(filename):
            dictionary = json.loads(json_file.read())
        else:
            dictionary = {
                "project_name": "Default project name",
                "experiment_description": "no experiment description",
                "file_name": "emission.csv",
                "measure_period": 10,
                "pue": 1,
                }
    return dictionary
