import sqlite3

conn = sqlite3.connect("d:\Bugu-backend\instance\demo_flask.sqlite")

cursor = conn.cursor()

sql = "select * from activity"
cursor.execute(sql)

values = cursor.fetchall()
print(values)
