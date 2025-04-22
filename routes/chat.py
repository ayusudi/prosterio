import json
import streamlit as st
from functions.header import header
from functions.chat_stream import chat_stream
from functions.vector_search_chat_prompt import chatPromptRAG

def main(cookies):
    header("👥", "PM Assistant")
    col1, col2 = st.columns((3, 2))
    col1.info(f"Trigger our Posterio RAG as a PM Assistant by starting a chat with **/RAG** then continue with your prompt.\n\n**/RAG** I'm planning to build an inventory management system. Who would you recommend from our IT talent to develop this app?")
    with col2:
        max_tokens = col2.slider(
            "Max Tokens:",
            min_value=512,
            max_value=8192,
            value=8192,
            step=512,
            help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: 8.192",
        )

    # Load messages once
    messages = json.loads(cookies['messages'])
    
    # Batch render messages
    for message in messages:
        avatar = "🤖" if message["role"] == "assistant" else "👨‍💻"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    
    prompt = st.chat_input("Chat with PM Assistant")
    if prompt:
        # Update messages immediately
        messages.append({"role": "user", "content": prompt})
        cookies['messages'] = json.dumps(messages)
        
        with st.chat_message("user", avatar="👨‍💻"):
            st.markdown(prompt)
            
        if prompt.lower().startswith("/rag"):
            try:
                user_question = prompt[5:]
                pm_email = cookies['email']
                response = ''
                with st.spinner("Thinking..."):
                    response = chatPromptRAG(user_question, pm_email)
                
                if response != '':
                    messages.append({"role": "assistant", "content": response})
                    cookies['messages'] = json.dumps(messages)
                    with st.chat_message("assistant", avatar="🤖"):
                        st.markdown(response)
            except Exception as e:
                st.error(str(e), icon="🚨")
        else:
            chat_stream(max_tokens, cookies)
        
        # Save cookies only once at the end
        cookies.save()
    else:
        st.stop()