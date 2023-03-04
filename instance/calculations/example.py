import sys
sys.path.insert(0, ".\hardware")
from cpu_metrics import CPU
from ram_metrics import RAM

obj=CPU()
print("------------------------------------")
print('number of CPUs: ', obj.cpu_num())
print("------------------------------------")
print('CPU Name: ',obj.name())
print("------------------------------------")
print('TDP value: ',obj.tdp())  
print("------------------------------------")
obj.calculate_consumption()
print('energy consumption due to cpu: ', obj.get_consumption(),'KWh')
obj2=RAM()
obj2.calculate_consumption()
print("------------------------------------")
print('energy consumption due to ram: ',obj2.get_consumption(),'KWh')
print("------------------------------------")
