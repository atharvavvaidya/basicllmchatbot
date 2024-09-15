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
    """Saves question and response in session state, except for the current query."""
    if "history" not in st.session_state:
        st.session_state.history = []
    # Append the question-response pair to the history, but not the current query
    if question and response:
        st.session_state.history.append({"question": question, "response": response})

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
st.header("DREJ: The Chat Bot")

# PDF uploader section
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")
pdf_text = None
if uploaded_pdf:
    pdf_text = read_pdf(uploaded_pdf)  

# Form to handle input submission with Enter key
with st.form(key='question_form'):
    input_text = st.text_input("Input your question: ", key="input")
    submit_button = st.form_submit_button("Ask the Question")

    if submit_button and input_text.strip():  # Check if input is not empty or just spaces
        response = get_gemini_response(input_text, context=pdf_text)
        st.subheader("The response is")
        st.write(response)
        # Save the question-response pair to history after showing the response
        save_history(input_text, response)
    elif submit_button:
        st.warning("The input cannot be empty. Please enter a question.")

# Display the history of previous questions and responses
if "history" in st.session_state:
    st.subheader("History of Questions")
    # Display history in reverse order while keeping the original numbering
    history = st.session_state.history
    for i, item in enumerate(reversed(history), 1):
        st.write(f"**Question {len(history) - i + 1}:** {item['question']}")
        st.write(f"**Response {len(history) - i + 1}:** {item['response']}")
