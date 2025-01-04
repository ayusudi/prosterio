import streamlit as st
from io import BytesIO
from PyPDF2 import PdfReader
from functions.connection import list_employees
import pandas as pd
import matplotlib.pyplot as plt
import base64

st.header("Dashboard")

employees = list_employees()

def display_pdf_from_binary(binary_data):
    """Display a PDF from binary data using iframe in Streamlit."""
    # Encode binary data to base64
    base64_pdf = base64.b64encode(binary_data).decode('utf-8')
    # Create an iframe for the PDF preview
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

# Display total employees
total_employees = len(employees)
st.metric("Total IT Talent", total_employees)

data = []
for index, employee in enumerate(employees):
    name = employee[0]
    email = employee[1]
    role = employee[2]
    cv = employee[3]
    data.append({
        "Name": name,
        "Role": role,
        "Email": email,
        "CV": cv
    })

df = pd.DataFrame(data)

# Toggle for Role Distribution
if st.checkbox("Show Role Distribution"):
    st.subheader("Role Distribution")
    role_counts = df['Role'].value_counts()  # Correctly count roles
    fig, ax = plt.subplots()
    role_counts.plot(kind='bar', color='skyblue', ax=ax)
    ax.set_title("Count of Members by Role")
    ax.set_xlabel("Role")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# Toggle for IT Talents Table
if st.checkbox("Show IT Talents Table"):
    st.write("## My IT Talents")

    # Convert data to a format suitable for st.table
    columns = st.columns((2,2,2,1))
    fields = ['Name', 'Role', 'Email', "Action"]
    for col, field_name in zip(columns, fields):
        col.write(field_name)

    for row in data:
        col1, col2, col3, col4 = st.columns((2,2,2,1))
        col1.write(row['Name'])
        col2.write(row['Role'])
        col3.write(row['Email'])
        button_type = "None" if row["CV"] else "CV"
        if row["CV"] is not None:
            button_hold = col4.empty()
            do_action = button_hold.button("View CV", key=row['Name'])
            if do_action:
                display_pdf_from_binary(row["CV"])
        else:
            col4.write("None")