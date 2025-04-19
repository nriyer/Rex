import streamlit as st
import requests
import json
from pathlib import Path
import tempfile
import os

# Set page config
st.set_page_config(
    page_title="Resume Optimizer",
    page_icon="📄",
    layout="wide"
)

# Title and description
st.title("📄 Resume Optimizer")
st.markdown("""
Enhance your resume to better match job descriptions and improve your chances of getting noticed by recruiters.
""")

# Initialize session state for resume text and job description
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""

# Create two columns for input
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Upload or Build Your Resume")
    
    # Resume input options
    resume_option = st.radio(
        "Choose how to input your resume:",
        ["Upload PDF", "Paste Text"],
        horizontal=True
    )
    
    if resume_option == "Upload PDF":
        uploaded_file = st.file_uploader("Upload your resume (PDF)", type=['pdf'])
        if uploaded_file is not None:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name
            
            # Call the backend to extract text
            try:
                with open(tmp_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post('http://localhost:8000/extract-text', files=files)
                    if response.status_code == 200:
                        st.session_state.resume_text = response.json()['text']
                        st.success("Resume uploaded successfully!")
                    else:
                        st.error("Failed to process the PDF file.")
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
            finally:
                # Clean up the temporary file
                os.unlink(tmp_path)
    
    else:  # Paste Text option
        st.session_state.resume_text = st.text_area(
            "Paste your resume text here:",
            height=300,
            value=st.session_state.resume_text
        )

with col2:
    st.subheader("2. Input Job Description")
    st.session_state.job_description = st.text_area(
        "Paste the job description here:",
        height=300,
        value=st.session_state.job_description
    )

# Add a divider
st.divider()

# Process button
if st.button("Optimize Resume", type="primary"):
    if not st.session_state.resume_text:
        st.error("Please provide your resume first.")
    elif not st.session_state.job_description:
        st.error("Please provide a job description.")
    else:
        with st.spinner("Optimizing your resume..."):
            try:
                # Call the backend optimization endpoint
                response = requests.post(
                    'http://localhost:8000/optimize-resume',
                    json={
                        'resume_text': st.session_state.resume_text,
                        'job_posting': st.session_state.job_description
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Display enhanced resume
                    st.subheader("Enhanced Resume")
                    st.text_area("", result['enhanced_resume'], height=400)
                    
                    # Display score report
                    st.subheader("Score Report")
                    score_report = result['score_report']
                    
                    # Create columns for before/after comparison
                    score_col1, score_col2 = st.columns(2)
                    
                    with score_col1:
                        st.markdown("**Before Optimization**")
                        st.metric("Match Percentage", f"{score_report['before']['match_percent']}%")
                        st.metric("Final Score", f"{score_report['before']['score_by_category']['final_score']:.1f}")
                    
                    with score_col2:
                        st.markdown("**After Optimization**")
                        st.metric("Match Percentage", f"{score_report['after']['match_percent']}%")
                        st.metric("Final Score", f"{score_report['after']['score_by_category']['final_score']:.1f}")
                    
                    # Add detailed category scores
                    st.markdown("### Detailed Category Scores")
                    
                    detail_col1, detail_col2 = st.columns(2)
                    
                    with detail_col1:
                        st.markdown("**Before:**")
                        for category, score in score_report['before']['score_by_category'].items():
                            if category != 'final_score':
                                st.metric(category.replace('_', ' ').title(), f"{score:.1f}")
                    
                    with detail_col2:
                        st.markdown("**After:**")
                        for category, score in score_report['after']['score_by_category'].items():
                            if category != 'final_score':
                                st.metric(category.replace('_', ' ').title(), f"{score:.1f}")
                    
                    # Download button
                    st.download_button(
                        label="Download Enhanced Resume",
                        data=result['enhanced_resume'],
                        file_name="enhanced_resume.txt",
                        mime="text/plain"
                    )
                    
                else:
                    st.error("Failed to optimize resume. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit") 