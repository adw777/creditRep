import streamlit as st
import requests
import os
from typing import List

# FastAPI endpoint URLs
API_BASE_URL = "http://localhost:8000"
PARSE_URL = f"{API_BASE_URL}/parse"
CHAT_URL = f"{API_BASE_URL}/chat"

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'processed_file_path' not in st.session_state:
        st.session_state.processed_file_path = None
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def process_document(uploaded_file):
    """Send document to FastAPI endpoint for processing"""
    if uploaded_file is not None:
        files = {"file": uploaded_file}
        try:
            response = requests.post(PARSE_URL, files=files)
            response.raise_for_status()
            result = response.json()
            
            # Extract the file path from the result
            # Assuming the result contains the markdown file path
            file_path = result["result"].split("Results saved to: ")[-1].split("\n")[0]
            return file_path
        except Exception as e:
            st.error(f"Error processing document: {str(e)}")
            return None

def send_chat_message(query: str, document_path: str) -> str:
    """Send chat message to FastAPI endpoint"""
    try:
        response = requests.post(
            CHAT_URL,
            json={"query": query, "document_path": document_path}
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        st.error(f"Error sending message: {str(e)}")
        return None

def main():
    st.title("Document Chat Interface")
    
    # Initialize session state
    initialize_session_state()
    
    # Document upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])
    
    if uploaded_file and st.button("Process Document"):
        with st.spinner("Processing document..."):
            file_path = process_document(uploaded_file)
            if file_path:
                st.session_state.processed_file_path = file_path
                st.success("Document processed successfully!")
    
    # Chat interface
    if st.session_state.processed_file_path:
        st.subheader("Chat")
        
        # Display chat history
        for message in st.session_state.chat_history:
            role = message["role"]
            content = message["content"]
            
            if role == "user":
                st.write(f"You: {content}")
            else:
                st.write(f"Assistant: {content}")
        
        # Chat input
        user_input = st.text_input("Type your message:")
        if st.button("Send") and user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            
            # Get response from API
            with st.spinner("Getting response..."):
                response = send_chat_message(user_input, st.session_state.processed_file_path)
                
                if response:
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    
                    # Rerun to update chat display
                    st.experimental_rerun()

if __name__ == "__main__":
    main()