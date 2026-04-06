import streamlit as st
import pandas as pd
import os

st.title("⚙️ Admin Dashboard")

# Define the file path
KB_FILE_PATH = "data/knowledge_base.csv"

# Use tabs to organize the admin panel
tab1, tab2, tab3 = st.tabs(["📊 Analytics", "📝 Edit Knowledge Base", "💬 Chat Logs"])

with tab1:
    st.header("Chatbot Performance")
    st.metric(label="Total Queries Today", value="142", delta="12")
    st.metric(label="Low Confidence Queries", value="5", delta="-2")

with tab2:
    st.header("Manage Questions")
    st.write("Upload, edit, or delete existing question patterns.")
    
    # 1. Load the actual CSV file
    if os.path.exists(KB_FILE_PATH):
        # Read the file
        kb_df = pd.read_csv(KB_FILE_PATH)
        
        # 2. Display the editable dataframe
        # num_rows="dynamic" allows the admin to add or delete rows!
        edited_df = st.data_editor(kb_df, num_rows="dynamic", use_container_width=True)
        
        # 3. Create a functional Save Button
        if st.button("Save Changes to Database"):
            try:
                # This physically writes the changes back to the CSV file
                edited_df.to_csv(KB_FILE_PATH, index=False)
                st.success("✅ Knowledge base successfully updated!")
                # Clear the cache so the student chat page gets the new data immediately
                st.cache_data.clear() 
            except Exception as e:
                st.error(f"An error occurred while saving: {e}")
    else:
        st.error("Cannot find data/knowledge_base.csv. Please check the file path.")

with tab3:
    st.header("Recent User Chats")
    st.write("Review recent chats to see if they were useful.")
    # (Chat logs logic will go here later)