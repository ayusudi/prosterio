# Prosterio

**Prosterio** is a **powerful tool for IT Project Managers** that streamlines tech talent discovery using Retrieval-Augmented Generation (RAG). It extracts relevant data from PDF CVs, processes it, and uses AI-powered matching to identify the most compatible developers for projects. Built with cutting-edge technologies, Prosterio aims to make the recruitment process faster and more efficient.

> Streamline Tech Talent Discovery for Project Managers, Faster Than Ever Before

## Features

- **PDF CV Data Extractor**: Processes PDF files containing CVs, extracts relevant information, and compiles the extracted data into a structured JSON format.
- **Integration with LangChain**: Leverages LangChain for advanced AI-driven operations, utilizing both LangChain's core and community integrations, especially for generating structured outputs from data extraction.
- **RAG Implementation**: Implements Retrieval-Augmented Generation (RAG) to provide more accurate and insightful developer-project matches. Uses RAG with Snowflake and the **mistral-large2** model.
- **Chunking & Embeddings**: Breaks down extracted CV data into chunks and stores embeddings in Snowflake using **snowflake-arctic-embed-l-v2.0**, enhancing search and matching capabilities.
- **Chat Interface**: A built-in chat feature powered by **Streamlit** that allows project managers to interact with the system and query tech talent information. It uses the **Mistral LLM** stored in **Snowflake** for context-aware, real-time answers to questions about developers’ skills, experience, and availability.

## Tech Stack

- **Snowflake**: For cloud-based data storage, query handling, and processing.
- **Snowflake-Arctic-Embed-L-V2.0**: Embedding model to store and retrieve data in Snowflake efficiently.
- **Mistral**: Integration with Mistral AI, used as part of the RAG implementation for advanced language models.
- **Streamlit**: For creating a simple and interactive front-end.
- **LangChain**: Core functionalities and integrations for advanced natural language processing (NLP).
- **PyPDF**: For parsing and extracting data from PDF CV files.
- **Pydantic**: For data validation and parsing.
- **Pandas**: For data manipulation and extraction.
- **Firebase Authentication**: For login with email and password and get token, built-in forget password and verify account.
