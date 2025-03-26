import os
from docling.document_converter import DocumentConverter
from llama_index.core import SimpleDirectoryReader

def extract_titles_from_med_pdfs(pdf_folder: str) -> list[str]:
    print("extract_titles_from_med_pdfs  -  start ")
    medical_document_titles = []
    for file_name in os.listdir(pdf_folder):   
        file_path = os.path.join(pdf_folder, file_name)
        # Check if the file is a PDF
        if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
            title = file_name[:-4].replace(" ", "_")
            medical_document_titles.append(title)
    return medical_document_titles


def extract_titles_from_patient_pdfs(pdf_folder: str) -> list[str]:
    print("extract_titles_from_patient_pdfs  -  start ")
    patient_report_titles = []

    # Iterate through all files in the provided folder
    for file_name in os.listdir(pdf_folder):
        file_path = os.path.join(pdf_folder, file_name)
        # Check if the file is a PDF
        if os.path.isfile(file_path) and file_name.lower().endswith(".pdf"):
            # Extract the title (filename without '.pdf')
            title = file_name[:-4].replace(" ", "_")
            patient_report_titles.append(title) 
    return patient_report_titles

# Function to extract text from a PDF file using docling
def convert_pdf_to_markdown(pdf_path):
    # Initialize the DocumentConverter
    converter = DocumentConverter()
    try:
        result = converter.convert(pdf_path)
        return result.document.export_to_markdown()
    except Exception as e:
        print(f"Error converting {pdf_path} to markdown: {e}")
        return ""

def extract_medical_document_to_markdown(medical_document_titles, med_doc_folder, data_path):
    # Extract and save medical documents as markdown files
    for medical_document_title in medical_document_titles:
        # Convert title with underscores to match possible PDF filename with spaces
        search_title = medical_document_title.replace("_", " ")  # Convert anjali_sharma → anjali sharma
        # Look for the PDF file with spaces in the name
        matching_files = list(med_doc_folder.glob(f"{search_title}.pdf"))  # Exact match
        if matching_files:
            # Ensure saved filename maintains underscores
            sanitized_title = medical_document_title  # Keep anjali_sharma format
            output_file = data_path / f"{sanitized_title}_med_doc.md"
            if not os.path.exists(output_file):
                pdf_path = matching_files[0]  # Use the first matching file
                med_doc_markdown = convert_pdf_to_markdown(pdf_path)
                with open(output_file, "w", encoding="utf-8") as fp:
                    fp.write(med_doc_markdown)
                print(f"Saved {output_file}")  # Debugging
            else:
                print(f" Output file exist -> {output_file}")
        else:
            print(f"No matching file found for med doc title: {medical_document_title}")

def extract_patient_document_to_markdown(patient_report_titles, patient_doc_folder, data_path):
        # Extract and save patient documents as markdown files
    for title in patient_report_titles:
        # Convert title with underscores to match possible PDF filename with spaces
        search_title = title.replace("_", " ")  # Convert anjali_sharma → anjali sharma
        # Look for the PDF file with spaces in the name
        matching_files = list(patient_doc_folder.glob(f"{search_title}.pdf"))  # Exact match
        if matching_files:
            # Ensure saved filename maintains underscores
            sanitized_title = title  # Keep anjali_sharma format
            output_file = data_path / f"{sanitized_title}_patient.md"
            if not os.path.exists(output_file):
                pdf_path = matching_files[0]  # Use the first matching file
                patient_markdown = convert_pdf_to_markdown(pdf_path)

                with open(output_file, "w", encoding="utf-8") as fp:
                    fp.write(patient_markdown)
                print(f"Saved {output_file}")  # Debugging
            else:
                print(f" Output file exist -> {output_file}")
        else:
            print(f"No matching file found for patient title: {title}")


def extract_text_and_save_as_markdown(med_doc_folder, patient_doc_folder, data_path, patient_report_titles, medical_document_titles):
    print("extract_text_and_save_as_markdown  -  start ")
    # Ensure the data directory exists
    os.makedirs(data_path, exist_ok=True)
    extract_medical_document_to_markdown(medical_document_titles, med_doc_folder, data_path)
    extract_patient_document_to_markdown(patient_report_titles, patient_doc_folder, data_path)

"""
    Load medical and patient documents into dictionaries.

    Args:
        document_titles (list): List of medical document titles.
        patient_titles (list): List of patient document titles.
        data_path (Path): Path to the directory where text files are stored.

    Returns:
        tuple: A tuple containing two dictionaries:
            - med_doc_docs: Dictionary with medical document titles as keys and loaded data as values.
            - patient_docs: Dictionary with patient document titles as keys and loaded data as values.
"""
def load_documents(document_titles, patient_titles, data_path):
    print("load_documents -  start ")
    PERSIST_DIRECTORY = os.path.join(os.getcwd(), "data")
    os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
    med_doc_docs = {}
    patient_docs = {}
    # Load medical documents
    for document_title in document_titles:
        med_doc_docs[document_title] = SimpleDirectoryReader(input_files=[data_path / f"{document_title}_med_doc.md"]).load_data()
    # Load patient documents
    for patient_title in patient_titles:
        patient_docs[patient_title] = SimpleDirectoryReader(input_files=[data_path / f"{patient_title}_patient.md"]).load_data()
    return med_doc_docs, patient_docs
