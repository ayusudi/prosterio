import streamlit as st
from typing import Generator
from groq import Groq
from functions.header import header
from functions.chat_prompt import chatPromptRAG

header("👥", "PM Assistant")


client = Groq(
    api_key=st.secrets["groq_apikey"],
)

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = (
    {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
)

# Layout for model selection and max_tokens slider
col1, col2 = st.columns((3, 2))

with col1:
    col1.info(
        f"Trigger our Posterio RAG as a PM Assistant by starting a chat with **/RAG** then continue with your prompt.\n\n**/RAG** I'm planning an inventory management system. What key skills should my developer have?"
    )


if st.session_state.messages is None:
    st.session_state.messages = []

# Detect model change and clear chat history if model has changed
model_option = "mixtral-8x7b-32768"
max_tokens_range = models[0]["tokens"]

with col2:
    # Adjust max_tokens slider dynamically based on the selected model
    max_tokens = st.slider(
        "Max Tokens:",
        min_value=512,  # Minimum value to allow some flexibility
        max_value=max_tokens_range,
        # Default value or max allowed if less
        value=min(32768, max_tokens_range),
        step=512,
        help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}",
    )

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


text_system = f"""
You are an AI Assistant for Project Managers, designed to streamline tech talent management through the application named Prosterio. You assist with tasks such as searching for candidates based on tech talent data uploaded by the user via the 'Add IT Talent' feature or viewing talent on the dashboard page.

Purpose: Respond professionally and focus strictly on topics relevant to project management and tech talent.

Guidelines:

Relevance: Avoid providing detailed responses to unrelated topics, such as movies, personal questions, or casual chats. Politely redirect the user to ask questions within your domain expertise.

Safety: Ensure responses are safe, respectful, and neutral, avoiding harm or controversial topics.

Clarity: Provide clear, concise, and professional responses to maintain the credibility of the assistant.

Examples:

If asked about movies: "I'm here to assist with project management and tech talent tasks. For movie-related queries, I recommend consulting a dedicated platform."

If asked a potentially harmful or controversial question: "I'm sorry, but I cannot assist with that query."

This ensures that the assistant remains focused, safe, and aligned with its purpose."""

def chatBot(max_tokens):
    try:
        initialize = [{"role": "system", "content": text_system}]
        messages = initialize + st.session_state.messages
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)

        print(st.session_state.messages, "<<<<!")
    except Exception as e:
        st.error(e, icon="🚨")

    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
    else:
        # Handle the case where full_response is not a string
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role": "assistant", "content": combined_response}
        )


prompt = st.chat_input("Chat with PM Assistant")

if type(prompt) == str and prompt.lower().startswith("/rag"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(prompt)
    # Fetch response from Groq API
    try:
        text = prompt.split("/rag")[0]
        response = chatPromptRAG(text, st.session_state.user_info["email"])
        st.session_state.messages.append(
            {"role": "assistant", "content": response[0][0]}
        )
        with st.chat_message("assistant", avatar="🤖"):
            st.markdown(response[0][0])
    except Exception as e:
        st.error(e, icon="🚨")
elif type(prompt) == str and len(prompt) > 0:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👨‍💻"):
        st.markdown(prompt)
    chatBot(max_tokens=max_tokens)
