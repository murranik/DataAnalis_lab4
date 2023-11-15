import psycopg2
import os
import csv

from psycopg2 import sql
from tabulate import tabulate 


sql_scripts_folder_path = 'scripts'
csv_folder_path = 'data'

host = "postgres"
database = "postgres"
user = "postgres"
pas = "postgres"
connection = psycopg2.connect(host=host, database=database, user=user, password=pas)
cursor = connection.cursor()
tables = []

def execute_sql_file(file_path):
    with open(file_path, 'r') as script_file:
        sql_script = script_file.read()
        cursor.execute(sql_script)
        print(f"Executed SQL script from {file_path}")

def table_exists(table_name):
    cursor.execute(f"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}');")
    return cursor.fetchone()[0]
        
def create():
    for filename in os.listdir(sql_scripts_folder_path):
        if filename.endswith('.sql'):
            file_path = os.path.join(sql_scripts_folder_path, filename)
            
            table_name = filename[:-4]
            
            if table_exists(table_name):
                cursor.execute(f"DROP TABLE {table_name};")
                print(f"Dropped existing table '{table_name}'")
                connection.commit()
                
            execute_sql_file(file_path)
            
            tables.append(table_name)


def insert_data_from_csv(table_name, csv_file_path):
    with open(csv_file_path, 'r') as csv_file:
        # Use string formatting to insert the table name into the COPY command
        copy_query = f"COPY {table_name} FROM STDIN WITH CSV HEADER"
        cursor.copy_expert(copy_query, csv_file)
        print(f"Inserted data into table '{table_name}' from CSV file {csv_file_path}")

def insert():
    for filename in os.listdir(csv_folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(csv_folder_path, filename)
            
            # Derive the table name from the filename (removing the '.csv' extension)
            table_name = filename[:-4]
            
            # Insert data into the corresponding table
            insert_data_from_csv(table_name, file_path)
         
def show():
    for table in tables:
        # Execute a SELECT query to fetch all rows from the table
        cursor.execute(f"SELECT * FROM {table};")
        
        # Fetch all the rows
        rows = cursor.fetchall()
        
        # Get the column names
        columns = [desc[0] for desc in cursor.description]
        
        # Pretty-print the data using the tabulate library
        print(f"\nTable: {table}")
        print(tabulate(rows, headers=columns, tablefmt='psql'))
            
def main():
    create()
    insert()
    print(tables)
    show()


if __name__ == "__main__":
    main()
