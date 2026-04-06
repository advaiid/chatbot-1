import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os

st.title("🎓 Student Academic Assistant")
st.write("Ask me in English or Malayalam!")

# --- 1. LOAD THE KNOWLEDGE BASE ---
@st.cache_data # This prevents reloading the CSV every time you type a letter
def load_kb():
    file_path = "data/knowledge_base.csv"
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        st.error("Knowledge base not found! Please check the data folder.")
        return None

kb_df = load_kb()

# --- 2. NLP LOGIC (The "Brain") ---
def get_bot_response(user_query, df):
    if df is None or df.empty:
        return "Sorry, my knowledge base is currently empty or broken.", 0.0
    
    # We combine the canonical questions and keywords for better matching
    corpus = (df['canonical_question'] + " " + df['keywords'].fillna("")).tolist()
    
    # Convert text to vectors using TF-IDF
    vectorizer = TfidfVectorizer().fit(corpus)
    query_vec = vectorizer.transform([user_query])
    corpus_vecs = vectorizer.transform(corpus)
    
    # Calculate how similar the user query is to our database
    similarities = cosine_similarity(query_vec, corpus_vecs)[0]
    
    # Find the best match
    best_index = similarities.argmax()
    best_score = similarities[best_index]
    
    # Fallback if the confidence is too low (e.g., less than 20% match)
    if best_score < 0.2:
        return "I'm not completely sure about that. Could you try rephrasing or asking something else?", round(best_score * 100, 1)
        
    # Return the actual response from the CSV
    best_response = df.iloc[best_index]['response']
    return best_response, round(best_score * 100, 1)

# --- 3. CHAT INTERFACE ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User input box
user_query = st.chat_input("Type your question here...")

if user_query:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Get the SMART response using our NLP function!
    bot_response, confidence_score = get_bot_response(user_query, kb_df)
    
    # Show assistant response
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        st.caption(f"Confidence Score: **{confidence_score}%**") # Displays actual dynamic score [cite: 67]
        
        # Feedback buttons (needs unique keys based on message length)
        col1, col2 = st.columns(2)
        with col1:
            st.button("👍 Helpful", key=f"up_{len(st.session_state.messages)}")
        with col2:
            st.button("👎 Not Helpful", key=f"down_{len(st.session_state.messages)}")

    st.session_state.messages.append({"role": "assistant", "content": bot_response})