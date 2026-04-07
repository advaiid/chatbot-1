import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

KB_FILE_PATH = "data/knowledge_base.csv"
LOG_FILE_PATH = "data/chat_logs.csv"

# --- AUTHENTICATION WALL ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔒 Admin Login")
    st.write("Please enter the password to access the admin dashboard.")
    
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if password == "admin123":
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
    st.header("📊 Real-Time Chatbot Performance")
    
    if os.path.exists(LOG_FILE_PATH):
        logs_df = pd.read_csv(LOG_FILE_PATH)
        
        if not logs_df.empty:
            total_queries = len(logs_df)
            low_confidence_count = len(logs_df[logs_df['confidence'] < 20.0])
            avg_confidence = round(logs_df['confidence'].mean(), 1)
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Queries", total_queries)
            col2.metric("Low Confidence (<20%)", low_confidence_count)
            col3.metric("Avg Confidence Score", f"{avg_confidence}%")
            
            st.divider()
            
            st.subheader("Queries by Academic Category")
            category_counts = logs_df['category'].value_counts()
            
            fig, ax = plt.subplots(figsize=(7, 4))
            ax.bar(category_counts.index, category_counts.values, color='#4CAF50')
            ax.set_ylabel("Number of Queries")
            ax.set_title("Most Common Questions")
            plt.xticks(rotation=45)
            
            st.pyplot(fig)
        else:
            st.info("No chat logs recorded yet. Ask the bot a question!")
    else:
        st.warning("Chat log database not found.")

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
    st.header("💬 Recent User Chats")
    st.write("Review recent chat logs and user interactions.")
    if os.path.exists(LOG_FILE_PATH):
        logs_df = pd.read_csv(LOG_FILE_PATH)
        st.dataframe(logs_df.tail(20).iloc[::-1]) # Shows the 20 most recent logs, newest first
    else:
        st.write("No logs available yet.")

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