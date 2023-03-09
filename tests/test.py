# from hardware.cpu_metrics import CPU
import sys
import os
import json
# sys.path.insert(0, ".\hardware")
# from cpu_metrics import CPU

# obj=CPU()
# print(obj)
# print("---------")
# print(obj.tdp())  
# print("---------")
# print(obj.name())
# print("---------")
# print(obj.cpu_num())
def get_params():
    # filename = resource_stream('SE_TOOL', 'data/config.txt').name
    filename='data/config.txt'
    print(os.path.isfile(filename))
    if not os.path.isfile(filename):
        print(1)
        with open(filename, "w"):
            pass
    with open(filename, "r") as json_file:
        print(2)
        if os.path.getsize(filename):
            dictionary = json.loads(json_file.read())
        else:
            dictionary = {
                "project_name": "Deafult project name",
                "file_name": "emission.csv",
                "measure_period": 10,
                "pue": 1,
                }
    return dictionary

sys.path.insert(0,"./")
from main import Tracker
# obj=Tracker(project_name="project1",file_name="emission.csv",measure_period=10,pue=1)

obj=Tracker() 
obj.start()

get_params()
get_params()
get_params()

obj.stop()

print(obj.cpu_consumption())
print(obj.ram_consumption())
print(obj.consumption())
print(obj._construct_attributes_dict())



