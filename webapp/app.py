import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import glob
import fileinput
import sys
import matplotlib.pyplot as plt
import io
import base64
sys.path.insert(0, "./")
from main import Tracker           # Tracker where all metric calculation functions are implemented


app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'py'

@app.route("/")
def uploadfile():
    return render_template('home.html')
metrics_dict = {'Entire_File':[]}
def measure_performance(func):
    def wrapper(*args, **kwargs):
        # Add code to execute before calling the decorated function
        obj = Tracker()
        obj.start()
        
        # Call the decorated function and capture its result
        result = func(*args, **kwargs)
        
        # Add code to execute after calling the decorated function
        obj.stop()
        
        # Add the metrics to the dictionary
        if func.__name__ in metrics_dict:
            metrics_dict[func.__name__].append(obj.cpu_consumption())
            metrics_dict[func.__name__].append(obj.ram_consumption())
            metrics_dict[func.__name__].append(obj.consumption())
            metrics_dict[func.__name__].append(float(obj._construct_attributes_dict()['CO2_emissions(kg)'][0]))
        else:
            metrics_dict[func.__name__] = [obj.cpu_consumption(),obj.ram_consumption(),obj.consumption(),float(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])]
        
        # Return the result of the decorated function
        return result
    return wrapper

def get_function_names(f):
    function_names = []
    with open(f, 'r') as fl:
        lines = fl.readlines()
        for line in lines:
            if 'def ' in line:
                function_names.append(line.split('def ')[1].split('(')[0])
    return function_names

@app.route('/uploader', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files
        print(f'this {f}')
        f = request.files['file']
        filename=f.filename
        if f.filename == '':
            not_uploaded = 'Please select a file to upload.'
            return render_template('home.html', not_uploaded=not_uploaded)
        if f and allowed_file(f.filename):
            f.save(os.path.join(app.instance_path,
                   'uploads', secure_filename(f.filename)))
            path = 'instance/uploads/' + f.filename
            new_code = '''# This is new code 
import sys
import os
# Add the path to the webapp folder to the system path
sys.path.insert(0, ".\webapp")
sys.path.insert(0, "./")
from main import Tracker
from app import measure_performance
from app import metrics_dict
from pathlib import Path
path = Path(__file__)
obj1 = Tracker()
obj1.start()
\n'''.lstrip()
        # Use fileinput to insert the new code at the beginning of the file
            with fileinput.input(path, inplace=True) as f:
                for line in f:
                    if fileinput.isfirstline():
                        print(new_code, end='')
                    print(line, end='')
             # Add decorator function to each function in the user uploaded file
            with fileinput.input(path, inplace=True) as file:
                for line in file:
                    # Find function definition lines
                    if line.startswith('def'):
                        # Extract function name
                        function_name = line.split()[1].split('(')[0]
                        
                        # Write decorator function above function definition
                        print(f"@measure_performance")
                       
                    print(line, end='')
                        # Define the new code to be added to the end of the file
            new_code = '''# This is the new code
\n
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

os.remove(path)       
'''.lstrip()
            # Open the file in append mode and write the new code to the file
            with open(path, 'a') as f:
                f.write(new_code)
            return render_template("successful.html", name=filename)
        
    if request.method == 'GET':
        # We get directory of current uploaded folder here
        upload_dir = os.path.join(app.instance_path, 'uploads')
        # Get all files with .py extension in the upload directory
        py_files = glob.glob(os.path.join(upload_dir, '*.py'))
        
        if len(py_files) == 1:
            example_path = py_files[0]
            # Run the file 
            result = os.popen(f'python {example_path}').readlines()[-1]
            # ...
        else:
            print('No .py file found in the upload directory')
        output = result

        my_dict = eval(output)
        for key, value in my_dict.items():
            if key!='Entire_File':
                count=1
                if len(value) > 4:
                    count=count+1
                    for i in range(4, len(value)):
                        value[i % 4] += float(value[i])
                    value = value[:4]
                for i in range(len(value)):
                    value[i]/=count

        new_dict = {key: value for key, value in my_dict.items() if key != 'Entire_File'}
        graphs = []
        graph_title = []
        graph_title.append("Energy Usage of CPU")
        graph_title.append("Energy Usage of RAM")
        graph_title.append("Power Consumption")
        graph_title.append("Carbon Footprint")
        for i in range(4):
            fig, ax = plt.subplots()
            for key, values in new_dict.items():
                ax.bar(key, values[i], width=0.4)
            ax.set_title(f'{graph_title[i]}')
            ax.legend()
            img = io.BytesIO()
            fig.savefig(img, format='png')
            graphs.append(base64.b64encode(img.getvalue()).decode())
        print(output)
        return render_template('results.html', my_dict=my_dict, graphs=graphs)
    return render_template('unsuccessful.html')




@app.route('/uploader/display')
def display():
    output = request.args.get('output')
    return render_template('results.html', output=output)

if __name__ == '__main__':
    app.run(debug=True)