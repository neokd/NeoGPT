from io import BytesIO

import pandas as pd
import streamlit as st
from pdfminer.high_level import extract_text

# Initialize the app
st.title("File Uploader")

# Create a file uploader
with st.form("Upload File"):
    file_upload = st.file_uploader("Select a file to upload:")

    # Check if a file is uploaded
    if file_upload is not None:
        # Display the file information
        st.subheader("File Information")
        filename = file_upload.name
        size = file_upload.size
        st.write(f"Filename: {filename}")
        st.write(f"Size: {size} bytes")

        # Read the file content as bytes
        content = file_upload.read()

        # Check file extension
        file_extension = filename.split(".")[-1].lower()

        # Display the file content based on file extension
        st.subheader("File Content")

        if file_extension == "pdf":
            # Extract text from PDF using pdfminer.six
            pdf_text = extract_text(BytesIO(content))
            st.text_area("Content:", pdf_text, height=300)
        elif file_extension in ["xls", "xlsx"]:
            # Read Excel file using pandas
            excel_df = pd.read_excel(BytesIO(content))
            st.write("Preview of Excel Data:")
            st.write(excel_df)
        else:
            # For other file types, display raw content
            st.text_area("Content:", content.decode("utf-8"), height=300)

    st.form_submit_button("Upload")
