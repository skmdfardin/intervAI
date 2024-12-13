import streamlit as st
import pandas as pd

def render_jobs_page(db):
    st.title("Job Management")
    
    with st.form("new_job"):
        job_title = st.text_input("Job Title")
        job_description = st.text_area("Job Description")
        if st.form_submit_button("Add Job"):
            db.add_job(job_title, job_description)
            st.success("Job added successfully!")
    
    jobs = db.get_all_jobs()
    if jobs:
        st.subheader("Existing Jobs")
        job_df = pd.DataFrame(jobs, columns=["ID", "Title", "Description", "Created At"])
        st.dataframe(job_df)
