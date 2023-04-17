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
    if len(query)==0:
        not_query = 'Please enter your query.'
        return render_template('home.html', not_query=not_query)
    elif is_sql(query):
        lang = "SQL"
        return render_template('sql_details.html', query=query, lang=lang)
    elif is_nosql(query):
        lang = "NoSQL"
        return render_template('nosql_details.html', query=query, lang=lang)
    else:
        not_query = 'Please enter a valid query.'
        return render_template('home.html', not_query=not_query)


@app.route('/display', methods=['POST'])
def display():
    lang = request.form['lang']
    query = request.form['query']
    if lang == "SQL":
        password = request.form['password']
        db_name = request.form['db_name']
        res = execute_sql_query(query, 'root', password, db_name)
    else:
        db_name = request.form['db_name']
        res = execute_noSQL_query(query, db_name)

    return render_template('result.html', cpu_consumption=res[0], ram_consumption=res[1], total_consumption=res[2], co2_emissions=res[3])


'''
@input : String  - given query 
@output: Boolean - True - SQL       
@desc  : detects whether given query is SQL or not

done by poojasree
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

done by manasa
'''
def is_nosql(query):
    nosql_keywords = ["insertOne","insertMany","find","findOne","updateOne","updateMany","deleteOne","deleteMany"]
    split_query=query.split('.')
    idx = split_query[2].find("(")
    key = split_query[2][:idx]
    if split_query[0] == "db":
        if key in nosql_keywords:
            return True
    return False

'''
@input : String - query , String : db_name
@output: Array consists of query energy consumption by CPU,RAM and CO2 emissions
@desc  : calculates the cpu,ram consumptions and CO2 emissions of SQL query by initializing a tracker object just before the start of the query execution and the object stops at the end of query execution

done by manasa
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
    return res

'''
@input : String - query , String : db_name
@output: Array consists of query energy consumption by CPU,RAM and CO2 emissions
@desc  : calculates the cpu,ram consumptions and CO2 emissions of MongoDB query by initializing a tracker object just before the start of the query execution and the object stops at the end of query execution

done by poojasree
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
    return res


'''
main program
'''
if __name__ == '__main__':
    app.run(debug=True)