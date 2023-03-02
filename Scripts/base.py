import os
import pandas as pd
import GPUtil
import cpuinfo
import re
import time
import psutil

gpu_dataset_path = 'data/gpu.csv'
cpu_dataset_path = 'data/cpu.csv'
regexp_cpu = '(Core|Ryzen).* (i\d-\d{3,5}.?|\d \d{3,5}.?)'


def detect_gpu():
    try:
        gpus = GPUtil.getGPUs()
        gpu_name = gpus[0].name
        print(f'GPU name: {gpu_name}')
        name=gpu_name.replace('NVIDIA ','')
        
        df = pd.read_csv("../data/gpu.csv")
        row = df[df['name'].str.contains(name)]
        
        if row.empty:
            print('GPU not found. Standard TDP= 250 assigned.')
        else:
            TDP = row.TDP.values[0]
            print(TDP)
    except (ValueError, IndexError):
        print('[except] GPU not found. Standard TDP= 250 assigned.')
        

def detect_cpu():
    try:
        cpu_name = cpuinfo.get_cpu_info()['brand_raw']
        print(f'CPU_name: {cpu_name}')
        result = re.search(regexp_cpu, cpu_name)
        if result is not None:
            cpu_name = result.group(1) + ' ' + result.group(2)
            
        df = pd.read_csv("../data/cpu.csv")
        row = df[df['name'].str.contains(cpu_name)]
        
        if row.empty:
            print('CPU not found. Standard TDP=250 assigned.')
        else:
            TDP = row.TDP.values[0]
            print(f'CPU recognized: TDP set to {row.TDP.values[0]}')

    except:
        print('[except] CPU not found. Standard TDP=250 assigned.')
        

def calculate(start,end):
    num_processors = psutil.cpu_count()
    total_power = psutil.cpu_percent() 
    print(total_power)
    avg_power = total_power / num_processors
    total_power = psutil.sensors_battery().power_plugged 
    it_power = psutil.cpu_percent() + psutil.virtual_memory().percent
    pue = total_power / it_power
    Hours_time = (end-start)/(60*60)
    Energy = (Hours_time*num_processors*avg_power*pue)/1000
    print(f'Number of processors : {num_processors}')
    print(f"PUE : {pue}")
    print(f"Average power per processor : {avg_power:.2f} W")
    print(f"Energy : {Energy} KWh")
    print(f"The time of execution of above program is : {(end-start) * 10**3} ms")

    
      
start=time.time()
def test():
    print("hello")
    print("hello")
    
test()
test()
test()
test()
test()
test()
test()

end=time.time()
calculate(start,end)