import os
import time
import platform
import pandas as pd
import numpy as np
import uuid
import warnings
import tzlocal
import sys
from apscheduler.schedulers.background import BackgroundScheduler

sys.path.insert(0, ".\hardware")

# from gpu_metrics import GPU, all_available_gpu
from cpu_metrics import CPU, all_available_cpu
from ram_metrics import RAM
from utils import  (
    is_file_opened,
    define_carbon_index,
    get_params,
    set_params,
    # NotNeededExtensionError,
)


FROM_mWATTS_TO_kWATTH = 1000*1000*3600
FROM_kWATTH_TO_MWATTH = 1000


class IncorrectMethodSequenceError(Exception):
    pass

class Tracker:
    def __init__(
        self,
        project_name=None,
        file_name=None,
        measure_period=10,
        emission_level=None,
        alpha_2_code=None,
        region=None,
        cpu_processes="current", 
        pue=1,
        ignore_warnings=False,
        ):
        self._ignore_warnings = ignore_warnings
#         if not self._ignore_warnings:
#             warnings.warn(
#                 message="""
# If you use a VPN, you may have problems with identifying your country by IP.
# It is recommended to disable VPN or
# manually install the ISO-Alpha-2 code of your country during initialization of the Tracker() class.
# You can find the ISO-Alpha-2 code of your country here: https://www.iban.com/country-codes 
# """
# )
        if (type(measure_period) == int or type(measure_period) == float) and measure_period <= 0:
            raise ValueError("\'measure_period\' should be positive number")
        if file_name is not None:
            if type(file_name) is not str and not (file_name is True):
                raise TypeError(f"'file_name' parameter should have str type, not {type(file_name)}")
            if type(file_name) is str and not file_name.endswith('.csv'):
                raise NotNeededExtensionError(f"'file_name' name need to be with extension \'.csv\'")
        self._params_dict = get_params()  # define default params
        self.project_name = project_name if project_name is not None else self._params_dict["project_name"]
        self.file_name = file_name if file_name is not None else self._params_dict["file_name"]
        self._measure_period = measure_period if measure_period is not None else self._params_dict["measure_period"]
        self._pue = pue if pue is not None else self._params_dict["pue"]
        self.get_set_params(self.project_name, self.file_name, self._measure_period, self._pue)

        self._emission_level, self._country = define_carbon_index(emission_level, alpha_2_code, region)
        self._cpu_processes = cpu_processes
        # self._scheduler = BackgroundScheduler(
        #     job_defaults={'max_instances': 10}, 
        #     timezone=str(tzlocal.get_localzone()),
        #     misfire_grace_time=None
        #     )
        self._start_time = None
        self._cpu = None
        self._ram = None
        self._id = None
        self._consumption = 0
        self._cpu_consumption=0
        self._ram_consumption=0
        self._os = platform.system()
        if self._os == "Darwin":
            self._os = "MacOS"
        # self._parameters_to_save = ""
    

        
    def get_set_params(
        self, 
        project_name=None, 
        file_name=None,
        measure_period=None,
        pue=None
        ):
        dictionary = dict()
        if project_name is not None:
            dictionary["project_name"] = project_name
        else: 
            dictionary["project_name"] = "default project name"
        if file_name is not None:
            dictionary["file_name"] = file_name
        else:
            dictionary["file_name"] = "emission.csv"
        if measure_period is not None:
            dictionary["measure_period"] = measure_period
        else:
            dictionary["measure_period"] = 10
        if pue is not None:
            dictionary["pue"] = pue
        else:
            dictionary["pue"] = 1
        set_params(**dictionary)

        return dictionary

    def consumption(self):
        return self._consumption
    
    def cpu_consumption(self):
        return self._cpu_consumption
    
    def ram_consumption(self):
        return self._ram_consumption

    #   The Tracker's id. id is random UUID
    def id(self): 
        return self._id

    #   emission_level is the mass of CO2 in kilos, which is produced  per every MWh of consumed energy.
    def emission_level(self):
        return self._emission_level
    
    #   Period of power consumption measurements.
    #   The more period the more time between measurements.
    #   The default is 10
    def measure_period(self):
          
        return self._measure_period
    
    #   Dictionary with all the attibutes that should be written to .csv file 
    def _construct_attributes_dict(self,):
        attributes_dict = dict()
        attributes_dict["id"] = [self._id]
        attributes_dict["project_name"] = [f"{self.project_name}"]
        attributes_dict["start_time"] = [f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self._start_time))}"]
        attributes_dict["duration(s)"] = [f"{time.time() - self._start_time}"]
        attributes_dict["cpu_power_consumption(kWh)"] = [f"{self._cpu_consumption}"]
        attributes_dict["ram_power_consumption(kWh)"] = [f"{self._ram_consumption}"]
        attributes_dict["power_consumption(kWh)"] = [f"{self._consumption}"]
        attributes_dict["CO2_emissions(kg)"] = [f"{self._consumption * self._emission_level / FROM_kWATTH_TO_MWATTH}"]
        attributes_dict["CPU_name"] = [f"{self._cpu.name()}/{self._cpu.cpu_num()} device(s), TDP:{self._cpu.tdp()}"]
        attributes_dict["OS"] = [f"{self._os}"]
        attributes_dict["region/country"] = [f"{self._country}"]

        return attributes_dict


    def _write_to_csv(self,add_new=False,):    
        attributes_dict = self._construct_attributes_dict()
        if not os.path.isfile(self.file_name):
            while True:
                if not is_file_opened(self.file_name):
                    open(self.file_name, "w").close()
                    tmp = open(self.file_name, "w")
                    pd.DataFrame(attributes_dict).to_csv(self.file_name, index=False)
                    tmp.close()
                    break
                else: 
                    time.sleep(0.5)
                
        else:
            while True:
                if not is_file_opened(self.file_name):
                    tmp = open(self.file_name, "r")
                    attributes_dataframe = pd.read_csv(self.file_name)
                    attributes_array = []
                    for element in attributes_dict.values():
                        attributes_array += element
                    
                    if attributes_dataframe[attributes_dataframe['id'] == self._id].shape[0] == 0:
                        attributes_dataframe.loc[attributes_dataframe.shape[0]] = attributes_array
                    else:
                        row_index = attributes_dataframe[attributes_dataframe['id'] == self._id].index.values[-1]
                        # check, if it's necessary to add a new row to the dataframe
                        if add_new:
                            attributes_dataframe = pd.DataFrame(
                                np.vstack((
                                    attributes_dataframe.values[:row_index+1], 
                                    attributes_array,
                                    attributes_dataframe.values[row_index+1:]
                                    )),
                                columns=attributes_dataframe.columns
                            )
                        else:
                            attributes_dataframe.loc[row_index] = attributes_array
                    attributes_dataframe.to_csv(self.file_name, index=False)
                    tmp.close()
                    break
                else: 
                    time.sleep(0.5)
        self._mode = "run time" if self._mode != "training" else "training"
        return attributes_dict


    def _func_for_sched(self, add_new=False):
        self._cpu.calculate_consumption()
        cpu_consumption = self._cpu.get_consumption()
        ram_consumption = self._ram.calculate_consumption()
        tmp_comsumption = 0
        tmp_comsumption += cpu_consumption
        tmp_comsumption += ram_consumption
        tmp_comsumption *= self._pue
        self._consumption += tmp_comsumption
        self._cpu_consumption=cpu_consumption*self._pue
        self._ram_consumption=ram_consumption*self._pue
        # if self._mode == "shut down":
        #     self._scheduler.remove_job("job")
        #     self._scheduler.shutdown()
        return self._write_to_csv(add_new)



    def start(self):
        # if self._start_time is not None:
        #     try:
        #         self._scheduler.remove_job("job")
        #         self._scheduler.shutdown()
        #     except:
        #         pass
        #     self._scheduler = BackgroundScheduler(job_defaults={'max_instances': 10}, misfire_grace_time=None)
        self._cpu = CPU(cpu_processes=self._cpu_processes, ignore_warnings=self._ignore_warnings)
        self._ram = RAM(ignore_warnings=self._ignore_warnings)
        self._id = str(uuid.uuid4())
        self._mode = "first_time"
        self._start_time = time.time()
        # self._scheduler.add_job(self._func_for_sched, "interval", seconds=self._measure_period, id="job")
        # self._scheduler.start()



    def stop(self, ):
        if self._start_time is None:
            raise Exception("Need to first start the tracker by running tracker.start() or tracker.start_training()")
        # self._scheduler.remove_job("job")
        # self._scheduler.shutdown()
        self._func_for_sched() 
        self._mode = "shut down"

def track(func):  # decorator function
    def inner(*args, **kwargs):
        tracker = Tracker()
        tracker.start()
        try:
            print("tracker")
            returned = func(*args, **kwargs)
        except Exception:
            tracker.stop()
            del tracker
            raise Exception
        tracker.stop()
        print(tracker._construct_attributes_dict())
        del tracker
        return returned
    return inner