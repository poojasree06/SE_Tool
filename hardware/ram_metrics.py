import psutil
import time
import os


FROM_WATTs_TO_kWATTh = 1000*3600


class RAM():
    def __init__(self, ignore_warnings=False):
        self._consumption = 0
        self._ignore_warnings = ignore_warnings
        self._start = time.time()


    def get_consumption(self):
        self.calculate_consumption()
        return self._consumption
    

    def _get_memory_used(self,):
        current_pid = os.getpid()
        memory_percent = 0
        
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['name', 'pid', 'memory_percent'])
                if pinfo['pid'] == current_pid:
                    memory_percent = float(pinfo['memory_percent'])
            except (psutil.NoSuchProcess, psutil.AccessDenied , psutil.ZombieProcess) :
                pass

        total_memory = psutil.virtual_memory().total / (1024 ** 3)
        return memory_percent * total_memory / 100


    def calculate_consumption(self):
        time_period = time.time() - self._start
        self._start = time.time()
        consumption = self._get_memory_used() * (3 / 8) * time_period / FROM_WATTs_TO_kWATTh
        self._consumption += consumption
        # print(self._consumption)
        return consumption