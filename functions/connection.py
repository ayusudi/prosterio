import streamlit as st
import snowflake.connector

conn = snowflake.connector.connect(
    user=st.secrets["snowflake_user"],
    password=st.secrets["snowflake_password"],
    account=st.secrets["snowflake_account"],
    warehouse=st.secrets["snowflake_warehouse"],
    database=st.secrets["snowflake_database"],
    schema=st.secrets["snowflake_schema"],
)

def destroy(pm_email):
    try:
        sql = "DELETE FROM CONTENT_CHUNKS WHERE PM_EMAIL = %s;"
        conn.cursor().execute(sql, (pm_email))
        sql = "DELETE FROM EMPLOYEES WHERE PM_EMAIL = %s;"
        result = conn.cursor().execute(sql, (pm_email))
        return result
    except Exception as e:
        st.error(f"Sorry we are not able to delete the data from the database.")


def list_employees(email):
    try:
        sql = "SELECT FULL_NAME, EMAIL, ROLE, FILE_DATA FROM EMPLOYEES WHERE PM_EMAIL = %s;"
        result = conn.cursor().execute(sql, (email))
        result = result.fetchall()
        return result
    except Exception as e:
        st.error(f"Sorry we are not able to fetch the data from the database.")


def insert_employee(full_name, email, role, pm_email, file_path):
    try:
        # Read the PDF file as binary
        with open(file_path, "rb") as file:
            file_data = file.read()

        # SQL query with parameter placeholders
        sql = f"INSERT INTO EMPLOYEES (FULL_NAME, EMAIL, ROLE, PM_EMAIL, FILE_DATA) VALUES (%s, %s, %s, %s, %s);"

        # Execute the query with parameters
        conn.cursor().execute(sql, (full_name, email, role, pm_email, file_data))
        sql = f"SELECT ID FROM EMPLOYEES WHERE FULL_NAME = %s AND PM_EMAIL = %s ORDER BY ID DESC LIMIT 1;"
        newdata = conn.cursor().execute(sql, (full_name, pm_email)).fetchone()
        # newdata format to list of tuples
        id = newdata[0]
        return id
    except Exception as e:
        st.error(f"Sorry we are not able to insert the data to the database.")


def bulk_insert_to_sql(data):
    try:
        values_list = []
        for record in data:
            try:
                chunk_text = record["CHUNK_TEXT"].replace("'", "\u0027")
                name = record["NAME"].replace("'", "\u0027")
                pm_email = record["PM_EMAIL"].replace("'", "\u0027")
                user_id = record["USERID"]
                ref = record["REF"]
                values_list.append([chunk_text, name, pm_email, user_id, ref])
            except Exception as e:
                print(f"Error with record: {record} - {e}")

        base_query = "INSERT INTO CONTENT_CHUNKS (CHUNK_TEXT, NAME, PM_EMAIL, USERID, REF) VALUES (%s, %s, %s, %s, %s);"
        cursor = conn.cursor()
        cursor.executemany(base_query, values_list)
        conn.commit()
    except Exception as e:
        print(e, "ERRROR")
        st.error(
            f"Sorry we are not able to bulk insert pdf text to the database, but we do manage add {name} to your IT Talent."
        )


def fetch_cv(file_data):
    output_path = "cv.pdf"
    with open(output_path, "wb") as output_file:
        output_file.write(file_data)
        st.pdf(output_path)


def set_data_file(id, file_path):
    sql = "UPDATE EMPLOYEES SET FILE_DATA = %s WHERE ID = %s;"
    with open(file_path, "rb") as file:
        file_data = file.read()
    conn.cursor().execute(sql, (file_data, id))
    return id
