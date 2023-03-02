import os
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename






app = Flask(__name__)


os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'py'

@app.route("/")
def uploadfile():
    return render_template('home.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
      f = request.files['file']
    #   f.save(secure_filename(f.filename))
      print(allowed_file(f.filename))
      if f and allowed_file(f.filename):
        f.save(os.path.join(app.instance_path, 'uploads', secure_filename(f.filename)))
        return 'file uploaded successfully'
    return 'unsuccessful!!'

if __name__ == '__main__':
    app.run(debug=True)

