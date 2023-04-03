import re
from pymongo import MongoClient
import mysql.connector
import sys
sys.path.insert(0, "./")
from main import Tracker           # Tracker where all metric calculation functions are implemented
from flask import Flask, render_template, request


app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/execute_query', methods=['POST'])
def execute_query_helper():
    query = request.form['query']
    password = request.form['password']
    db_name = request.form['db_name']

    if is_sql(query):
        lang= "SQL"
        res=execute_sql_query(query, 'root', password, db_name)
    else:
        lang="NoSQL"
        res=execute_noSQL_query(query,db_name)

    return render_template('result.html',cpu_consumption=res[0], ram_consumption=res[1],total_consumption=res[2],co2_emissions=res[3])

def is_sql(query):
    sql_keywords = ["SELECT","UPDATE", "DELETE", "INSERT INTO" "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False


def execute_sql_query(query,db_user,db_password,db_name):
    obj = Tracker()
    obj.start()
    res = []
    print('\nDetected database model:  "SQL" ')
    connection = mysql.connector.connect(user=db_user, password=db_password, host='localhost', database=db_name)
    cursor = connection.cursor()
    cursor.execute(query)
    splitted_query=query.split()
    if splitted_query[0]=="DELETE" or splitted_query[0]=="UPDATE" or ( splitted_query[0]=="INSERT" and splitted_query[1]=="INTO"):
        connection.commit()  # commit the changes
        connection.close()
    else:     
        result_set = cursor.fetchall()
        connection.close()
        return result_set
    obj.stop()
    res.append(obj.cpu_consumption())
    res.append(obj.ram_consumption())
    res.append(obj.consumption())
    res.append(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])
    return res


def execute_noSQL_query(query,db_name):
    obj = Tracker()
    obj.start()
    res = []
    print('Detected database model:  "NoSQL" ')
    client = MongoClient('mongodb://localhost:27017/')
    db = client[db_name]
    client.close()
    obj.stop()
    res.append(obj.cpu_consumption())
    res.append(obj.ram_consumption())
    res.append(obj.consumption())
    res.append(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])
    return res

# query=input("Enter query: ")
# query = "UPDATE department SET dname = 'Manasa3' WHERE dnumber = 1;" 

# if is_sql(query):
#     user=input('Enter user: ')
#     password=input('Enter password: ')
#     database_name=input('Enter database name: ')
    
#     ''' Tracker object starts '''

#     obj = Tracker()
#     obj.start() 
#     res=execute_sql_query(query,user,password,database_name)
#     obj.stop()

#     ''' Tracker object ends '''

# else:
#     db_name=input('Enter database name: ')
    
#     ''' Tracker object starts '''
    
#     obj=Tracker()
#     obj.start()
#     res=execute_noSQL_query(query,db_name)
#     obj.stop()
    
#     ''' Tracker object ends '''


if __name__ == '__main__':
    app.run(debug=True)