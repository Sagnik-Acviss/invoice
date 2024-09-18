
import os
import time
import fitz  # PyMuPDF
import streamlit as st
import pdfplumber
import pandas as pd


def get_words(pdf_path):
    doc = fitz.open(pdf_path)

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)  # Get the page
        words_pdf = page.get_text("words")  # Extract words with bounding boxes
        return words_pdf

def get_invoice_number(words):
    for index in range(len(words) - 1):
        if words[index][4] == "Invoice" and words[index + 1][4] == "No:" or words[index + 1][4] == "Invoice" and  words[index][4] == "No:":
            if len(words[index + 2][4]) == 12:
                return words[index + 2][4]
            elif len(words[index - 1][4]) == 12:
                return words[index - 1][4]

def get_supplying_location(words):
    for index in range(len(words) - 1):
        if words[index][4] == "Supplying" and words[index + 1][4] == "Location":
            # if words[index+2][5]
            return words[index + 2][4] +" " +  words[index + 3][4]+" " +  words[index + 4][4]+" " +  words[index + 5][4]

def get_buyer_location(words):
    block_no = 0
    for index in range(len(words) - 1):

        if words[index][4] == "Buyer:":
            block_no = words[index][5]

    location = []
    for index in range(len(words) - 1):
        if words[index][5] == block_no+1:
            if words[index][6] == 0:
                location.append(words[index][4])
    return ' '.join(location)
def get_table(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        # List to hold rows of the table
        table_data = []
        for page in pdf.pages:
            text = page.extract_text()
            if "BATCH DETAILS" in text:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        table_data.append(row)

    columns = []

    for data_index in range(len(table_data)):

        if table_data[data_index][0] == "Inv\nS.No.":
            index_list = table_data[data_index]

            cleaned_index_list = [item for item in index_list if item is not None]

            data = []
            counter = 1
            try:
                while True:
                    data_list = table_data[data_index + counter]
                    cleaned_data_list = [item for item in data_list if item is not None]
                    if len(cleaned_index_list) == len(cleaned_data_list):
                        data.append(cleaned_data_list)

                    counter = counter + 1
            except:
                pass

            df = pd.DataFrame(data, columns=cleaned_index_list)
    return df


# Streamlit UI
st.title("PDF Invoice Processor")

# File uploader
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:

    start = time.time()

    for uploaded_file in uploaded_files:
        try:
            # Save the uploaded file to a temporary directory
            temp_file_path = os.path.join("temp", "data.pdf")
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.read())

            # Process each PDF using the file path
            with st.spinner(f"Processing {uploaded_file.name}..."):
                words = get_words(temp_file_path)
                number = get_invoice_number(words)
                supply_location = get_supplying_location(words)
                buyer_location = get_buyer_location(words)
                df = get_table(pdf_path="temp/data.pdf")


                # Display results in the Streamlit app
                st.write(f"**File Path:** {uploaded_file.name}")
                st.write(f"**Invoice Number:** {number}")
                st.write(f"**Supplying Location:** {supply_location}")
                st.write(f"**Buyer Location:** {buyer_location}")
                st.dataframe(df)
                st.write("-" * 80)

        except Exception as e:
            st.error(f"Error processing {uploaded_file.name}: {e}")

    end = time.time()


    st.write(f"Total time taken: {end - start:.2f} seconds")
