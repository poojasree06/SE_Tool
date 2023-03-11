# This is new code 
import sys
import os
# Add the path to the webapp folder to the system path
sys.path.insert(0, ".\webapp")
sys.path.insert(0, "./")
from main import Tracker
from app import measure_performance
from app import metrics_dict
obj1 = Tracker()
obj1.start()

# import sys
# sys.path.insert(0, "./")
# from main import track
# @track
@measure_performance
def get_params():
    dictionary = {
                "project_name": "Deafult project name",
                "file_name": "emission.csv",
                "measure_period": 10,
                "pue": 1,
                }
    return dictionary

print(get_params())




# This is the new code


obj1.stop()
metrics_dict['Entire_File'].append(obj1.cpu_consumption())
metrics_dict['Entire_File'].append(obj1.ram_consumption())
metrics_dict['Entire_File'].append(obj1.consumption())
metrics_dict['Entire_File'].append(obj1._construct_attributes_dict()['CO2_emissions(kg)'][0])
# system_details=[]
# system_details.append(obj1._construct_attributes_dict()['OS'][0])
# system_details.append(obj1._construct_attributes_dict()['CPU_name'][0])
# metrics_dict['Entire_File'].append(system_details)
metrics_dict['Entire_File'].append(obj1._construct_attributes_dict()['OS'][0])
metrics_dict['Entire_File'].append(obj1._construct_attributes_dict()['CPU_name'][0])
print(metrics_dict)
