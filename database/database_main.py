import re
from pymongo import MongoClient
import mysql.connector
import sys
sys.path.insert(0, "./")
from main import Tracker           # Tracker where all metric calculation functions are implemented

def is_sql(query):
    sql_keywords = ["SELECT","UPDATE", "DELETE", "INSERT INTO" "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False


def execute_sql_query(query,db_user,db_password,db_name):
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

def execute_noSQL_query(query,db_name):
    client = MongoClient('mongodb://localhost:27017/')
    splitted_query=query.split('.')
    collection_name=splitted_query[1]
    
    # print(splitted_query)
    
    db = client[db_name]
    collection=db[collection_name]
    a=splitted_query[2]
    pattern = r'(\w+)\((.*)\)'
    match = re.match(pattern,a)
    function_name = match.group(1)
    argument_str = match.group(2)
    if function_name=="insert_one":
        print("inserting document")
        argument_dict = eval(argument_str)
        result=collection.insert_one(argument_dict)
   
    # print(db)
    # print(collection)
    print(result.inserted_id)
    
    client.close()
    
    return result

# query=input("Enter query: ")
# query = "UPDATE department SET dname = 'Manasa3' WHERE dnumber = 1234;" 
query='db.cats.insert_one({"name":"cat_two"})'
if is_sql(query):
    print('\nDetected database model:  "SQL" ')
    user=input('Enter user: ')
    password=input('Enter password: ')
    database_name=input('Enter database name: ')
    
    ''' Tracker object starts '''

    obj = Tracker()
    obj.start() 
    res=execute_sql_query(query,user,password,database_name)
    obj.stop()

    ''' Tracker object ends '''

else:
    print('Detected database model:  "NoSQL" ')
    db_name=input('Enter database name: ')
    
    ''' Tracker object starts '''
    
    obj=Tracker()
    obj.start()
    res=execute_noSQL_query(query,db_name)
    obj.stop()
    
    ''' Tracker object ends '''

print("CPU Consumption: ",obj.cpu_consumption())
print("RAM Consumption: ",obj.ram_consumption())
print("Total Consumption: ",obj.consumption())
print("CO2 Emmissions: ",obj._construct_attributes_dict()['CO2_emissions(kg)'][0],"\n")
