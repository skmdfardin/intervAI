import streamlit as st
import pandas as pd

def render_rankings_page(db):
    st.title("Candidate Rankings")
    
    jobs = db.get_all_jobs()
    job_titles = {job[1]: job[0] for job in jobs}
    selected_job = st.selectbox("Select Job", list(job_titles.keys()))
    
    if selected_job:
        candidates = db.get_candidates_by_job(job_titles[selected_job])
        if candidates:
            df = pd.DataFrame(candidates, columns=["Name", "Score", "Analysis", "Date"])
            df = df.sort_values(by="Score", ascending=False)
            st.dataframe(df)
        else:
            st.info("No candidates analyzed for this job yet.")
