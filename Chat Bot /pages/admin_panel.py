import streamlit as st
import pandas as pd
import os

KB_FILE_PATH = "data/knowledge_base.csv"

# --- AUTHENTICATION WALL ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔒 Admin Login")
    st.write("Please enter the password to access the admin dashboard.")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == "admin123": # Change this password as needed!
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Incorrect password.")
    st.stop() 

# --- DASHBOARD UI ---
st.title("⚙️ Admin Dashboard")
st.button("Logout", on_click=lambda: st.session_state.update(admin_logged_in=False))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Analytics", "📝 Edit Knowledge Base", "💬 Chat Logs", "📤 Bulk Upload"])

with tab1:
    st.header("Chatbot Performance")
    st.metric(label="Total Queries Today", value="142", delta="12")
    st.metric(label="Low Confidence Queries", value="5", delta="-2")
    st.info("Visual charts using matplotlib will be placed here.")

with tab2:
    st.header("Manage Questions")
    if os.path.exists(KB_FILE_PATH):
        kb_df = pd.read_csv(KB_FILE_PATH)
        edited_df = st.data_editor(kb_df, num_rows="dynamic", use_container_width=True)
        
        if st.button("Save Changes to Database"):
            try:
                edited_df.to_csv(KB_FILE_PATH, index=False)
                st.success("✅ Knowledge base updated!")
                st.cache_data.clear() 
            except Exception as e:
                st.error(f"Error saving: {e}")
    else:
        st.error("Cannot find knowledge_base.csv.")

with tab3:
    st.header("Recent User Chats")
    st.write("Review recent chat logs and user feedback here.")

with tab4:
    st.header("📤 Bulk Upload Knowledge Base")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

    if uploaded_file is not None:
        try:
            new_data = pd.read_csv(uploaded_file)
            st.dataframe(new_data.head()) 

            upload_action = st.radio("Apply method:", ("Append", "Overwrite"))

            if st.button("Apply Bulk Update"):
                if os.path.exists(KB_FILE_PATH):
                    existing_data = pd.read_csv(KB_FILE_PATH)

                    if upload_action == "Append":
                        combined_data = pd.concat([existing_data, new_data], ignore_index=True)
                        combined_data.drop_duplicates(subset='id', keep='last', inplace=True)
                        combined_data.to_csv(KB_FILE_PATH, index=False)
                        st.success(f"✅ Added {len(new_data)} new rows!")
                    else:
                        new_data.to_csv(KB_FILE_PATH, index=False)
                        st.success("✅ Replaced the knowledge base!")

                    st.cache_data.clear() 
                else:
                    st.error("Database file not found.")
        except Exception as e:
            st.error(f"Error: {e}")