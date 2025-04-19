import streamlit as st
import requests
import json
from pathlib import Path
import tempfile
import os
from resume_export import generate_pdf, generate_docx, get_available_styles

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

# Initialize session state for resume text, job description and contact info
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'job_description' not in st.session_state:
    st.session_state.job_description = ""
if 'enhanced_resume' not in st.session_state:
    st.session_state.enhanced_resume = None
if 'score_report' not in st.session_state:
    st.session_state.score_report = None
if 'contact_info' not in st.session_state:
    st.session_state.contact_info = {
        'name': '',
        'email': '',
        'phone': '',
        'location': '',
        'linkedin': '',
        'github': '',
        'website': ''
    }

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

# Add this after the col1 and col2 creation
with st.expander("Contact Information (for Resume Header)"):
    contact_col1, contact_col2 = st.columns(2)
    
    with contact_col1:
        st.session_state.contact_info['name'] = st.text_input("Full Name", value=st.session_state.contact_info.get('name', ''))
        st.session_state.contact_info['email'] = st.text_input("Email", value=st.session_state.contact_info.get('email', ''))
        st.session_state.contact_info['phone'] = st.text_input("Phone", value=st.session_state.contact_info.get('phone', ''))
        st.session_state.contact_info['location'] = st.text_input("Location", value=st.session_state.contact_info.get('location', ''), 
                                                help="City, State or Country")
    
    with contact_col2:
        st.session_state.contact_info['linkedin'] = st.text_input("LinkedIn URL", value=st.session_state.contact_info.get('linkedin', ''))
        st.session_state.contact_info['github'] = st.text_input("GitHub URL", value=st.session_state.contact_info.get('github', ''))
        st.session_state.contact_info['website'] = st.text_input("Personal Website", value=st.session_state.contact_info.get('website', ''))

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
                    
                    # Store the result in session state for later use
                    st.session_state.enhanced_resume = result['enhanced_resume']
                    st.session_state.score_report = result['score_report']
                    
                    # Display enhanced resume
                    st.subheader("Enhanced Resume")
                    st.text_area("Enhanced resume content", st.session_state.enhanced_resume, height=400)
                    
                    # Display score report
                    st.subheader("Score Report")
                    score_report = st.session_state.score_report
                    
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
                    
                else:
                    st.error("Failed to optimize resume. Please try again.")
            
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

# Add resume export options only if we have an enhanced resume
if st.session_state.enhanced_resume:
    st.subheader("Export Options")
    
    # Create columns for formatting options
    format_col1, format_col2 = st.columns(2)
    
    with format_col1:
        # Resume style selection
        st.markdown("**Resume Style**")
        resume_style = st.selectbox(
            "Choose formatting style:",
            options=get_available_styles(),
            index=0,
            help="Select a style for your resume export",
            key="resume_style"
        )
        
        # Add an explanation of the selected style
        if resume_style == "ATS-Friendly":
            st.info("Simple, clean format optimized for Applicant Tracking Systems.")
        elif resume_style == "Modern":
            st.info("Contemporary design with clean spacing and subtle color accents.")
        elif resume_style == "Professional":
            st.info("Traditional serif fonts with formal formatting for conservative industries.")
    
    with format_col2:
        # Export format selection
        st.markdown("**File Format**")
        export_format = st.radio(
            "Choose export format:",
            options=["PDF", "DOCX", "TXT"],
            index=0,
            horizontal=True,
            help="Select which file format to download",
            key="export_format"
        )
        
        # Show advanced options for PDF if selected
        if export_format == "PDF":
            with st.expander("PDF Generation Troubleshooting"):
                st.markdown("""
                **Note:** PDF generation requires wkhtmltopdf to be installed on your system.
                
                If you're having issues:
                1. Make sure [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) is installed
                2. If installed but not found, specify the path below
                """)
                
                wkhtmltopdf_path = st.text_input(
                    "Path to wkhtmltopdf (optional):",
                    placeholder="e.g., C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe",
                    help="Leave empty to use system PATH",
                    key="wkhtmltopdf_path"
                )
                
                if wkhtmltopdf_path:
                    # Import here to avoid circular imports
                    import resume_export
                    resume_export.WKHTMLTOPDF_PATH = wkhtmltopdf_path
    
    # Generate download buttons based on selection
    export_col1, export_col2, export_col3 = st.columns([1, 2, 1])
    
    with export_col2:
        if export_format == "PDF":
            # Check if PDF generation is enabled
            pdf_enabled = False
            try:
                from resume_export import ENABLE_PDF_GENERATION
                pdf_enabled = ENABLE_PDF_GENERATION
            except ImportError:
                pdf_enabled = False
            
            if not pdf_enabled:
                st.warning("""
                PDF generation is currently disabled. To enable it:
                
                1. Install wkhtmltopdf from https://wkhtmltopdf.org/downloads.html
                2. Set ENABLE_PDF_GENERATION = True in resume_export.py
                3. If needed, set WKHTMLTOPDF_PATH to the executable path
                
                Downloading as text instead.
                """)
                
                st.download_button(
                    label="Download as Text (Fallback)",
                    data=st.session_state.enhanced_resume,
                    file_name="enhanced_resume.txt",
                    mime="text/plain",
                    use_container_width=True
                )
            else:
                # Generate PDF based on the selected style
                try:
                    pdf_bytes = generate_pdf(
                        st.session_state.enhanced_resume, 
                        style=resume_style,
                        name=st.session_state.contact_info.get('name', 'Optimized Resume'),
                        email=st.session_state.contact_info.get('email'),
                        phone=st.session_state.contact_info.get('phone'),
                        location=st.session_state.contact_info.get('location'),
                        linkedin=st.session_state.contact_info.get('linkedin'),
                        github=st.session_state.contact_info.get('github'),
                        website=st.session_state.contact_info.get('website')
                    )
                    
                    st.download_button(
                        label=f"Download {resume_style} Resume as PDF",
                        data=pdf_bytes,
                        file_name=f"enhanced_resume_{resume_style.lower().replace('-', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                    
                except Exception as e:
                    st.error(f"Error generating PDF: {str(e)}")
                    st.warning("""
                    PDF generation failed. This might be because:
                    1. wkhtmltopdf is not installed
                    2. wkhtmltopdf is not in your PATH
                    3. The path specified is incorrect
                    
                    The app requires wkhtmltopdf for PDF generation.
                    """)
                    st.download_button(
                        label="Download as Text (Fallback)",
                        data=st.session_state.enhanced_resume,
                        file_name="enhanced_resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
        elif export_format == "DOCX":
            # Generate DOCX based on the selected style
            try:
                docx_bytes = generate_docx(
                    st.session_state.enhanced_resume, 
                    style=resume_style,
                    name=st.session_state.contact_info.get('name', 'Optimized Resume'),
                    email=st.session_state.contact_info.get('email'),
                    phone=st.session_state.contact_info.get('phone'),
                    location=st.session_state.contact_info.get('location'),
                    linkedin=st.session_state.contact_info.get('linkedin'),
                    github=st.session_state.contact_info.get('github'),
                    website=st.session_state.contact_info.get('website')
                )
                
                st.download_button(
                    label=f"Download {resume_style} Resume as DOCX",
                    data=docx_bytes,
                    file_name=f"enhanced_resume_{resume_style.lower().replace('-', '_')}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True
                )
                
            except Exception as e:
                st.error(f"Error generating DOCX: {str(e)}")
                st.download_button(
                    label="Download as Text (Fallback)",
                    data=st.session_state.enhanced_resume,
                    file_name="enhanced_resume.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        else:  # TXT format
            st.download_button(
                label="Download as Plain Text",
                data=st.session_state.enhanced_resume,
                file_name="enhanced_resume.txt",
                mime="text/plain",
                use_container_width=True
            )

# Add footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit") 