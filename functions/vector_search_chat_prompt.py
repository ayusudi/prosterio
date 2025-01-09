# IMPORTANT NOTES ===================================
# Not used since I migrated to implement Cortex Search.

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

def chatPromptRAG(question: str, pm_email: str):
    try:
        sql = f"""
    WITH context AS (
        SELECT 
            name,
            chunk_text,
            snowflake.cortex.embed_text_1024('snowflake-arctic-embed-l-v2.0', chunk_text) AS embedding
        FROM 
            "HELP_PM"."PUBLIC"."CONTENT_CHUNKS"
        WHERE PM_EMAIL = '{pm_email}' 
        QUALIFY ROW_NUMBER() OVER (PARTITION BY name ORDER BY name) = 1
        ORDER BY 
            vector_cosine_similarity(embedding, snowflake.cortex.embed_text_1024('snowflake-arctic-embed-l-v2.0', %s)) DESC
    ),
    concatenated_context AS (
        SELECT 
            LISTAGG(chunk_text, ' ') WITHIN GROUP (ORDER BY name) AS combined_context
        FROM context
    )
    SELECT 
        snowflake.cortex.complete(
            'mistral-large2', 
            'Here is our analysis of our employee, please just select the related employee who can help to our question. Make sure your narative is explain the project and the reason ' || 
            '###
            CONTEXT: ' || concatenated_context.combined_context || '
            ###
            QUESTION: ' || %s || '
            ANSWER: '
        ) AS response
    FROM concatenated_context;
    """
        result = conn.cursor().execute(sql, (question, question))
        result = result.fetchall()
        return result
    except Exception as error:
        print(error)
