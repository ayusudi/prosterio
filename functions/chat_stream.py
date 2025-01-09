import streamlit as st
from typing import Generator
from groq import Groq

# "model-name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"
client = Groq(
    api_key=st.secrets["groq_apikey"],
)

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

This ensures that the assistant remains focused, safe, and aligned with its purpose.
"""


def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    """Yield chat response content from the Groq API response."""
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def chat_stream(max_tokens):
    try:
        initialize = [{"role": "system", "content": text_system}]
        messages = initialize + st.session_state.messages
        chat_completion = client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        # Use the generator function with st.write_stream
        with st.chat_message("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)

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
