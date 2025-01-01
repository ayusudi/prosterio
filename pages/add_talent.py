import streamlit as st
import pandas as pd 
from io import BytesIO
from langchain_mistralai.chat_models import ChatMistralAI
from pydantic import BaseModel, Field
from langchain_community.document_loaders import PyPDFLoader
from typing import List
import ssl
from chunks import compile_to_chunk
from connection import insert_employee, bulk_insert_to_sql
import streamlit.components.v1 as components

st.header("Add IT Talent")
def close_and_destroy(place_holder, full_name, index):
    print(index)
    place_holder.empty()
    st.write(f"Closed and destroyed data for {full_name}")
def add_talent_to_db(data, uploaded_file: BytesIO, placeholder):
    pm_email = st.session_state.user_info["email"]
    employee_id = insert_employee(data["full_name"], data["github_username"], data["email"], data["title"], pm_email, uploaded_file.name)
    chunks = compile_to_chunk(data, employee_id, pm_email)
    bulk_insert_to_sql(chunks)
    # delete file after processing
    
    uploaded_file.seek(0)
    return data


def main():
# Upload PDF via Streamlit file uploader
  list_data = []
  uploaded_files = st.file_uploader("Upload CVs (PDF format)", type=["pdf"], accept_multiple_files=True)

  if uploaded_files is not None:
      print(len(uploaded_files))
      # Display OpenSSL version
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
              github_username: str = Field(description="The candidate's github username or - if not available.")
              title: str = Field(description="The candidate's job title or role, indicating their professional position.")
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
              placeholder=st.container()
              data = extracted_data.model_dump()
              placeholder = st.empty()
              placeholder.write(f"Extracted CV Data for {data['full_name']}")
              placeholder.json(data)
              st.button(label=f"Add {data['full_name']} to My IT Talent", on_click=add_talent_to_db, args=(data, uploaded_file, index), type='primary')
              st.button(label=f"Cancel {data['full_name']}", on_click=close_and_destroy, args=[placeholder, data["full_name"], index], type='secondary')



          except Exception as e:
              st.error(f"An error occurred while processing {uploaded_file.name}: {e}")
  else:
      st.info(f"Please upload PDF files to extract CV data.\n\nMaximum processing limit is 3 files at a time, each file representative as 1 IT Talent.")


main()



# Define the custom component's HTML and JavaScript
html_code = """
<script>
    function sendToPython(className) {
       const elements = document.getElementsByClassName(className);
      
      // Convert the HTMLCollection to an array (since HTMLCollection doesn't have forEach)
      Array.from(elements).forEach(element => {
        // Remove each element from the DOM
        element.remove();
      });
    }
</script>
<button onclick="sendToPython('lala')" class='lala'>Send Message to Python</button>
<h1 class='lala'>Element 1</h1>
"""

# Use Streamlit's components to embed the HTML with JavaScript
result = components.html(html_code,)
components.html("""
<script>
window.addEventListener('load', function() {
  sendToPython('lala') 
});
    
</script>
""")
# Handle the result in Python
if result:
    st.write(f"Message received: {result}")