import asyncio
import streamlit as st
import os
from components.jobs import render_jobs_page
from components.cv_analysis import render_cv_page
from components.rankings import render_rankings_page
from components.interview import Interview
from models import Database
import logging
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
interview = Interview()

# Constants
TEMP_DIR = "temp"
INTERVIEW_RECORDINGS_DIR = "recordings"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(INTERVIEW_RECORDINGS_DIR, exist_ok=True)

# Initialize database
db = Database()

def render_interview_results():
    st.title("Interview Results Dashboard 📊")
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        jobs = db.get_all_jobs()
        job_titles = {job[1]: job[0] for job in jobs}
        selected_job = st.selectbox("Filter by Job Position", ["All"] + list(job_titles.keys()))
    
    # Get interview results
    if selected_job == "All":
        results = db.get_interview_results()
    else:
        results = db.get_interview_results(job_id=job_titles[selected_job])
    
    if results:
        # Convert to DataFrame for better display
        df = pd.DataFrame(results, columns=[
            'ID', 'Candidate ID', 'Job ID', 'Interview Date', 'Score',
            'Strengths', 'Improvements', 'Recommendation', 'Hired', 'Recording'
        ])
        
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Interviews", len(df))
        with col2:
            hired_count = len(df[df['Hired'] == True])
            st.metric("Candidates Hired", hired_count)
        with col3:
            avg_score = df['Score'].apply(lambda x: float(x.split('/')[0])).mean()
            st.metric("Average Score", f"{avg_score:.1f}/10")
        
        # Display detailed results
        st.subheader("Interview Details")
        for _, row in df.iterrows():
            with st.expander(f"Interview on {row['Interview Date']} - Score: {row['Score']}"):
                st.write("**Strengths:**")
                for strength in row['Strengths'].split(', '):
                    st.write(f"- {strength}")
                
                st.write("**Areas for Improvement:**")
                for improvement in row['Improvements'].split(', '):
                    st.write(f"- {improvement}")
                
                st.write("**Final Recommendation:**")
                st.write(row['Recommendation'])
                
                if row['Recording']:
                    st.audio(row['Recording'])
                
                status_color = "🟢" if row['Hired'] else "🔴"
                st.write(f"Hiring Status: {status_color} {'Hired' if row['Hired'] else 'Not Hired'}")

# Page config
st.set_page_config(
    page_title="AI Interview Assistant",
    page_icon="🎙️",
    layout="wide"
)

# Add custom CSS
st.markdown("""
    <style>
    .stButton>button {
        height: 3em;
    }
    .main .block-container {
        padding-top: 2rem;
    }
    .interview-response {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .interview-question {
        font-weight: bold;
        color: #0066cc;
    }
    .interview-score {
        font-size: 1.5rem;
        color: #2ecc71;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'interview_active' not in st.session_state:
    st.session_state.interview_active = False
if 'interview_manager' not in st.session_state:
    st.session_state.interview_manager = None
if 'candidate_id' not in st.session_state:
    st.session_state.candidate_id = None
if 'audio_buffer' not in st.session_state:
    st.session_state.audio_buffer = []
if 'interview_recording' not in st.session_state:
    st.session_state.interview_recording = None
if 'transcript' not in st.session_state:
    st.session_state.transcript = []
if 'interview_score' not in st.session_state:
    st.session_state.interview_score = None

# Sidebar navigation
st.sidebar.title("AI Interview System 🤖")
page = st.sidebar.radio(
    label="Navigation",
    options=[
        "🎥 Interview Assessment",
        "📊 Interview Results",
        "🏢 Manage Jobs",
        "📄 Analyze CVs",
        "📈 View Rankings"
    ]
)

# Route to appropriate page
if page == "🎥 Interview Assessment":
    asyncio.run(interview.render_interview_page(db))
elif page == "📊 Interview Results":
    render_interview_results()
elif page == "🏢 Manage Jobs":
    render_jobs_page(db)
elif page == "📄 Analyze CVs":
    render_cv_page(db, TEMP_DIR)
elif page == "📈 View Rankings":
    render_rankings_page(db)