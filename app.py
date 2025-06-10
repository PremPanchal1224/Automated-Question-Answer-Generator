import streamlit as st
from PyPDF2 import PdfReader
from transformers import BartTokenizer, BartForConditionalGeneration, T5Tokenizer, T5ForConditionalGeneration, pipeline
import sqlite3
import hashlib

# Database setup
conn = sqlite3.connect("users.db")
c = conn.cursor()
c.execute('''
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
''')
conn.commit()

# Password hashing function
def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

# Password check function
def check_password(stored_password, input_password):
    return stored_password == hash_password(input_password)

# Signup function
def signup():
    st.title("Signup")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    
    if st.button("Signup"):
        if password != confirm_password:
            st.error("Passwords do not match.")
        else:
            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchone():
                st.error("Username already exists.")
            else:
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
                conn.commit()
                st.success("Signup successful. Please log in.")

# Login function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        c.execute("SELECT password FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result and check_password(result[0], password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success("Login successful!")
        else:
            st.error("Invalid username or password")

# Optimized model loading with caching
@st.cache_resource
def load_summary_model():
    summary_tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn")
    summary_model = BartForConditionalGeneration.from_pretrained("facebook/bart-large-cnn")
    return summary_tokenizer, summary_model

@st.cache_resource
def load_question_model():
    question_tokenizer = T5Tokenizer.from_pretrained("valhalla/t5-small-qg-hl")
    question_model = T5ForConditionalGeneration.from_pretrained("valhalla/t5-small-qg-hl")
    return question_tokenizer, question_model

# Load a pipeline for question answering
@st.cache_resource
def load_qa_pipeline():
    qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")
    return qa_pipeline

# PDF text extraction
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text.strip()

# Generate summary
def generate_summary(text):
    max_length = 1024
    if len(text) > max_length:
        text = text[:max_length]  # Trim text to reduce processing time

    summary_tokenizer, summary_model = load_summary_model()
    inputs = summary_tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True)
    summary_ids = summary_model.generate(inputs["input_ids"], max_length=250, min_length=150, length_penalty=2.0, num_beams=4, early_stopping=True)
    summary = summary_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary

# Generate questions
def generate_questions(text, answer_type="sentence"):
    sentences = text.split('. ')
    questions = set()

    question_tokenizer, question_model = load_question_model()

    for sentence in sentences:
        if len(sentence) > 30:  # Ensure the sentence is long enough for meaningful questions
            input_text = f"generate a question that can be answered with one word: {sentence}" if answer_type == "word" else f"generate a question: {sentence}"
            input_ids = question_tokenizer.encode(input_text, return_tensors="pt")
            output = question_model.generate(input_ids, max_length=50, num_return_sequences=4, num_beams=4, early_stopping=True)
            for output_id in output:
                question = question_tokenizer.decode(output_id, skip_special_tokens=True)
                questions.add(question)

    return list(questions)[:5]

# Generate answers
def generate_answers(questions, context):
    qa_pipeline = load_qa_pipeline()
    answers = []
    for question in questions:
        result = qa_pipeline(question=question, context=context)
        answers.append(result['answer'])
    return answers

# Main app logic
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    page = st.sidebar.selectbox("Select Page", ["Login", "Signup"])
    
    if page == "Login":
        login()
    elif page == "Signup":
        signup()
else:
    st.sidebar.write(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.success("Logged out successfully.")

    st.title("PDF Processing, Question Generator, and Answer Generator")
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

    if uploaded_file is not None:
        st.write("Processing the PDF...")
        extracted_text = extract_text_from_pdf(uploaded_file)
        st.subheader("Extracted Text")
        st.text_area("Full Text", extracted_text, height=300)

        summary = generate_summary(extracted_text)
        st.subheader("Generated Summary")
        st.write(summary)

        if st.button("Generate and Answer Questions (One-word Answers)"):
            questions_word = generate_questions(extracted_text, answer_type="word")
            st.subheader("Generated Questions and Answers (One-word)")
            answers_word = generate_answers(questions_word, extracted_text)
            for question, answer in zip(questions_word, answers_word):
                st.write(f"Q: {question}")
                st.write(f"A: {answer}")
        
        if st.button("Generate and Answer Questions (Sentence Answers)"):
            questions_sentence = generate_questions(extracted_text, answer_type="sentence")
            st.subheader("Generated Questions and Answers (Sentence)")
            answers_sentence = generate_answers(questions_sentence, extracted_text)
            for question, answer in zip(questions_sentence, answers_sentence):
                st.write(f"Q: {question}")
                st.write(f"A: {answer}")

# Close the database connection when the app is closed
conn.close()
