import streamlit as st

st.title("🎓 Student Academic Assistant")
st.write("Ask me in English or Malayalam!")

# 1. Initialize chat history in Streamlit's session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# 2. Display previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 3. Accept user input
user_query = st.chat_input("Type your question here...")

if user_query:
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(user_query)
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_query})

    # --- THIS IS WHERE YOUR AI/NLP LOGIC GOES ---
    # For now, we will just use a dummy response and dummy confidence score
    bot_response = "This is a placeholder answer about college policies."
    confidence_score = "95%"
    
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        st.markdown(bot_response)
        st.caption(f"Confidence Score: {confidence_score}") # Displays the score small [cite: 273]
        
        # Simple feedback buttons
        col1, col2 = st.columns(2)
        with col1:
            st.button("👍 Helpful")
        with col2:
            st.button("👎 Not Helpful")

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": bot_response})