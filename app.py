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
    """Generates a response from the Gemini model with optional context."""
    if context:
        question = f"{question}\n\nContext:\n{context}"
    response = model.generate_content(question)
    return response.text

def save_history(question, response):
    """Saves question and response in session state."""
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({"question": question, "response": response})

def read_pdf(file):
    """Reads and extracts text from a PDF file."""
    try:
        pdf_reader = fitz.open(stream=file.read(), filetype="pdf")
        text = ""
        for page_num in range(pdf_reader.page_count):
            page = pdf_reader.load_page(page_num)
            text += page.get_text("text")
        pdf_reader.close()
        return text
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
        return ""

# Streamlit app configuration
st.set_page_config(page_title="Q&A Demo with PDF Reader")
st.header("DREJ: The Chat Bot")

# Initialize state variables
if "history" not in st.session_state:
    st.session_state.history = []
if "first_question_asked" not in st.session_state:
    st.session_state.first_question_asked = False

# PDF uploader section
uploaded_pdf = st.file_uploader("Upload a PDF", type="pdf")
pdf_text = None
if uploaded_pdf:
    pdf_text = read_pdf(uploaded_pdf)

# Form to handle input submission with Enter key
with st.form(key='question_form'):
    input_text = st.text_input("Input your question: ", key="input", placeholder="Type your question here...")
    submit_button = st.form_submit_button("Ask the Question")

    if submit_button:
        if input_text.strip():  # Check if input is not empty or just spaces
            response = get_gemini_response(input_text, context=pdf_text)
            st.subheader("The response is")
            st.write(response)
            
            # Add the first question to history only if it is not the first question
            if st.session_state.first_question_asked:
                save_history(st.session_state.first_question, st.session_state.first_response)

            # Save the current question and response
            st.session_state.first_question_asked = True
            st.session_state.first_question = input_text
            st.session_state.first_response = response

        else:
            st.warning("The input cannot be empty. Please enter a question.")

# Sidebar with an image
with st.sidebar:
    st.image("/workspaces/basicllmchatbot/DREJLOGO.png", use_column_width=True)  # Replace with the path to your image
    st.subheader("History of Questions")
    if "history" in st.session_state and st.session_state.history:
        history = st.session_state.history
        for i, item in enumerate(reversed(history), 1):
            st.write(f"**Question {len(history) - i + 1}:** {item['question']}")
            st.write(f"**Response {len(history) - i + 1}:** {item['response']}")
    else:
        st.write("No history available.")
