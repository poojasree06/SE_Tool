import re
from pymongo import MongoClient
import mysql.connector
import psutil
import time

def execute_query(query, database_type):
    if database_type == "SQL":
        connection = mysql.connector.connect(user='root', password='password_of_mysql', host='localhost', database='database_name')
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
        client = MongoClient('mongodb://localhost:27017/')
        db = client['database_name']
        client.close()

def calculate_time_consumption(start_time, end_time):
    time_consumption = end_time - start_time
    return time_consumption

start_time = time.time()
query = "UPDATE department SET dname = 'Manasa1' WHERE dnumber = 1234;"
res=execute_query(query, "SQL")
end_time = time.time()
time_consumed = calculate_time_consumption(start_time, end_time)
print("Time consumption:", time_consumed)
