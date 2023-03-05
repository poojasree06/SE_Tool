import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import glob
import fileinput


app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)


def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'py'


@app.route("/")
def uploadfile():
    return render_template('home.html')


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
        if f.filename == '':
            return ('No selected file')
        if f and allowed_file(f.filename):
            f.save(os.path.join(app.instance_path,
                   'uploads', secure_filename(f.filename)))
            path = 'instance/uploads/' + f.filename
            function_names = get_function_names(path)
            # print(function_names)
            return render_template("successful.html", name=f.filename)

    if request.method == 'GET':
        # We get directory of current uploaded folder here
        upload_dir = os.path.join(app.instance_path, 'uploads')

        # Get all files with .py extension in the upload directory
        py_files = glob.glob(os.path.join(upload_dir, '*.py'))

        # If there are multiple files with .py extension in the upload directory
        if len(py_files) > 1:
            # Display a list of all the .py files in the upload directory
            print("Multiple .py files found in the upload directory:")
            for i, file_path in enumerate(py_files):
                print(f"{i+1}. {os.path.basename(file_path)}")
            # Prompt the user to select the file they want to run
            selection = input("Enter the number of the file you want to run: ")
            # Verify the user's selection
            if not selection.isdigit() or int(selection) not in range(1, len(py_files)+1):
                print("Invalid selection")
            else:
                # Run the selected file
                example_path = py_files[int(selection)-1]
                result = os.popen(f'python {example_path}').read()
                # ...
        # If there is only one file with .py extension in the upload directory
        elif len(py_files) == 1:
            example_path = py_files[0]
            new_code = '''# This is new code 
import sys
sys.path.insert(0, ".\hardware")
from cpu_metrics import CPU
from ram_metrics import RAM

obj=CPU()\n'''.lstrip()
            with fileinput.input(example_path, inplace=True) as f:
                for line in f:
                    # Check if the line contains a print statement
                    if 'print(' in line:
                        # Comment out the print statement by adding a #
                        line = '#' + line
                    # Print the modified line to the file
                    print(line, end='')

        # Use fileinput to insert the new code at the beginning of the file
            with fileinput.input(example_path, inplace=True) as f:
                for line in f:
                    if fileinput.isfirstline():
                        print(new_code, end='')
                    print(line, end='')
            # Define the new code to be added to the end of the file
            new_code = '''# This is the new code
print(obj)
print("---------")
print(obj.tdp())  
print("---------")
print(obj.name())
print("---------")
print(obj.cpu_num())
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
print("------------------------------------")\n'''.lstrip()

            # Open the file in append mode and write the new code to the file
            with open(example_path, 'a') as f:
                f.write(new_code)

            # Run the file
            result = os.popen(f'python {example_path}').read()
            # ...
        else:
            print('No .py file found in the upload directory')

        output = result
        print(output)
        return redirect(url_for('display', output=output))
    return render_template('unsuccessful.html')



@app.route('/display')
def display():
    output = request.args.get('output')
    return render_template('results.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)
