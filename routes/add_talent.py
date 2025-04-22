import streamlit as st
from io import BytesIO
import ssl, os
from functions.chunks import compile_to_chunk
from functions.connection import insert_employee, bulk_insert_to_sql
from functions.extract_cv import extract_cv
from functions.header import header

def add_talent_to_db(data, uploaded_file: BytesIO, pm_email):
    try:
        employee_id = insert_employee(
            data["full_name"],
            data["email"],
            data["title"],
            pm_email,
            uploaded_file.name,
        )
        chunks = compile_to_chunk(data, employee_id, pm_email)
        bulk_insert_to_sql(chunks)
        st.write(f"Successfully added {data['full_name']} to My IT Talent")
        return data
    except Exception as error:
        print(error)

def main(cookies):
    # Upload PDF via Streamlit file uploader
    header("👥", "Add IT Talent")
    
    list_data = []
    uploaded_files = st.file_uploader(
        "Upload CVs (PDF format)", type=["pdf"], accept_multiple_files=True
    )
    if len(uploaded_files) > 0:
        st.write("OpenSSL Version:", ssl.OPENSSL_VERSION)

        if len(uploaded_files) > 3:
            st.error(
                "Maximum processing limit is 3 files at a time, each file representative as 1 IT Talent."
            )
            return "Maximum processing limit is 3 files at a time, each file representative as 1 IT Talent."
        else:
            list_data = extract_cv(uploaded_files)

        for index, data in enumerate(list_data):
            unique_key = f"view_button_{index}_{data['full_name']}"
            dialog_key = f"dialog_{index}_{data['full_name']}"
            confirm_key = f"confirm_{index}_{data['full_name']}"

            @st.dialog(
                f"Confirmation of {data['full_name']} CV Data Extraction",
                key=dialog_key,
                width="large"
            )
            def detail(data=data, uploaded_file=uploaded_files[index]):
                st.json(data)
                st.write(
                    f"By click confirm button we will save it to database and also file pdf (cv)"
                )
                if st.button("Confirm", key=confirm_key):
                    add_talent_to_db(data, uploaded_file, cookies['email'])

            if st.button(
                f"View {data['full_name']} CV Data Extraction",
                key=unique_key
            ):
                detail()

    else:
        st.info(
            f"Please upload PDF files to extract CV data.\n\nMaximum processing limit is 3 files at a time, each file representative as 1 IT Talent."
        )

