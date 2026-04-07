import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import os
import datetime
import csv

st.title("🎓 Student Academic Assistant")

# --- OPENAI SETUP FOR VOICE ---
# IMPORTANT: Replace this with your actual OpenAI API key
client = OpenAI(api_key="YOUR_OPENAI_API_KEY") 

@st.cache_data
def load_kb():
    if os.path.exists("data/knowledge_base.csv"):
        return pd.read_csv("data/knowledge_base.csv")
    return None

kb_df = load_kb()

def get_bot_response(user_query, df):
    if df is None or df.empty:
        return "Knowledge base is empty.", 0.0, "Unknown"
    
    corpus = (df['canonical_question'] + " " + df['keywords'].fillna("")).tolist()
    vectorizer = TfidfVectorizer().fit(corpus)
    query_vec = vectorizer.transform([user_query])
    similarities = cosine_similarity(query_vec, vectorizer.transform(corpus))[0]
    
    best_index = similarities.argmax()
    best_score = similarities[best_index]
    
    if best_score < 0.2:
        return "I'm not completely sure. Could you rephrase?", round(best_score * 100, 1), "Unknown"
        
    return df.iloc[best_index]['response'], round(best_score * 100, 1), df.iloc[best_index]['category']

def log_interaction(query, response, category, confidence):
    with open("data/chat_logs.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), query, category, response, confidence, "Pending"])

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_query = None

# --- VOICE INPUT ---
st.write("🎤 **Record your question:**")
audio_bytes = audio_recorder(text="Click to talk", recording_color="#e8b125", neutral_color="#6aa36f")

if audio_bytes:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    st.success("Audio captured! Transcribing...")
    
    try:
        with open("temp_audio.wav", "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        user_query = transcript.text
        st.info(f"**You said:** {user_query}")
    except Exception as e:
        st.error("Voice transcription requires a valid OpenAI API key. Please check your setup.")

# --- TEXT INPUT ---
text_input = st.chat_input("...or type your question here")
if text_input:
    user_query = text_input

# --- PROCESS RESPONSE ---
if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    bot_response, confidence_score, category = get_bot_response(user_query, kb_df)
    log_interaction(user_query, bot_response, category, confidence_score)
    
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        st.caption(f"Category: {category} | Confidence: **{confidence_score}%**")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👍 Helpful", key=f"up_{len(st.session_state.messages)}"):
                st.success("Thanks for your feedback!")
        with col2:
            if st.button("👎 Not Helpful", key=f"down_{len(st.session_state.messages)}"):
                st.success("Thanks for your feedback!")
                
    st.session_state.messages.append({"role": "assistant", "content": bot_response})