import streamlit as st
import time
import pandas as pd
import os
import docx
import io
import json

from agents.workflow import create_workflow

from utils.helper import read_docx,read_excel,read_markdown,read_txt,detect_page_type
    
# if 'processbutton' not in st.session_state:
#     st.session_state.processbutton = False

# def process_query():
#     st.session_state.processbutton = not st.session_state.processbutton
#     st.text(st.session_state.processbutton)

# def process_event(log_placeholder):
#     log_placeholder.text("Processing started...")
#     time.sleep(1)  # Simulate some processing time

#     for i in range(5):
#         log_placeholder.text(f"Step {i + 1}: Processing...")
#         time.sleep(1)  # Simulate processing time for each step

#     log_placeholder.text("Processing completed!")

# with st.sidebar:
#     type = st.selectbox('Select backbone API:',['openai','openrouter'])
#     if type == 'openai':
#         openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
#     else:
#         openrouter_api_key = st.text_input("OpenRouter API Key", key="openrouter_api_key", type="password")

# st.title("SEO Proofreading Tool")
# st.caption("Reads the blogs and generate report based on checklist for Trustoo.nl")

# if type=='openai' and not openai_api_key:
#     st.info("Please add your OpenAI API key to continue.")
#     st.stop()
# elif type=='openrouter' and not openrouter_api_key:
#     st.info("Please add your OpenRouter API key to continue.")
#     st.stop()


# col1, col2 = st.columns(2)

# with col1:
#     uploaded_posts = st.file_uploader("Upload Blog Post", type=["docx", "txt", "markdown"])

# with col2:
#     uploaded_keywords = st.file_uploader("Upload Keywords", type=["xlsx"])

# uploaded_checklist = st.file_uploader("Upload Checklist", type=["xlsx"])
# is_city = st.selectbox('Type of Blog (Optional)', [None,'city','cost'])
# processButton = st.button('Submit',on_click=process_query)

# if st.button("Start Processing"):
#     # Create a placeholder for logs
#     log_placeholder = st.empty()
    
#     # Call the processing function
#     process_event(log_placeholder)

# if uploaded_posts is not None:
#     st.write("Post file uploaded:", uploaded_posts.name)

# if uploaded_keywords is not None:
#     st.write("Keyword file uploaded:", uploaded_keywords.name)

def read_file(file) -> str:
    """Read the content of a file based on its type."""
    file_type = file.name.split('.')[-1].lower()
    
    if file_type == 'docx':
        return read_docx(file)
    elif file_type == 'txt':
        return read_txt(file)
    elif file_type in ['md', 'markdown']:
        return read_markdown(file)
    else:
        st.error(f"Unsupported file type: {file_type}")
        return ""
    
def display_header():
    st.title("SEO Proofreading Tool")
    st.caption("Reads blogs and generates reports based on checklist for Trustoo.nl")
    
    with st.sidebar:
        api_type = st.selectbox('Select backbone API:', ['openai', 'openrouter'])
        if api_type == 'openai':
            openai_api_key = st.text_input("OpenAI API Key", key="openai_api_key", type="password")
            serp_api_key = st.text_input("SERP API Key", key="serp_api_key", type="password")
            if openai_api_key:
                os.environ["OPENAI_API_KEY"] = openai_api_key
                os.environ["SERP_API_KEY"] = serp_api_key
        else:
            openrouter_api_key = st.text_input("OpenRouter API Key", key="openrouter_api_key", type="password")
            serp_api_key = st.text_input("SERP API Key", key="serp_api_key", type="password")
            if openrouter_api_key:
                os.environ["OPENROUTER_API_KEY"] = openrouter_api_key
                os.environ["SERP_API_KEY"] = serp_api_key
    
    return api_type

def display_file_uploads():
    col1, col2 = st.columns(2)
    
    with col1:
        uploaded_posts = st.file_uploader("Upload Blog Post", type=["docx", "txt", "markdown"])
    
    with col2:
        uploaded_keywords = st.file_uploader("Upload Keywords", type=["xlsx"])
    
    uploaded_checklist = st.file_uploader("Upload Checklist", type=["xlsx"])
    content_type = st.selectbox('Type of Blog (Optional)', [None, 'city', 'cost'])
    url = st.text_input("Blog URL (Optional, for extracting meta data)")
    
    return uploaded_posts, uploaded_keywords, uploaded_checklist, content_type, url

def file_processing(uploaded_posts, uploaded_keywords, uploaded_checklist, content_type, url):
    if not uploaded_posts:
        st.warning("Please upload a blog post file.")
        return None
    
    if not uploaded_keywords:
        st.warning("Please upload a keywords file.")
        return None
    
    content = read_file(uploaded_posts)
    keywords = read_excel(uploaded_keywords).to_dict('records')
    
    # Detect content type if not provided
    if not content_type:
        content_type = detect_page_type(content)
        st.info(f"Content type detected: {content_type}")
    
    if uploaded_checklist:
        checklist = read_excel(uploaded_checklist).to_dict('records')
    else:
        # Use default checklist
        if content_type == "cost":
            checklist_file = '''./experimentation/data/SEO Content Checklist Cost Pages.xlsx'''
        else:  # city
            checklist_file = '''./experimentation/data/SEO Content Checklist Top 10 City Pages.xlsx'''
        
        checklist = read_excel(checklist_file).to_dict('records')
    
    initial_state = {
        "content": content,
        "content_type": content_type,
        "keywords": keywords,
        "checklist": checklist,
        "keyword_analysis": {},
        "structure_analysis": {},
        "checklist_evaluation": [],
        "recommendations": [],
        "overall_score": 0,
        "messages": [],
        "pass_fail": "FAIL"
    }

    
    return initial_state

def run_analysis(initial_state, log_placeholder):
    workflow = create_workflow()
    
    log_placeholder.text("Starting SEO content evaluation...")
    final_state = workflow.invoke(initial_state)
    time.sleep(0.5)
    log_placeholder.text("SEO evaluation completed!")
    
    return final_state

def display_results(final_state):
    st.header("SEO Content Evaluation Results")
    score = final_state["overall_score"]
    status = final_state["pass_fail"]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Overall Score", f"{score:.1f}%")
    with col2:
        if status == "PASS":
            st.success("Status: PASS")
        else:
            st.error("Status: FAIL")

    st.subheader("Checklist Evaluation")
    if final_state["checklist_evaluation"]:
        # Create a dataframe for the checklist evaluation
        checklist_data = []
        for item in final_state["checklist_evaluation"]:
            if isinstance(item, dict):
                checklist_data.append({
                    "Category": item.get("category", ""),
                    "Checklist Item": item.get("item", ""),
                    "Status": "Yes" if item.get("completed", False) else "No",
                    "Reason": item.get("reason", "")
                })
            else:  # Pydantic model
                checklist_data.append({
                    "Category": item.category,
                    "Checklist Item": item.item,
                    "Status": "Yes" if item.completed else "No",
                    "Reason": item.reason
                })
        
        checklist_df = pd.DataFrame(checklist_data)
        
        # Display the dataframe with colored rows based on status
        def color_status(val):
            color = 'green' if val == 'Yes' else 'red'
            return f'color: {color}'
        
        styled_df = checklist_df.style.applymap(color_status, subset=['Status'])
        st.dataframe(styled_df)
    
    # Display recommendations
    st.subheader("Recommendations")
    if final_state["recommendations"]:
        for i, rec in enumerate(final_state["recommendations"]):
            if isinstance(rec, dict):
                title = rec.get("title", "")
                description = rec.get("description", "")
                priority = rec.get("priority", 5)
            else:  # Pydantic model
                title = rec.title
                description = rec.description
                priority = rec.priority
            
            # Display with color based on priority
            priority_colors = {
                1: "#ae0455",  # High priority - dark pink
                2: "#8706b1",  # magenta
                3: "#d6bc06",  # orange yellow
                4: "#03a557",  # green
                5: "#10187f"   # dark blue
            }
            
            st.markdown(
                f"""
                <div style="background-color: {priority_colors.get(priority, '#f0f0f0')}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                    <h4>Priority {priority}: {title}</h4>
                    <p>{description}</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    else:
        st.info("No specific recommendations generated.")