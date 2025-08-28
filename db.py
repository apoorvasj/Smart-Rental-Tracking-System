'''
This script sets up the database based on the provided CSV data.
'''

import pandas as pd 
import psycopg2

df = pd.read_csv('cat_data.csv')
print(df.head())

def connect():
    conn = psycopg2.connect(
        database = "caterpillar_monitor",
        host = "localhost",
        user="postgres",
        password = "4455",
        port = "5432"
    )

    if conn:
        print("Database connected successfully")
    else:
        print("Connection failed")
    return conn

conn = connect()
conn.autocommit = True
cursor = conn.cursor()

sql = '''
CREATE TABLE IF NOT EXISTS caterpillar_data(
   Equipment_ID VARCHAR(50),
   Type VARCHAR(50),
   Site_ID VARCHAR(50),
   Check_Out_Date DATE,
   Check_In_Date DATE,
   Engine_Hours_Day NUMERIC(10,2),
   Idle_Hours_Day NUMERIC(10,2),
   Operating_Days NUMERIC(10,2),
   Last_Operator_ID VARCHAR(50),
   Status VARCHAR(50) CHECK (Status IN('Idle', 'Active', 'Overdue')),
   Location_GPS VARCHAR(100),
   Fuel_Usage_Day NUMERIC(10,2),
   Maintenance_Due DATE,
   Daily_Rate NUMERIC(10,2));'''
   
cursor.execute(sql)
#print("Table created successfully")


with open("C:/Users/My PC/VIT/Caterpillar_Hack_2025/cat_data.csv", "r") as f:
    cursor.copy_expert("COPY caterpillar_data FROM STDIN WITH CSV HEADER DELIMITER ','", f)
print("Data inserted successfully")

sql3 = '''SELECT * FROM caterpillar_data;'''
cursor.execute(sql3)
for i in cursor.fetchall():
    print(i)

conn.commit()
conn.close()