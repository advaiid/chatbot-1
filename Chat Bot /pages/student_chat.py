import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from audio_recorder_streamlit import audio_recorder
import speech_recognition as sr
import os
import datetime
import csv

st.title("🎓 Student Academic Assistant")

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

# --- VOICE INPUT (FREE GOOGLE API) ---
st.write("🎤 **Record your question:**")

# Optional: Let the user choose the language they are speaking!
spoken_language = st.radio("Select spoken language:", ("English", "Malayalam"), horizontal=True)
lang_code = "en-IN" if spoken_language == "English" else "ml-IN"

audio_bytes = audio_recorder(text="Click to talk", recording_color="#e8b125", neutral_color="#6aa36f")

if audio_bytes:
    with open("temp_audio.wav", "wb") as f:
        f.write(audio_bytes)
    st.success("Audio captured! Transcribing...")
    
    try:
        # Initialize the recognizer
        recognizer = sr.Recognizer()
        with sr.AudioFile("temp_audio.wav") as source:
            audio_data = recognizer.record(source)
            
            # Use Google's free recognition endpoint
            transcript = recognizer.recognize_google(audio_data, language=lang_code)
            
        user_query = transcript
        st.info(f"**You said:** {user_query}")
    
    except sr.UnknownValueError:
        st.error("Sorry, I could not understand the audio. Please try again or type your question.")
    except sr.RequestError as e:
        st.error(f"Could not request results from Google Speech Recognition service; {e}")

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