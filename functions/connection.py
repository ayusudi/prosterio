import streamlit as st
import snowflake.connector
from datetime import datetime

conn = snowflake.connector.connect(
  user=st.secrets["snowflake_user"],
  password=st.secrets["snowflake_password"],
  account=st.secrets["snowflake_account"],
  warehouse=st.secrets["snowflake_warehouse"],
  database=st.secrets["snowflake_database"],
  schema=st.secrets["snowflake_schema"],
)

def insert_employee(full_name, github_username, email, role, pm_email, file_path):
    try:
      # Read the PDF file as binary
      with open(file_path, 'rb') as file:
          file_data = file.read()
      
      # SQL query with parameter placeholders
      sql = f"INSERT INTO HELP_PM.PUBLIC.EMPLOYEES (FULL_NAME, GITHUB, EMAIL, ROLE, PM_EMAIL, FILE_DATA) VALUES (%s, %s, %s, %s, %s, %s);"
      
      # Execute the query with parameters
      conn.cursor().execute(sql, (full_name, github_username, email, role, pm_email, file_data))
      sql = f"SELECT ID FROM EMPLOYEES WHERE FULL_NAME = %s AND PM_EMAIL = %s ORDER BY ID DESC LIMIT 1;"
      newdata = conn.cursor().execute(sql, (full_name, pm_email)).fetchone()
      # newdata format to list of tuples
      id = newdata[0]
      return id
    except Exception as e:
      st.error(f"Sorry we are not able to insert the data to the database.")


def bulk_insert_to_sql(data, name):
    try:
      # Define the base SQL query
      base_query = "INSERT INTO CONTENT_CHUNKS (CHUNK_TEXT, NAME, PM_EMAIL, USERID, REF) VALUES "

      # Initialize a list to hold the value tuples
      values_list = []

      # Loop through the list of dictionaries and extract the values
      for record in data:
          chunk_text = record["CHUNK_TEXT"]
          name = record["NAME"]
          pm_email = record["PM_EMAIL"]
          user_id = record["USERID"]
          ref = record["REF"]
          
          # Add the formatted values to the values list
          values_list.append(f"('{chunk_text}', '{name}', '{pm_email}', {user_id}, {ref})")

      # Combine the base query with all the value tuples
      final_query = base_query + ", ".join(values_list) + ";"
      result = conn.cursor().execute(final_query)
      return result
    except Exception as e:
      st.error(f"Sorry we are not able to bulk insert pdf text to the database, but we do manage add {name} to your IT Talent.")

def fetch_cv(file_data):
  output_path = 'cv.pdf'
  with open(output_path, 'wb') as output_file:
    output_file.write(file_data)
    st.pdf(output_path)

