import os
import psycopg2
from psycopg2 import Error
from psycopg2 import OperationalError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from http.server import HTTPServer, BaseHTTPRequestHandler



def db_create(table_name="mytable"):


    DB_USER = os.getenv('DB_USER')
    DB_PASSWD = os.getenv('DB_PASSWD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT',"5432")

    create_table_query = "CREATE TABLE "+table_name+" (id SERIAL PRIMARY KEY, name varchar(255), phoneNumber varchar(255), company varchar(255));"
    create_database = 0

    try:
       connection_db = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
    except OperationalError as e:
        if 'database "'+DB_NAME+'" does not exist' in str(e):
            print ("[WARN] - The database '{}' will trying be create.".format(DB_NAME))
            connection_db_create = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT)
            connection_db_create.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor_db_create = connection_db_create.cursor()
            cursor_db_create.execute("CREATE DATABASE "+DB_NAME+";")
            cursor_db_create.close()
            connection_db_create.close()
            create_database = 1

    if create_database:
        connection_db = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)

    try:
        cursor_table = connection_db.cursor()
        cursor_table.execute("SELECT * FROM "+table_name+" LIMIT 1;")
        cursor_table.close()
        connection_db.close()
    except Error as e:
        if 'relation "'+table_name+'" does not exist' in str(e):
            print ("[WARN] - The table '{}' will trying be create.".format(table_name))
            connection_table_create = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT,database=DB_NAME)
            connection_table_create.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor_table_create = connection_table_create.cursor()
            cursor_table_create.execute(create_table_query)
            cursor_table_create.close()
            connection_table_create.close()
    else:
        print("[INFO] - The database was successfully initialized.")
        

def db_query(query):


    DB_USER = os.getenv('DB_USER')
    DB_PASSWD = os.getenv('DB_PASSWD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT',"5432")
    connection = 0
    results = False

    try:
        connection = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)

        cursor = connection.cursor()
        cursor.execute(query)
        if "insert" in query or "INSERT" in query:
            connection.commit()
            results = True
        elif "select" in query or "SELECT" in query:
            results = cursor.fetchall()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
        return results 
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
            return results

def populate_db():
    datas = [
        {"name":"John","number": "(866) 490-3907","company": "Company A"},
        {"name":"Walsh","number": "(831) 450-2422","company": "Company B"},
        {"name":"Walsh","number": "(854) 481-3903","company": "Company C"}
        ]

    if not db_query("select * from mytable limit 1;"):
        db_create()
        for data in datas:
            query = "INSERT INTO mytable (name , phoneNumber , company ) VALUES ('"+data['name']+"','"+data['number']+"','"+data['company']+"')"
            db_query(query)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        html_body = ["<!DOCTYPE html><html><body><table><tr><th>ID</th><th>Name</th><th>PhoneNumber</th><th>Company</th></tr>"]
        db_results = db_query("select * from mytable")
        for row in db_results:
            html_body.append("<tr><td>"+str(row[0])+"</td><td>"+row[1]+"</td><td>"+row[2]+"</td><td>"+row[3]+"</td></tr>")
        html_body.append("</table></body></html>")
        html_page = '\n'.join(html_body)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(html_page.encode('utf-8'))

if __name__ == "__main__":
    
    populate_db()
    httpd = HTTPServer(('0.0.0.0', 80), SimpleHTTPRequestHandler)
    httpd.serve_forever()    
