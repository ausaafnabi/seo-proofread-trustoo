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
            checklist_file = '''a'''
        else:  # city
            checklist_file = '''0'''
        
        checklist = pd.read_csv(checklist_file).to_dict('records')
    
    # Set up RAG system
    # vectorstore, retriever = setup_rag_system(content)
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
        "pass_fail": "FAIL"
    }
    
    # Initialize the state
    # initial_state = {
    #     "content": content,
    #     "content_type": content_type,
    #     "keywords": keywords,
    #     "checklist": checklist,
    #     "url": url,
    #     "retriever": retriever,
    #     "keyword_analysis": {},
    #     "structure_analysis": {},
    #     "serp_data": None,
    #     "checklist_evaluation": [],
    #     "recommendations": [],
    #     "overall_score": 0,
    #     "pass_fail": "FAIL",
    #     "rag_context": []
    # }
    
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
                    "Status": "✅" if item.get("completed", False) else "❌",
                    "Reason": item.get("reason", "")
                })
            else:  # Pydantic model
                checklist_data.append({
                    "Category": item.category,
                    "Checklist Item": item.item,
                    "Status": "✅" if item.completed else "❌",
                    "Reason": item.reason
                })
        
        checklist_df = pd.DataFrame(checklist_data)
        
        # Display the dataframe with colored rows based on status
        def color_status(val):
            color = 'green' if val == '✅' else 'red'
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
                1: "#ffcccc",  # High priority - light red
                2: "#ffe6cc",  # light orange
                3: "#ffffcc",  # light yellow
                4: "#e6ffcc",  # light green-yellow
                5: "#ccffcc"   # Low priority - light green
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


def export_results(final_state):
    """Export the results as a Word document or PDF."""
    if final_state:
        export_format = st.selectbox("Export Format", ["Word", "PDF", "JSON"])
        
        if st.button("Export Results"):
            # Create a buffer for the data
            buffer = io.BytesIO()
            
            if export_format == "Word":
                document = docx.Document()
                
                document.add_heading("SEO Content Evaluation Report", 0)
                
                document.add_paragraph(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
                document.add_heading("Overall Assessment", 1)
                document.add_paragraph(f"Score: {final_state['overall_score']:.1f}%")
                document.add_paragraph(f"Status: {final_state['pass_fail']}")
                
                document.add_heading("Keyword Analysis", 1)
                if 'keyword_analysis' in final_state and 'overall_keyword_score' in final_state['keyword_analysis']:
                    document.add_paragraph(f"Score: {final_state['keyword_analysis']['overall_keyword_score']}/100")
                    
                    if 'strengths' in final_state['keyword_analysis']:
                        document.add_heading("Strengths", 2)
                        for strength in final_state['keyword_analysis']['strengths']:
                            document.add_paragraph(f"• {strength}", style="List Bullet")
                    
                    if 'weaknesses' in final_state['keyword_analysis']:
                        document.add_heading("Weaknesses", 2)
                        for weakness in final_state['keyword_analysis']['weaknesses']:
                            document.add_paragraph(f"• {weakness}", style="List Bullet")
                
                document.add_heading("Structure Analysis", 1)
                if 'structure_analysis' in final_state and 'overall_structure_score' in final_state['structure_analysis']:
                    document.add_paragraph(f"Score: {final_state['structure_analysis']['overall_structure_score']}/100")
                    
                    if 'heading_structure' in final_state['structure_analysis']:
                        document.add_heading("Heading Structure", 2)
                        heading = final_state['structure_analysis']['heading_structure']
                        document.add_paragraph(f"H1 Count: {heading.get('h1_count', 0)}")
                        document.add_paragraph(f"H2 Count: {heading.get('h2_count', 0)}")
                        document.add_paragraph(f"H3 Count: {heading.get('h3_count', 0)}")
                        document.add_paragraph(f"Proper Hierarchy: {'Yes' if heading.get('heading_hierarchy_proper', False) else 'No'}")
                
                document.add_heading("Checklist Evaluation", 1)
                if final_state["checklist_evaluation"]:
                    table = document.add_table(rows=1, cols=4)
                    table.style = 'Table Grid'
                    
                    header_cells = table.rows[0].cells
                    header_cells[0].text = "Category"
                    header_cells[1].text = "Checklist Item"
                    header_cells[2].text = "Status"
                    header_cells[3].text = "Reason"
                    
                    for item in final_state["checklist_evaluation"]:
                        if isinstance(item, dict):
                            row_cells = table.add_row().cells
                            row_cells[0].text = item.get("category", "")
                            row_cells[1].text = item.get("item", "")
                            row_cells[2].text = "Pass" if item.get("completed", False) else "Fail"
                            row_cells[3].text = item.get("reason", "")
                        else:  # Pydantic model
                            row_cells = table.add_row().cells
                            row_cells[0].text = item.category
                            row_cells[1].text = item.item
                            row_cells[2].text = "Pass" if item.completed else "Fail"
                            row_cells[3].text = item.reason
                
                document.add_heading("Recommendations", 1)
                if final_state["recommendations"]:
                    for rec in final_state["recommendations"]:
                        if isinstance(rec, dict):
                            document.add_heading(f"Priority {rec.get('priority', 5)}: {rec.get('title', '')}", 2)
                            document.add_paragraph(rec.get("description", ""))
                        else:  # Pydantic model
                            document.add_heading(f"Priority {rec.priority}: {rec.title}", 2)
                            document.add_paragraph(rec.description)
                
                document.save(buffer)
                
                st.download_button(
                    label="Download Word Report",
                    data=buffer,
                    file_name="seo_report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            
            elif export_format == "JSON":
                # Create a JSON export
                export_data = {
                    "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "overall_score": final_state["overall_score"],
                    "status": final_state["pass_fail"],
                    "keyword_analysis": final_state["keyword_analysis"],
                    "structure_analysis": final_state["structure_analysis"],
                    "checklist_evaluation": [
                        item.model_dump() if hasattr(item, "model_dump") else item 
                        for item in final_state["checklist_evaluation"]
                    ],
                    "recommendations": [
                        item.model_dump() if hasattr(item, "model_dump") else item 
                        for item in final_state["recommendations"]
                    ]
                }
                
                json_data = json.dumps(export_data, indent=2)
                st.download_button(
                    label="Download JSON Report",
                    data=json_data,
                    file_name="seo_report.json",
                    mime="application/json"
                )
