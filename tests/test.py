# from hardware.cpu_metrics import CPU
import sys
sys.path.insert(0, ".\hardware")
from cpu_metrics import CPU

obj=CPU()
print(obj)
print("---------")
print(obj.tdp())  
print("---------")
print(obj.name())
print("---------")
print(obj.cpu_num())
