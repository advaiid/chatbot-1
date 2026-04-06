import streamlit as st
import pandas as pd

st.title("⚙️ Admin Dashboard")

# Use tabs to organize the admin panel
tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📝 Edit Knowledge Base", "💬 Chat Logs"])

with tab1:
    st.header("Chatbot Performance")
    # Placeholder for matplotlib charts or Streamlit native charts [cite: 49]
    st.metric(label="Total Queries Today", value="142", delta="12")
    st.metric(label="Low Confidence Queries", value="5", delta="-2")

with tab2:
    st.header("Manage Questions")
    st.write("Upload or edit the existing question patterns.")
    # You can use st.data_editor to let admins edit a dataframe directly!
    dummy_data = pd.DataFrame({
        "Category": ["Exams", "Attendance"],
        "Question": ["When is the final?", "What is the minimum attendance?"],
        "Answer": ["Next Monday.", "75% minimum."]
    })
    edited_df = st.data_editor(dummy_data, num_rows="dynamic")
    st.button("Save Changes")

with tab3:
    st.header("Recent User Chats")
    st.write("Review recent chats to see if they were useful.")
    # Display logs here