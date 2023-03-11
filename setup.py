import subprocess

libraries = [psutil, GPUtil, pandas, numpy, py-cpuinfo,
             APScheduler, tzlocal, pynvml, geopy, geocoder, flask, werkzeug, matplotlib]

for lib in libraries:
    subprocess.check_call(['pip', 'install', lib])