import os
from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import subprocess

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

        result = os.popen(
            'python ..\\SE_TOOL\\instance\\calculations\\example.py').read()

        output = result
        print(output)
        return redirect(url_for('display', output=output))
    return redirect(url_for('unsuccessful'))


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


@app.route('/unsuccuessful')
def unsuccessful():
    return render_template('unsuccessful.html')


if __name__ == '__main__':
    app.run(debug=True)
