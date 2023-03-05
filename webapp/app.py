import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess
import glob

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
            # Run the file
            result = os.popen(f'python {example_path}').read()
            # ...
        else:
            print('No .py file found in the upload directory')

        output = result
        print(output)
        return redirect(url_for('display', output=output))
    return render_template('unsuccessful.html')


# @app.route('/execute', methods = ['GET', 'POST'])
# def execute():
#     if request.method == 'GET':
#         # changing the path -- ? relative path not working - as of now just taken an example
#         result = subprocess.check_output(["python","D:\OneDrive\Desktop\SE_LAB\SE_TOOL\SE_Tool\instance\calculations\example.py"])
#         output=result.decode("utf-8")
#         print(output)
#         return redirect(url_for('display', output=output))


@app.route('/display')
def display():
    output = request.args.get('output')
    return render_template('results.html', output=output)


if __name__ == '__main__':
    app.run(debug=True)
