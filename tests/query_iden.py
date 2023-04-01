import re

def is_sql(query):
    sql_keywords = ["SELECT", "FROM", "WHERE", "JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "ON", "GROUP BY", "HAVING", "ORDER BY", "LIMIT"]
    for keyword in sql_keywords:
        if re.search(r"\b" + keyword + r"\b", query.upper()):
            return True
    return False

query = 'db.car.find( {make: {$in: ["ford","hyundai"] } , year: "2017"} ).pretty()'
print(is_sql(query))