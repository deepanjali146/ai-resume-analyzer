import os
import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import pdfplumber

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Extract text
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text

        if not text.strip():
            return None

        return text.strip()

    except Exception as e:
        print(f"Error extracting text: {e}")
        return None

# Analyze resume
def analyze_resume(resume_text, job_description=None):
    if not resume_text:
        return "❌ Resume text is empty."

    model = genai.GenerativeModel("models/gemini-2.5-flash")

    prompt = f"""
    You are an HR expert. Analyze this resume.
    Give strengths, weaknesses, skills, and improvement suggestions.

    Resume:
    {resume_text}
    """

    if job_description:
        prompt += f"""
        Also compare with this job description:

        {job_description}
        """

    response = model.generate_content(prompt)
    return response.text.strip()

# UI
st.set_page_config(page_title="Resume Analyzer", layout="wide")

st.title("AI Resume Analyzer")
st.write("Upload resume and analyze using Gemini AI")

col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

with col2:
    job_description = st.text_area("Job Description")

if uploaded_file:
    st.success("Resume uploaded")

    with open("uploaded_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    resume_text = extract_text_from_pdf("uploaded_resume.pdf")

    if st.button("Analyze Resume"):
        with st.spinner("Analyzing..."):
            if not resume_text:
                st.error("⚠️ No readable text found in PDF")
            else:
                result = analyze_resume(resume_text, job_description)
                st.success("Done")
                st.write(result)

else:
    st.warning("Upload a resume")