import os
import streamlit as st

def save_file(uploaded_file, directory="data"):
    print("save_file - start")
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_path = os.path.join(directory, uploaded_file.name)
    try:
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        return True, file_path
    except Exception as e:
        return False,str(e)
    
def upload_medical_files():
    st.subheader("Upload Medical documents")
    medical_files = st.file_uploader(
                                        "Upload medical documents",
                                        type=["pdf"],
                                        accept_multiple_files=True,
                                        key="medical_upload"
                                    )
    if st.button("Upload Medical Documents", key="medical_upload_button"):
        for file in medical_files:
            success, result = save_file(file,eval(os.getenv('MEDICAL_FOLDER')))
            if success:
                st.success(f"Successfully saved {file.name} to medical documents directory")
            else:
                st.error(f"Failed to save {file.name}: {result}")

def upload_patient_report_files():
    # File uploader for patient documents
    st.subheader("Upload Patient Documents")
    patient_files = st.file_uploader(
                                        "Upload patient documents",
                                        type=["pdf"],
                                        accept_multiple_files=True,
                                        key="patient_upload"
                                    )
    if st.button("Upload Patient Documents", key="patient_upload_button"):
        for file in patient_files:
            success, result = save_file(file,eval(os.getenv('PATIENT_FOLDER') ))
            if success:
                st.success(f"Successfully saved {file.name} to patient documents directory")
            else:
                st.error(f"Failed to save {file.name}: {result}")

def settings():
    # File uploader for medical documents
    print("upload - start")
    upload_medical_files()
    upload_patient_report_files()
    

    