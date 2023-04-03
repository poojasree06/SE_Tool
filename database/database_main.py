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

    lang= "SQL" if is_sql(query) else "NoSQL"
    res=execute_query(query, lang, password, db_name)

    return render_template('result.html',cpu_consumption=res[0], ram_consumption=res[1],total_consumption=res[2],co2_emissions=res[3])

def is_sql(query):
    sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT", "UPDATE", "INSERT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False


def execute_query(query, database_type, password, db_name):
    obj = Tracker()
    obj.start()
    res = []
    try:
        if database_type == "SQL":
            connection = mysql.connector.connect(user='root', password=password, host='localhost', database=db_name)
            cursor = connection.cursor()
            cursor.execute(query)
            if query[0] == "I" or query[0] == "D" or query[0] == "U":
                connection.commit()  # commit the changes
                connection.close()
            else:
                result_set = cursor.fetchall()
                connection.close()
                res = result_set
        elif database_type == "NoSQL":
            client = MongoClient('mongodb://localhost:27017/')
            db = client[db_name]
            result_set = db.eval(query)
            client.close()
            res = result_set
    except Exception as e:
        print("Error: ", e)
    obj.stop()

    res.append(obj.cpu_consumption())
    res.append(obj.ram_consumption())
    res.append(obj.consumption())
    res.append(obj._construct_attributes_dict()['CO2_emissions(kg)'][0])

    return res



if __name__ == '__main__':
    app.run(debug=True)