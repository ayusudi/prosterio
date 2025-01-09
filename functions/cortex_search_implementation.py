import streamlit as st
from snowflake.core import Root  # requires snowflake>=0.8.0
from snowflake.cortex import Complete
from snowflake.snowpark.session import Session

# INITIALIZATION =================================================================================

session = Session.builder.configs(
    {
        "user": st.secrets["snowflake_user"],
        "password": st.secrets["snowflake_password"],
        "account": st.secrets["snowflake_account"],
        "role": "accountadmin",
        "warehouse": st.secrets["snowflake_warehouse"],
        "database": st.secrets["snowflake_database"],
        "schema": "public",
    }
).create()

root = Root(session)


def init_service_metadata():
    """
    Initialize the session state for cortex search service metadata. Query the available
    cortex search services from the Snowflake session and store their names and search
    columns in the session state.
    """
    if "service_metadata" not in st.session_state:
        services = session.sql("SHOW CORTEX SEARCH SERVICES;").collect()
        service_metadata = []
        if services:
            for s in services:
                svc_name = s["name"]
                svc_search_col = session.sql(
                    f"DESC CORTEX SEARCH SERVICE {svc_name};"
                ).collect()[0]["search_column"]
                service_metadata.append(
                    {"name": svc_name, "search_column": svc_search_col}
                )
        st.session_state.service_metadata = service_metadata


init_service_metadata()

# FUNCTIONS ======================================================================================

def query_cortex_search_service(query, columns=[], filter={}):
    """
    Query the selected cortex search service with the given query and retrieve context documents.
    Display the retrieved context documents in the sidebar if debug mode is enabled. Return the
    context documents as a string.

    Args:
        query (str): The query to search the cortex search service with.

    Returns:
        str: The concatenated string of context documents.
    """
    db, schema = session.get_current_database(), session.get_current_schema()

    cortex_search_service = (
        root.databases[db]
        .schemas[schema]
        .cortex_search_services[st.session_state.selected_cortex_search_service]
    )

    context_documents = cortex_search_service.search(
        query, columns=columns, filter=filter
    )
    results = context_documents.results

    service_metadata = st.session_state.service_metadata
    search_col = [
        s["search_column"]
        for s in service_metadata
        if s["name"] == st.session_state.selected_cortex_search_service
    ][0].lower()
    context_str = ""
    for i, r in enumerate(results):
        context_str += f"Context document {i+1}: {r[search_col]} \n" + "\n"
    return context_str, results


def cortex_search(query, filter_pm_email):
    return query_cortex_search_service(
        query=query,
        columns=["chunk_text", "name", "userid"],
        filter={"@and": [{"@eq": {"pm_email": filter_pm_email}}]},
    )


def prompting_llm(list, prompt_user):
    promptCortex = f"""
[INST]
You are an AI Assistant for Project Managers, designed to streamline tech talent management through the application named Prosterio. You assist with tasks such as searching for candidates based on tech talent data uploaded by the user via the 'Add IT Talent' feature, viewing talent on the dashboard page, or analyzing employee profiles to address specific project-related questions.

You will also be provided context between <context> and </context> tags. Use that information to deliver a coherent, concise, and directly relevant response to the user's query.

When analyzing employee data:
- Identify the most relevant employee(s) who can assist with the user's query.
- Provide a narrative that explains the project, why the selected employee(s) are a good fit, and how they can contribute to solving the issue.

If the user's question cannot be answered with the given context or chat history, respond with "I don't know the answer to that question."

Guidelines:

1. **Relevance**: Avoid detailed responses to unrelated topics such as movies, personal questions, or casual chats. Politely redirect the user to ask questions within your domain expertise.

2. **Safety**: Ensure responses are safe, respectful, and neutral, avoiding harm or controversial topics.

3. **Clarity**: Provide clear, concise, and professional responses to maintain the credibility of the assistant.

Examples:

- If asked about movies: "I'm here to assist with project management and tech talent tasks. For movie-related queries, I recommend consulting a dedicated platform."

- If asked a potentially harmful or controversial question: "I'm sorry, but I cannot assist with that query."

<context>
{list}
</context>
<question>
{prompt_user}
</question>

[/INST]
Answer:
"""
    result = Complete(model="mistral-large2",prompt=promptCortex, session=session,).replace("$", "\$")
    return result
