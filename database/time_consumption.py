import re
from pymongo import MongoClient
import mysql.connector
import psutil
import time
import sys
sys.path.insert(0, "./")
from main import Tracker           # Tracker where all metric calculation functions are implemented

def is_sql(query):
    sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False


def execute_query(query, database_type):
    if database_type == "SQL":
        print('SQL Code')
        connection = mysql.connector.connect(user='root', password='password of mysql', host='localhost', database='')
        cursor = connection.cursor()
        cursor.execute(query)
        if query[0] == "I" or query[0] == "D" or query[0] == "U":
            connection.commit()  # commit the changes
            connection.close()
        else:
            result_set = cursor.fetchall()
            connection.close()
            return result_set
    elif database_type == "NoSQL":
        print('NoSQL Code')
        client = MongoClient('mongodb://localhost:27017/')
        db = client['cs20b019']
        client.close()

def calculate_time_consumption(start_time, end_time):
    time_consumption = end_time - start_time
    return time_consumption

start_time = time.time()
query = "UPDATE department SET dname = 'Manasa1' WHERE dnumber = 1234;"

# start_time = time.time()
obj = Tracker()
obj.start()
query = "UPDATE department SET dname = 'Manasa3' WHERE dnumber = 1234;"
lang= "SQL" if is_sql(query) else "NoSQL"  
res=execute_query(query, lang)
# end_time = time.time()
obj.stop()
# time_consumed = calculate_time_consumption(start_time, end_time)
print("CPU Consumption: ",obj.cpu_consumption())
print("RAM Consumption: ",obj.ram_consumption())
print("Total Consumption: ",obj.consumption())
print("CO2 Emmissions: ",obj._construct_attributes_dict()['CO2_emissions(kg)'][0])

# print("Time consumption:", time_consumed)
