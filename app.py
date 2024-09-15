from dotenv import load_dotenv
load_dotenv()  # Load all environment variables

import streamlit as st
import os
import google.generativeai as genai
import fitz  # PyMuPDF

# Configure the Generative AI API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to load and generate responses
model = genai.GenerativeModel("gemini-pro")

def get_gemini_response(question, context=None):
    """Generates response from the Gemini model with optional context (e.g., from PDF)."""
    if context:
        # Add context to the question if it's provided (from the PDF text)
        question = f"{question}\n\nContext:\n{context}"
    
    response = model.generate_content(question)
    return response.text

def save_history(question, response):
    """Saves question and response in session state."""
    if "history" not in st.session_state:
        st.session_state.history = []
    # Insert the new question-response pair at the start of the history list (for reverse order)
    st.session_state.history.insert(0, {"question": question, "response": response})

def read_pdf(file):
    """Reads and extracts text from a PDF file."""
    pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page_num in range(pdf_reader.page_count):
        page = pdf_reader.load_page(page_num)
        text += page.get_text("text")
    pdf_reader.close()
    return text

# Streamlit app configuration
st.set_page_config(page_title="Q&A Demo with PDF Reader")
st.header("LLM Application")

# PDF uploader section
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")
pdf_text = None
if uploaded_pdf:
    pdf_text = read_pdf(uploaded_pdf)
    st.subheader("Extracted Text from PDF")
    st.write(pdf_text[:500])  # Display first 500 characters of the PDF text

# Input field and button
input = st.text_input("Input your question: ", key="input")
submit = st.button("Ask the Question")

# Ensure input is not empty before generating response
if submit:
    if input.strip():  # Check if input is not empty or just spaces
        response = get_gemini_response(input, context=pdf_text)
        save_history(input, response)
        st.subheader("The response is")
        st.write(response)
    else:
        st.warning("The input cannot be empty. Please enter a question.")

# Display the history of previous questions and responses
if "history" in st.session_state:
    st.subheader("History of Questions")
    for i, item in enumerate(st.session_state.history, 1):
        st.write(f"**Question {i}:** {item['question']}")
        st.write(f"**Response {i}:** {item['response']}")
