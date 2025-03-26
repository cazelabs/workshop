import os
import streamlit as st

from dotenv import load_dotenv

from settings import settings
from dashboard import dashboard

# Load .env file
load_dotenv("./.env")


def main():
    print("Inside app -> main ()")
    st.sidebar.markdown(
                        """
                            <style>
                            /* Sidebar content styling */
                            [data-testid="stSidebarContent"] {
                                background-color: white;
                                secondary-background-colour: grey;
                            }
                            /* Adjust the sidebar width */
                            [data-testid="stSidebar"] {
                                width: 200px; /* Adjust this value to your desired width */
                            }    
                            .stRadio {
                                    background-color: black !important;
                                    padding: 15px;
                                    border-radius: 12px; /* Rounded corners */S
                                    margin-bottom: 10px;
                            }
                            
                            /* Change the text color of the radio button labels to black */
                            .stRadio label div[data-testid="stMarkdownContainer"] p {
                            color: white !important; /* Set text color to black */
                            font-weight: bold
                            }
                            .stRadio label div[data-testid="stMarkdownContainer"] p {
                            font-size: 18px !important;  /* Set the font size to 18px */
                            font-weight: bold
                            }
                            /* Ensure "Choose an operation mode" label is visible */
                            .st-ae p{
                                font-size: 20px; /* Adjust the label font size */
                                color: black; /* Set label text color to black */
                            }
                            .st-ae .st-am p {
                                color: black !important;  /* Set text color to black */
                                font-size: 18px !important;  /* Set font size for better visibility */
                                font-weight: bold
                            }

                            /* Highlight the radio buttons with hover effect */
                            .stRadio div div div label:hover {
                                background-color: #D8D8D8;  /* Change background color on hover */
                            }

                            /* Add a bottom margin to the radio button container for spacing */
                            .stRadio div {
                                margin-bottom: 10px;
                            }

                            
                            /* Styling for st.button elements */
                            [data-testid="stSidebar"] button {
                                background-color: black; 
                                color: white; 
                                padding: 10px; 
                                border-radius: 5px; 
                                font-weight: bold;
                                width: 100%; /* Full width */
                                display: block; /* Stack buttons vertically */
                                text-align:left; /* Align text to the left */
                                margin-bottom: 10px; /* Spacing between buttons */
                                border: none; /* Remove default borders */
                                outline: none; /* Remove focus outlines */
                            }

                            /* Button hover effect */
                            [data-testid="stSidebar"] button:hover {
                                background-color: grey; /* Change background color on hover */
                            }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )   

    st.sidebar.write("")
    st.sidebar.write("")
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "page" not in st.session_state:
        st.session_state.page="Dashboard"
    if st.sidebar.button("📊 Dashboard"):
        st.session_state.page = "Dashboard"

    if st.sidebar.button("⚙️ Settings"):
        st.session_state.page = "Settings"
    
    # for i in range(12):
    #     st.sidebar.write("")
    # st.sidebar.image( eval(os.getenv('CAZE_PATH')),use_container_width=True)
    # Now handle different pages and options
    if st.session_state.page == "Settings":
        settings()  # Call the upload function 
    if st.session_state.page == "Dashboard": 
        dashboard()
            
if __name__ == "__main__":
    main()

        

