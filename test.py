import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="",
  database="db_medicine_cabinet"
)

# print(mydb)
cursor = mydb.cursor()

sql = "SELECT * FROM door_logs;"
cursor.execute(sql)
result = cursor.fetchall()

for x in result:
    print(x)