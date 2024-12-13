import streamlit as st
import os
from cv_analyzer import extract_text_from_pdf, analyze_cv

def process_cv(cv_text, candidate_name, job_id, db, temp_dir):
    job_desc = db.get_job_description(job_id)
    result = analyze_cv(job_desc, cv_text)
    
    lines = result.split('\n')
    details = {}
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            details[key.strip()] = value.strip()
    
    score = float(details.get('Score', '0').split('/')[0])
    cv_path = os.path.join(temp_dir, f"{candidate_name}_text.txt")
    
    if isinstance(cv_text, str):
        with open(cv_path, 'w') as f:
            f.write(cv_text)
    
    db.add_candidate(
        job_id=job_id,
        name=candidate_name,
        cv_path=cv_path,
        score=score,
        analysis=result,
        email=details.get('Email', 'Not found'),
        phone=details.get('Phone', 'Not found'),
        location=details.get('Location', 'Not found')
    )
    
    st.success("Analysis Complete!")
    st.write(result)

def render_cv_page(db, temp_dir):
    st.title("CV Analysis")
    
    jobs = db.get_all_jobs()
    job_titles = {job[1]: job[0] for job in jobs}
    selected_job = st.selectbox("Select Job", list(job_titles.keys()))
    
    input_method = st.radio("Choose input method:", ["Upload PDF", "Paste Text"])
    candidate_name = st.text_input("Candidate Name")
    
    if input_method == "Upload PDF":
        uploaded_file = st.file_uploader("Upload CV (PDF)", type="pdf")
        if uploaded_file and candidate_name and st.button("Analyze PDF CV"):
            with st.spinner("Analyzing..."):
                temp_path = os.path.join(temp_dir, f"{candidate_name}_{uploaded_file.name}")
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                cv_text = extract_text_from_pdf(temp_path)
                process_cv(cv_text, candidate_name, job_titles[selected_job], db, temp_dir)
    else:
        pasted_text = st.text_area("Paste CV text here:", height=300)
        if pasted_text and candidate_name and st.button("Analyze Text CV"):
            with st.spinner("Analyzing..."):
                process_cv(pasted_text, candidate_name, job_titles[selected_job], db, temp_dir)
