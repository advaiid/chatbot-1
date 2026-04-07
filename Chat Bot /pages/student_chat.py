import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from audio_recorder_streamlit import audio_recorder
import os

st.title("🎓 Student Academic Assistant")
st.write("Ask me in English or Malayalam using text or voice!")

# --- 1. LOAD THE KNOWLEDGE BASE ---
@st.cache_data
def load_kb():
    file_path = "data/knowledge_base.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error("Knowledge base not found! Please check the data folder.")
        return None

kb_df = load_kb()

# --- 2. NLP LOGIC ---
def get_bot_response(user_query, df):
    if df is None or df.empty:
        return "Sorry, my knowledge base is currently empty.", 0.0, "Unknown"
    
    # Combine question and keywords for better matching
    corpus = (df['canonical_question'] + " " + df['keywords'].fillna("")).tolist()
    
    # Convert text to vectors
    vectorizer = TfidfVectorizer().fit(corpus)
    query_vec = vectorizer.transform([user_query])
    corpus_vecs = vectorizer.transform(corpus)
    
    # Calculate similarity
    similarities = cosine_similarity(query_vec, corpus_vecs)[0]
    best_index = similarities.argmax()
    best_score = similarities[best_index]
    
    # Fallback for low confidence
    if best_score < 0.2:
        return "I'm not completely sure about that. Could you try rephrasing or asking something else?", round(best_score * 100, 1), "Unknown"
        
    best_response = df.iloc[best_index]['response']
    detected_category = df.iloc[best_index]['category']
    return best_response, round(best_score * 100, 1), detected_category

# --- 3. INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. INPUT HANDLING (Voice or Text) ---
user_query = None

st.write("🎤 **Record your question:**")
audio_bytes = audio_recorder(text="Click to talk", recording_color="#e8b125", neutral_color="#6aa36f")

if audio_bytes:
    st.audio(audio_bytes, format="audio/wav")
    # Placeholder: Replace this with OpenAI Whisper logic later
    st.info("Audio received! (Plug in Whisper API here to convert to text)")
    # Example: user_query = transcribe_audio(audio_bytes) 

# Check text input box
text_input = st.chat_input("...or type your question here")
if text_input:
    user_query = text_input

# --- 5. PROCESS AND DISPLAY RESPONSE ---
if user_query:
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    bot_response, confidence_score, category = get_bot_response(user_query, kb_df)
    
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        st.caption(f"Category: {category} | Confidence Score: **{confidence_score}%**")
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("👍 Helpful", key=f"up_{len(st.session_state.messages)}")
        with col2:
            st.button("👎 Not Helpful", key=f"down_{len(st.session_state.messages)}")

    st.session_state.messages.append({"role": "assistant", "content": bot_response})