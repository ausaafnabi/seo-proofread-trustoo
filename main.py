import streamlit as st
from core.ui import display_header, display_file_uploads, file_processing, run_analysis, display_results
from dotenv import load_dotenv

load_dotenv()

def main():
    """Main function to run the application."""
    api_type = display_header()
    
    uploaded_posts, uploaded_keywords, uploaded_checklist, content_type, url = display_file_uploads()
    
    if st.button("Run Analysis"):
        if not uploaded_posts or not uploaded_keywords:
            st.warning("Please upload both a blog post and keywords file.")
            return
        
        with st.spinner('Processing...'):
            # Process the files
            initial_state = file_processing(uploaded_posts, uploaded_keywords, uploaded_checklist, content_type, url)
            
            if initial_state:
                progress_container = st.container()
                log_placeholder = progress_container.empty()
                
                # Run analysis
                final_state = run_analysis(initial_state, log_placeholder)
                display_results(final_state)
                
            else:
                st.error("Failed to process the files. Please check your uploads.")

if __name__ == "__main__":
    main()