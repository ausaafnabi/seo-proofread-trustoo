import streamlit as st
import time

if 'processbutton' not in st.session_state:
    st.session_state.processbutton = False

def process_query():
    st.session_state.processbutton = not st.session_state.processbutton
    st.text(st.session_state.processbutton)

def process_event(log_placeholder):
    log_placeholder.text("Processing started...")
    time.sleep(1)  # Simulate some processing time

    for i in range(5):
        log_placeholder.text(f"Step {i + 1}: Processing...")
        time.sleep(1)  # Simulate processing time for each step

    log_placeholder.text("Processing completed!")

with st.sidebar:
    type = st.selectbox('Select backbone API:',['openai','openrouter'])
    if type == 'openai':
        openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
    else:
        openrouter_api_key = st.text_input("OpenRouter API Key", key="openrouter_api_key", type="password")

st.title("SEO Proofreading Tool")
st.caption("Reads the blogs and generate report based on checklist for Trustoo.nl")

if type=='openai' and not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()
elif type=='openrouter' and not openrouter_api_key:
    st.info("Please add your OpenRouter API key to continue.")
    st.stop()


col1, col2 = st.columns(2)

with col1:
    uploaded_posts = st.file_uploader("Upload Blog Post", type=["docx", "txt", "markdown"])

with col2:
    uploaded_keywords = st.file_uploader("Upload Keywords", type=["xlsx"])

uploaded_checklist = st.file_uploader("Upload Checklist", type=["xlsx"])
is_city = st.selectbox('Type of Blog (Optional)', [None,'city','cost'])
processButton = st.button('Submit',on_click=process_query)

if st.button("Start Processing"):
    # Create a placeholder for logs
    log_placeholder = st.empty()
    
    # Call the processing function
    process_event(log_placeholder)

if uploaded_posts is not None:
    st.write("Post file uploaded:", uploaded_posts.name)

if uploaded_keywords is not None:
    st.write("Keyword file uploaded:", uploaded_keywords.name)