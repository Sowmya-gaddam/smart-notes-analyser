import streamlit as st
import re
from collections import Counter
import pdfplumber

# Summarization
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Topic extraction
from rake_nltk import Rake
import nltk

# ---------- SAFE NLTK DOWNLOAD ----------
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# ---------- PAGE CONFIG ----------
st.set_page_config(page_title="Smart Notes Analyser")

st.title("📘 Smart Notes Analyser")
st.write("Upload your notes and analyze them easily.")

# ---------- FILE UPLOAD ----------
uploaded_file = st.file_uploader("Upload file", type=["txt", "pdf"])

# ---------- FUNCTIONS ----------

# Summarization
def generate_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary_sentences = summarizer(parser.document, 3)
    return " ".join(str(sentence) for sentence in summary_sentences)

# Q&A
def answer_question(text, question):
    sentences = re.split(r'(?<=[.!?]) +', text)
    question_words = question.lower().split()

    scores = []
    for sentence in sentences:
        sentence_words = sentence.lower().split()
        common = Counter(question_words) & Counter(sentence_words)
        score = sum(common.values())
        scores.append((score, sentence))

    if scores:
        best_sentence = max(scores, key=lambda x: x[0])[1]
        return best_sentence
    else:
        return "No relevant answer found."

# Topic extraction
def extract_topics(text):
    rake = Rake()
    rake.extract_keywords_from_text(text)
    return rake.get_ranked_phrases()[:5]

# ---------- MAIN ----------

if uploaded_file:
    content = ""

    # ---------- PDF HANDLING ----------
    if uploaded_file.type == "application/pdf":
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        content += text + "\n"
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")

    # ---------- TXT HANDLING ----------
    else:
        try:
            content = uploaded_file.read().decode("utf-8")
        except:
            content = uploaded_file.read().decode("latin-1")

    # ---------- CHECK CONTENT ----------
    if not content.strip():
        st.warning("⚠ Could not extract readable text. Try another file.")
    else:
        st.subheader("📄 Your Notes")
        st.write(content)

        # ---------- SUMMARY ----------
        st.subheader("🧠 Summary")
        if st.button("Generate Summary"):
            with st.spinner("Processing..."):
                summary = generate_summary(content)
            st.success(summary)

        # ---------- Q&A ----------
        st.subheader("❓ Ask Questions from Notes")
        question = st.text_input("Enter your question")

        if question:
            answer = answer_question(content, question)
            st.subheader("💡 Answer")
            st.success(answer)

        # ---------- TOPICS ----------
        st.subheader("🏷️ Important Topics")
        if st.button("Extract Topics"):
            topics = extract_topics(content)
            for topic in topics:
                st.write("•", topic)

else:
    st.info("Please upload a TXT or text-based PDF file to begin.")
