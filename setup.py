import subprocess

libraries = ['pandas','numpy','matplotlib', 'psutil', 'py-cpuinfo', 'tzlocal', 'geopy', 'geocoder', 'flask', 'werkzeug']

for lib in libraries:
    subprocess.check_call(['pip', 'install', lib])
