# This code will execute a query that will create the database in your local server
# after running this code with "python createDB.py " run the command "python manage.py migrate"

import mysql.connector
from decouple import config

dataBase = mysql.connector.connect(
    host=config("DB_HOST", "db"),
    # your password maybe different so enter the password you setup on mysql
    password=config("MYSQL_PASSWORD"),
)

cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE sampleshare_db")

print("Database Successfully Created!!")
print("Please run the command 'docker compose run web python manage.py migrate' ")
