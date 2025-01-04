import streamlit as st
import pandas as pd 
from io import BytesIO
from langchain_mistralai.chat_models import ChatMistralAI
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from typing import List
import ssl
from functions.chunks import compile_to_chunk
from functions.connection import insert_employee, bulk_insert_to_sql, set_data_file
import streamlit.components.v1 as components

st.header("Add IT Talent")

def add_talent_to_db(data, uploaded_file: BytesIO):
  try:
    pm_email = st.session_state.user_info["email"]
    employee_id = insert_employee(data["full_name"], data["email"], data["title"], pm_email, uploaded_file.name)
    chunks = compile_to_chunk(data, employee_id, pm_email)
    bulk_insert_to_sql(chunks, data["full_name"])
    st.write(f"Successfully added {data['full_name']} to My IT Talent")
    return data
  except Exception as e:
    print(e)

def main():
  # Upload PDF via Streamlit file uploader
  list_data = []
  uploaded_files = st.file_uploader("Upload CVs (PDF format)", type=["pdf"], accept_multiple_files=True)
  if len(uploaded_files) > 0:
    st.write("OpenSSL Version:", ssl.OPENSSL_VERSION)

    if len(uploaded_files) > 3:
      st.error("Maximum processing limit is 3 files at a time, each file representative as 1 IT Talent.")
      return "Maximum processing limit is 3 files at a time, each file representative as 1 IT Talent."
    
    for index, uploaded_file in enumerate(uploaded_files):
      # Save the uploaded file to a temporary path
      with open(uploaded_file.name, "wb") as f:
        f.write(uploaded_file.read())
      
      # Load and process the PDF
      loader = PyPDFLoader(uploaded_file.name)
      pages = loader.load_and_split()

      # Combine text content from all pages
      text = " ".join([page.page_content for page in pages])

      # Define CV Data Extraction model schema
      class CVDataExtraction(BaseModel):
        full_name: str = Field(description="The full name of the candidate, used as their username in the system.")
        email: str = Field(description="The candidate's email address for identification and communication purposes.")
        title: str = Field(description="The candidate's main title.")
        job_titles: str = Field(description="A summary of the candidate's current or most recent job titles.")
        promotion_years: int = Field(description="The year the candidate started their professional career.")
        profile: str = Field(description="A brief overview of the candidate's professional profile, including their key attributes and expertise.")
        skills: List[str] = Field(description="A list of the candidate's soft and technical skills, showcasing their capabilities.")
        professional_experiences: List[str] = Field(description="Detailed information about the candidate's professional work experiences, including company, roles, duration, start date or year, and responsibilities.")
        educations: List[str] = Field(description="Educational qualifications of the candidate, including degrees, institutions, and graduation years or ongoing.")
        publications: List[str] = Field(description="Any publications authored or co-authored by the candidate, such as articles, papers, or books.")
        distinctions: List[str] = Field(description="Awards, honors, or recognitions received by the candidate throughout their career or education.")
        certifications: List[str] = Field(description="Professional certifications achieved by the candidate, indicating their specialized knowledge and qualifications.")

      # Initialize the model
      api_key = st.secrets.get("MISTRAL_API_KEY")
      if not api_key:
        st.error("API key for Mistral AI is not set. Please set the MISTRAL_API_KEY environment variable.")
      model = ChatMistralAI(api_key=api_key, model='mistral-large-latest')

      # Use the structured output model
      structured_llm = model.with_structured_output(CVDataExtraction)
      # Extract data using the model
      try:
        extracted_data = structured_llm.invoke(text)
        data = extracted_data.model_dump()
        list_data.append(data)
      except Exception as e:
        st.error(f"An error occurred while processing {uploaded_file.name}: {e}")

    for index, data in enumerate(list_data):
      @st.dialog(f"Confirmation of {data['full_name']} CV Data Extraction", width="large")
      def detail(data, uploaded_file):
        st.json(data)
        st.write(f"By click confirm button we will save it to database and also file pdf (cv)")
        if st.button("Confirm", key=f"Confirm {data['full_name']}"):
          add_talent_to_db(data, uploaded_file)
      if st.button(f"View {data['full_name']} CV Data Extraction", key=data["full_name"]):
        detail(data, uploaded_files[index])   

  else:
    st.info(f"Please upload PDF files to extract CV data.\n\nMaximum processing limit is 3 files at a time, each file representative as 1 IT Talent.")


main()

