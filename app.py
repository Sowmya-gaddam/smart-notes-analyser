import streamlit as st
from textblob import TextBlob
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# OCR
import pytesseract
from pdf2image import convert_from_bytes

# Summarization
from sumy.summarizers.lsa import LsaSummarizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer

# ---------------- SETTINGS ----------------

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\sowmy\Downloads\Release-25.12.0-0\Library\bin"

# NLTK downloads
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

# ---------------- UI ----------------

st.title("🧠 Smart Notes Analyzer")

text = st.text_area("✍️ Enter your notes:")

# ---------------- PDF ----------------

uploaded_file = st.file_uploader("📄 Upload PDF", type="pdf")

if uploaded_file is not None:
    try:
        images = convert_from_bytes(
            uploaded_file.read(),
            poppler_path=POPPLER_PATH
        )

        text = ""

        for img in images:
            text += pytesseract.image_to_string(img)

        st.success("✅ PDF text extracted successfully!")
        st.write("Preview:", text[:500])

    except Exception as e:
        st.error("❌ PDF Error: " + str(e))

# ---------------- FUNCTIONS ----------------

# Summary
def advanced_summary(text):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 2)

    result = ""
    for sentence in summary:
        result += str(sentence) + " "

    return result

# IMPORTANT TOPICS
def extract_topics(text):
    words = word_tokenize(text)
    stop_words = set(stopwords.words("english"))

    topics = []
    current_topic = []

    for word in words:
        if word.lower() not in stop_words and word.isalpha():
            current_topic.append(word)
        else:
            if len(current_topic) > 1:
                topics.append(" ".join(current_topic))
            current_topic = []

    return list(set(topics))[:5]

# ---------------- ANALYZE ----------------

if st.button("🔍 Analyze"):
    if text.strip() != "":

        # Summary
        st.subheader("📌 Summary")
        st.write(advanced_summary(text))

        # Sentiment
        st.subheader("😊 Sentiment")
        polarity = TextBlob(text).sentiment.polarity

        if polarity > 0:
            st.success("Positive")
        elif polarity < 0:
            st.error("Negative")
        else:
            st.info("Neutral")

        # Important Topics
        st.subheader("📌 Important Topics")
        topics = extract_topics(text)
        st.write(topics)

    else:
        st.warning("⚠️ Please enter or upload some text")