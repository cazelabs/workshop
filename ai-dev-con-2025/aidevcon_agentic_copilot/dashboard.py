import os
from pathlib import Path
import base64
import streamlit as st

from llama_index.llms.azure_openai import AzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from llama_index.core import Settings
from langchain.schema import HumanMessage, AIMessage

from text_extraction import extract_text_and_save_as_markdown, load_documents
from text_extraction import extract_titles_from_med_pdfs, extract_titles_from_patient_pdfs
from agent_setup import setup_agents_and_query_engines, define_tools_for_agents, initialize_top_agent


def display_chat_history():
     for message in st.session_state.messages[1:]:
        if isinstance(message, AIMessage):
            st.chat_message("assistant").write(message.content)
        elif isinstance(message, HumanMessage):
            st.chat_message("user").write(message.content)
            
            
def handle_user_input(top_agent,all_tools):
    print("handle_user_input - start")
    # Check if the conversation has already ended
    if st.session_state.conversation_ended:
        st.write("Conversation has ended. Please refresh the page to start a new conversation.")
    else:
    # User input via chat
        user_input = st.chat_input("Enter clinical query...")
        if user_input:
             if user_input.strip().lower() in ["exit", "exitt"]:
                st.session_state.messages.append(HumanMessage(content=user_input))
                st.chat_message("user").write(user_input)
                st.write("Conversation has been ended by the user. Please refresh the page to start a new conversation.")
                st.session_state.conversation_ended = True
        # Append the user's message to session state
             else:
                st.session_state.messages.append(HumanMessage(content=user_input))
                st.chat_message("user").write(user_input)
                response = top_agent.chat(user_input)
                st.session_state.messages.append(AIMessage(content=response.response))
                st.chat_message("assistant").write(response.response)
                st.session_state.conversation_ended = False
                st.rerun()

def dashboard():
    llm = AzureOpenAI(
                        engine=os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
                        deployment_name=os.getenv("AZURE_OPENAI_API_DEPLOYMENT_NAME"),
                        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                        api_version=os.getenv("OPENAI_API_VERSION"),
                    )

    # You need to deploy your own embedding model as well as your own chat completion model
    embed_model = AzureOpenAIEmbedding(
                                            deployment_name="embedding",
                                            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                                            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                                            api_version=os.getenv("OPENAI_API_VERSION"),
                                    )

    Settings.llm = llm
    Settings.embed_model = embed_model

    st.write("👉 To end the conversation, type 'Exit'.")

    patient_folder = Path(eval(os.getenv('PATIENT_FOLDER')))
    med_doc_folder = Path(eval(os.getenv('MEDICAL_FOLDER')))
    data_path = Path(eval(os.getenv('DATA_PATH')))

    os.makedirs(patient_folder, exist_ok=True)
    os.makedirs(med_doc_folder, exist_ok=True)
    os.makedirs(data_path, exist_ok=True)



    # Extract document titles
    medical_document_titles = extract_titles_from_med_pdfs(med_doc_folder)
    patient_report_titles  = extract_titles_from_patient_pdfs(patient_folder)

    # Extract text and save as files
    extract_text_and_save_as_markdown( med_doc_folder, patient_folder, data_path, patient_report_titles, medical_document_titles)
    
    # Load documents
    med_doc_docs, patient_docs = load_documents(medical_document_titles, patient_report_titles, data_path)

    # Set up agents and query engines
    agents = setup_agents_and_query_engines( medical_document_titles, patient_report_titles, med_doc_docs, patient_docs, llm)
    
    all_tools = define_tools_for_agents(medical_document_titles, patient_report_titles, agents)
    top_agent = initialize_top_agent(all_tools)
    
    if "messages" not in st.session_state:
        st.session_state.messages = []  # List to store chat messages
    if "conversation_ended" not in st.session_state:
        st.session_state.conversation_ended = False
    display_chat_history()  # If you have a function for displaying previous messages

    # Handle user input and interaction
    handle_user_input(top_agent,all_tools)