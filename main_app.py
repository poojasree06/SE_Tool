import os
from flask import Flask, render_template, request,Blueprint
from werkzeug.utils import secure_filename
import glob
import fileinput
import sys
import matplotlib.pyplot as plt
import io
import base64
sys.path.insert(0, "./")
from Tracker.main import Tracker           # Tracker where all metric calculation functions are implemented
import re
from pymongo import MongoClient
import mysql.connector
sys.path.insert(0, "./")
import time


app = Flask(__name__)
os.makedirs(os.path.join(app.instance_path, 'uploads'), exist_ok=True)

@app.route("/")
def index():
    return render_template('main.html')

# ---------------EcoPY Routes and Definitions ------------

@app.route("/ecopy", methods=['POST'])
def ecopy():
    return render_template('ecopy.html')



def allowed_file(filename):
    print(filename.rsplit('.', 1)[1].lower())
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'py'

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


# function to find the function names in the uploaded file
def get_function_names(f):
    function_names = []
    with open(f, 'r') as fl:
        lines = fl.readlines()
        #if the starts with the 'def ' then split that line till it reaches '('
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
        # if no file is found then display the error please upload a file
        if f.filename == '':
            not_uploaded = 'Please select a file to upload.'
            return render_template('home.html', not_uploaded=not_uploaded)
        # if file is in correct format then upload it to the uploaded folder
        if f and allowed_file(f.filename):
            f.save(os.path.join(app.instance_path,
                   'uploads', secure_filename(f.filename)))
            path = 'instance/uploads/' + f.filename
            new_code = '''# This is new code 
import sys
import os
# Add the path to the webapp folder to the system path
sys.path.insert(0,".\Tracker")
from main import Tracker
sys.path.insert(0, ".\python_webapp")
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
            return render_template("ecopy_successful.html", name=filename)
        
    if request.method == 'GET':
        # We get directory of current uploaded folder here
        upload_dir = os.path.join(app.instance_path, 'uploads')
        # Get all files with .py extension in the upload directory
        py_files = glob.glob(os.path.join(upload_dir, '*.py'))
        
        if len(py_files) == 1:
            example_path = py_files[0]
            print(example_path)
            # Run the file 
            result = os.popen(f'python {example_path}').readlines()[-1]
            # ...
        else:
            print('No .py file found in the upload directory')
        output = result
        # convert the output string into dictionary
        my_dict = eval(output)
        #if function is called multiple times, then take the average of all the values we get for every run
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
        # create one more new dictionary without keeping the entire file metric values to display in the graphs
        new_dict = {key: value for key, value in my_dict.items() if key != 'Entire_File'}
        graphs = []
        graph_title = []
        # append all the four titles for all the graphs
        graph_title.append("Energy Usage of CPU")
        graph_title.append("Energy Usage of RAM")
        graph_title.append("Total Energy Consumption")
        graph_title.append("Carbon Footprint")
        for i in range(4):
            # plot the graph
            fig, ax = plt.subplots()
            for key, values in new_dict.items():
                ax.bar(key, values[i], width=0.4)
            #set the title for the respective graph
            ax.set_title(f'{graph_title[i]}')
            ax.legend()
            img = io.BytesIO()
            #save the graph in the png and show it in the web
            fig.savefig(img, format='png')
            #append all the 4 graphs to the graphs list
            graphs.append(base64.b64encode(img.getvalue()).decode())
        print(output)
        return render_template('ecopy_result.html', my_dict=my_dict, graphs=graphs)
    return render_template('ecopy_unsuccessful.html')



# display the output in the results html page
@app.route('/display')
def display():
    output = request.args.get('output')
    return render_template('ecopy_result.html', output=output)


# ----------------- EcoDB routes and Definitions ---------------

@app.route('/ecodb', methods=['POST'])
def ecodb():
    return render_template('ecodb.html')

@app.route('/comparision')
def comparision():
    return render_template('comparision.html')


@app.route('/execute_query')
def execute_query():
    return render_template('query_home.html')

@app.route('/compare', methods=['POST'])
def compare():
    sql_query = request.form['sql_query']
    sql_db_name = request.form['sql_db_name']
    password = request.form['password']
    nosql_query = request.form['nosql_query']
    nosql_db_name = request.form['nosql_db_name']
    sql_res = execute_sql_query(sql_query, 'root', password, sql_db_name)
    time.sleep(1)
    nosql_res = execute_noSQL_query(nosql_query, nosql_db_name)
    eff_res = []
    for i in range(2,len(sql_res)):
        if sql_res[i] < nosql_res[i]:
            eff_res.append("SQL")
        else:
            eff_res.append("NOSQL")
    return render_template('compare_result.html', sql_cpu_consumption=sql_res[0], sql_ram_consumption=sql_res[1], sql_total_consumption=sql_res[2], sql_co2_emissions=sql_res[3], 
                           nosql_cpu_consumption=nosql_res[0], nosql_ram_consumption=nosql_res[1], nosql_total_consumption=nosql_res[2], nosql_co2_emissions=nosql_res[3],
                           efficient_total_consumption=eff_res[0], efficient_co2_emissions=eff_res[1])


@app.route('/details', methods=['POST'])
def execute_query_helper():
    query = request.form['query']
    if len(query)==0:
        not_query = 'Please enter your query.'
        return render_template('ecodb.html', not_query=not_query)
    elif is_sql(query):
        lang = "SQL"
        return render_template('sql_details.html', query=query, lang=lang)
    elif is_nosql(query):
        lang = "NoSQL"
        return render_template('nosql_details.html', query=query, lang=lang)
    else:
        not_query = 'Please enter a valid query.'
        return render_template('ecodb.html', not_query=not_query)


@app.route('/display', methods=['POST'])
def display1():
    lang = request.form['lang']
    query = request.form['query']
    if lang == "SQL":
        password = request.form['password']
        db_name = request.form['db_name']
        res = execute_sql_query(query, 'root', password, db_name)
    else:
        db_name = request.form['db_name']
        res = execute_noSQL_query(query, db_name)

    return render_template('ecodb_result.html', cpu_consumption=res[0], ram_consumption=res[1], total_consumption=res[2], co2_emissions=res[3],mile_eqivalents=res[4],tv_minutes=res[5])

def carbon_to_miles(kg_carbon):
    '''
    8.89 × 10-3 metric tons CO2/gallon gasoline ×
    1/22.0 miles per gallon car/truck average ×
    1 CO2, CH4, and N2O/0.988 CO2 = 4.09 x 10-4 metric tons CO2E/mile
    Source: EPA
    '''
    f_carbon = float(kg_carbon)
    return 4.09 * 10**(-7) * f_carbon # number of miles driven by avg car

def carbon_to_tv(kg_carbon):
    '''
    Gives the amount of minutes of watching a 32-inch LCD flat screen tv required to emit and
    equivalent amount of carbon. Ratio is 0.097 kg CO2 / 1 hour tv
    '''
    f_carbon = float(kg_carbon)
    return f_carbon * (1 / .097) * 60

'''
@input : String  - given query 
@output: Boolean - True - SQL       
@desc  : detects whether given query is SQL or not

done by Poojasree
'''
def is_sql(query):
    sql_keywords = ["SELECT","UPDATE", "DELETE", "INSERT INTO" "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False

'''
@input : String  - given query 
@output: Boolean - True - NoSQL     
@desc  : detects whether given query is NoSQL or not

done by Manasa
'''
def is_nosql(query):
    nosql_keywords = ["insertOne","insertMany","find","findOne","updateOne","updateMany","deleteOne","deleteMany"]
    split_query=query.split('.')
    idx = split_query[2].find("(")
    key = split_query[2][:idx]
    if split_query[0] == "db" and len(split_query)>2:
        if key in nosql_keywords:
            return True
    return False

'''
@input : String - query , String : db_name
@output: Array consists of query energy consumption by CPU,RAM and CO2 emissions
@desc  : calculates the cpu,ram consumptions and CO2 emissions of SQL query by initializing a tracker object just before the start of the query execution and the object stops at the end of query execution

done by Manasa and Namitha
'''
def execute_sql_query(query,db_user,db_password,db_name):
    obj = Tracker()
    # Tracker object starts to calculate the cpu,ram consumptions
    obj.start()
    res = []
    connection = mysql.connector.connect(user=db_user, password=db_password, host='localhost', database=db_name)
    cursor = connection.cursor()
    cursor.execute(query)
    splitted_query=query.upper().split()
    if splitted_query[0]=="DELETE" or splitted_query[0]=="UPDATE" or ( splitted_query[0]=="INSERT" and splitted_query[1]=="INTO"):
        connection.commit()  # commit the changes
        connection.close()
    else:     
        result_set = cursor.fetchall()
        print(result_set)
        connection.close()
    #Tracker object stops 
    obj.stop()
    
    # store the cpu and ram consumptions,CO2 emissions
    res.append(obj.cpu_consumption())
    res.append(obj.ram_consumption())
    res.append(obj.consumption())
    res.append(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])
    res.append(carbon_to_miles(obj._construct_attributes_dict()['CO2_emissions(kg)'][0]))
    res.append(carbon_to_tv(obj._construct_attributes_dict()['CO2_emissions(kg)'][0]))
    return res

'''
@input : String - query , String : db_name
@output: Array consists of query energy consumption by CPU,RAM and CO2 emissions
@desc  : calculates the cpu,ram consumptions and CO2 emissions of MongoDB query by initializing a tracker object just before the start of the query execution and the object stops at the end of query execution

done by Poojasree
'''
def execute_noSQL_query(query,db_name):
    client = MongoClient('mongodb://localhost:27017/')
    obj = Tracker()
    # Tracker object starts to calculate the cpu,ram consumptions
    obj.start()
    res = []
    
    # split the query string as [db,collection,query_field]
    splitted_query=query.split('.')
    collection_name=splitted_query[1]
    
    db = client[db_name]
    collection=db[collection_name]
    query_field=splitted_query[2]
    
    # store aggregate functions like count(),sort() in additonal_funcs
    additional_funcs=[]
    if len(splitted_query)>3:
        for i in range(3,len(splitted_query)):
            additional_funcs.append(splitted_query[i])
            print(splitted_query[i])

    # executes the query operation from the query_field 
    if "insertOne" in query_field:
        print("inserting one document")
        query_doc = query_field.split('insertOne(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.insert_one(*arg_dict)
        print(result)
        
    if "insertMany" in query_field:
        print("inserting many documents")
        query_doc = query_field.split('insertMany(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.insert_many(*arg_dict)
        print(result)
        
    if "find" in query_field:
        print("finding documents")
        query_doc = query_field.split('find(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.find(*arg_dict)
        print(result)
        
    if "findOne" in query_field:
        print("finding documents")
        query_doc = query_field.split('findOne(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.find_one(*arg_dict)
        
    if "updateOne" in query_field:
        print("update one document")
        query_doc = query_field.split('updateOne(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        # print(split_quer_doc)
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.update_one(*arg_dict)
        print(result.modified_count)
    
    if "updateMany" in query_field:
        print("update one document")
        query_doc = query_field.split('updateMany(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.update_many(*arg_dict)
        print(result.modified_count)
        
    if "deleteOne" in query_field:
        print("deleting one document")
        query_doc = query_field.split('deleteOne(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.delete_one(*arg_dict)
        print(result)
        
    if "deleteMany" in query_field:
        print("deleting many documents")
        query_doc = query_field.split('deleteMany(')[1].split(')')[0]
        split_quer_doc=query_doc.split(',')
        arg_dict=[]
        for q in split_quer_doc:
            arg_dict.append(eval(q))
            
        result=collection.delete_many(*arg_dict)
        print(result)
        
    client.close()
    #Tracker object stops 
    obj.stop()
    
    # store the cpu and ram consumptions,CO2 emissions
    res.append(obj.cpu_consumption())
    res.append(obj.ram_consumption())
    res.append(obj.consumption())
    res.append(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])
    res.append(carbon_to_miles(obj._construct_attributes_dict()['CO2_emissions(kg)'][0]))
    res.append(carbon_to_tv(obj._construct_attributes_dict()['CO2_emissions(kg)'][0]))
    return res


'''
main program
'''
if __name__ == '__main__':
    app.run(debug=True)
