import streamlit as st
from datetime import datetime
import whisper
import torch
import os
import pyttsx4 as pyttsx
import numpy as np
import aiohttp
import json
from st_audiorec import st_audiorec

class SpeechToText:
    def __init__(self):
        cache_dir = os.path.expanduser("~/.cache/whisper")
        os.makedirs(cache_dir, exist_ok=True)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(
            "base",
            device=device,
            download_root=cache_dir,
            in_memory=True,
        )
        
    def transcribe(self, audio_data):
        result = self.model.transcribe(audio_data)
        return result["text"]

class InterviewManager:
    def __init__(self, cv_text, job_desc):
        self.cv_text = cv_text
        self.job_desc = job_desc
        self.conversation_history = []
        self.current_question = None
        
    async def generate_question(self):
        job_title = self.job_desc.split()[0]
        prompt = f"""
        Role: Senior Technical Interviewer specializing in {job_title} positions
    
        System Requirements:
        - Track key competencies covered
        - Monitor response quality and depth
        - End interview when sufficient data gathered for all core skills
        - Minimum 3 questions, maximum 7 questions
        - Ensure balanced assessment across technical areas
    
        Context:
        Job Requirements: {self.job_desc}
        Previous Conversation: {self.conversation_history}
        Questions Asked: {len([x for x in self.conversation_history if x[0] == "Interviewer"])}
    
        Instructions:
        Generate ONE technical interview question that:
        1. Maps directly to core {job_title} competencies
        2. Progresses logically from previous responses
        3. Tests both theoretical understanding and practical implementation
        4. Requires specific examples from candidate's experience
        5. Evaluates problem-solving methodology
    
        Question Parameters:
        - Must be specific and targeted
        - Should require 2-3 minute detailed response
        - Must evaluate both depth and breadth of knowledge
        - Should connect to real-world scenarios
        - If sufficient data gathered, return [END_INTERVIEW] instead of question
    
        Output Format:
        Return ONLY the question or [END_INTERVIEW], no additional text or context.
        """
    
        question = ""
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:11434/api/generate',
                                  json={
                                      "model": "llama3.2",
                                      "prompt": prompt,
                                      "stream": True
                                  }) as response:
                placeholder = st.empty()
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            question += data['response']
                            placeholder.write(question)
            
                if question.strip() == '[END_INTERVIEW]':
                    st.session_state.interview_score = await self.generate_score()
                    st.session_state.interview_active = False
                    return None
            
                self.conversation_history.append(("Interviewer", question))
                return question.strip()
    async def process_response(self, response):
        self.conversation_history.append(("Candidate", response))
        prompt = f"""
        Role: Technical Assessment Expert with 15+ years industry experience

        Complete Interview Context:
        {self.conversation_history}
    
        Current Response Being Evaluated: {response}
        Position Requirements: {self.job_desc}

        Evaluation Criteria:
        1. Technical Accuracy (Concepts, Terminology, Implementation)
        2. Problem-Solving Approach
        3. Communication Clarity
        4. Real-World Application
        5. Best Practices Awareness
        6. Consistency with Previous Responses
        7. Progressive Knowledge Demonstration

        Output Requirements:
        - One concise, actionable feedback paragraph
        - Maximum 3 sentences
        - Must reference any relevant connections to previous responses
        - Must include specific technical points
        - Balance positive aspects and improvement areas
        - Link directly to job requirements
        - If interview should end, start response with [END_INTERVIEW]

        Format: Direct feedback only, no preamble or explanation.
        """
    
        comment = ""
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:11434/api/generate',
                                  json={
                                      "model": "llama3.2",
                                      "prompt": prompt,
                                      "stream": True
                                  }) as response:
                placeholder = st.empty()
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            comment += data['response']
                            placeholder.write(comment)
            
                if comment.strip().startswith('[END_INTERVIEW]'):
                    st.session_state.interview_score = await self.generate_score()
                    st.session_state.interview_active = False
                    return None
            
                return comment.strip()

    async def generate_score(self):
        prompt = f"""
        Role: Chief Technical Officer conducting final candidate evaluation
        
        Complete Interview Transcript:
        {self.conversation_history}
        
        Position Requirements:
        {self.job_desc}
        
        Evaluation Framework:
        1. Technical Proficiency
        2. Problem-Solving Methodology
        3. Communication Effectiveness
        4. Industry Knowledge
        5. Growth Potential
        
        Required Output Format:
        Score: [X]/10
        
        Technical Strengths:
        - [Specific technical capability demonstrated]
        - [Problem-solving approach highlight]
        - [Communication or methodology strength]
        
        Development Areas:
        - [Primary technical gap identified]
        - [Secondary improvement opportunity]
        
        Hiring Recommendation: [HIRE/NO HIRE] because [one-line decisive justification]
        
        Note: Be extremely specific and reference actual responses from the conversation.
        """
        
        score = ""
        async with aiohttp.ClientSession() as session:
            async with session.post('http://localhost:11434/api/generate',
                                  json={
                                      "model": "llama3.2",
                                      "prompt": prompt,
                                      "stream": True
                                  }) as response:
                placeholder = st.empty()
                async for line in response.content:
                    if line:
                        data = json.loads(line)
                        if 'response' in data:
                            score += data['response']
                            placeholder.write(score)
                return score.strip()
class Interview:
    def __init__(self):
        self.speech_to_text = SpeechToText()
        os.makedirs('temp', exist_ok=True)
        os.makedirs('interviews', exist_ok=True)

    def text_to_speech(self, text):
        engine = pyttsx.init()
        engine.say(text)
        engine.save_to_file(text, 'temp/question.mp3')
        engine.runAndWait()

    def get_transcription(self, audio_data):
        if audio_data is not None:
            temp_file = "temp/temp_recording.wav"
            with open(temp_file, 'wb') as f:
                f.write(audio_data)
            return self.speech_to_text.transcribe(temp_file)
        return None

    async def save_interview_analysis(self, db, candidate_id, job_id, analysis_text):
        # Parse the analysis text to extract key information
        lines = analysis_text.split('\n')
        score = next(line.split(': ')[1] for line in lines if line.startswith('Score:'))
        recommendation = next(line for line in lines if line.startswith('Recommendation:')).split(': ')[1]
        is_hired = 'Hire' in recommendation.split()[0]
        
        # Format strengths and areas for growth
        strengths = []
        areas_growth = []
        current_section = None
        
        for line in lines:
            if 'Strengths:' in line:
                current_section = 'strengths'
            elif 'Areas for Growth:' in line:
                current_section = 'growth'
            elif line.strip().startswith('- '):
                if current_section == 'strengths':
                    strengths.append(line.strip()[2:])
                elif current_section == 'growth':
                    areas_growth.append(line.strip()[2:])
        
        # Create analysis summary
        analysis_summary = {
            'score': score,
            'strengths': strengths,
            'areas_for_growth': areas_growth,
            'recommendation': recommendation,
            'is_hired': is_hired
        }
        
        # Save to database
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        db.save_interview_result(
            candidate_id=candidate_id,
            job_id=job_id,
            interview_date=timestamp,
            score=score,
            strengths=', '.join(strengths),
            improvements=', '.join(areas_growth),
            recommendation=recommendation,
            is_hired=is_hired
        )
        
        return analysis_summary

    async def render_interview_page(self, db):
        st.title("AI Interview Assessment")
        
        for key in ['interview_manager', 'current_question', 
                   'interview_active', 'tts_active', 'interview_score']:
            if key not in st.session_state:
                st.session_state[key] = None

        if not st.session_state.interview_active:
            st.header("Interview Setup")
            
            st.subheader("Test Your Microphone")
            wav_audio_data = st_audiorec()
            if wav_audio_data is not None:
                st.audio(wav_audio_data, format='audio/wav')
            
            jobs = db.get_all_jobs()
            job_titles = {job[1]: job[0] for job in jobs}
            selected_job = st.selectbox("Select Job Position", list(job_titles.keys()))
            
            if selected_job:
                candidates = db.get_candidates_by_job(job_titles[selected_job])
                if candidates:
                    selected_candidate = st.selectbox("Select Candidate", [c[0] for c in candidates])
                    
                    if st.button("Start Interview"):
                        job_desc = db.get_job_description(job_titles[selected_job])
                        cv_text = db.get_candidate_cv(selected_candidate)
                        
                        st.session_state.interview_manager = InterviewManager(cv_text, job_desc)
                        st.session_state.current_question = await st.session_state.interview_manager.generate_question()
                        
                        if st.session_state.current_question:
                            st.session_state.tts_active = True
                            self.text_to_speech(st.session_state.current_question)
                            st.session_state.interview_active = True
                        st.rerun()
        if st.session_state.interview_active:
            if st.button("⏹️ End Interview"):
                st.session_state.interview_score = await st.session_state.interview_manager.generate_score()
                st.session_state.interview_active = False
                st.rerun()

            if 'audio_recorded' not in st.session_state:
                st.session_state.audio_recorded = False
                
            st.write("Current Question:", st.session_state.current_question)
            
            wav_audio_data = st_audiorec()
            
            if wav_audio_data is not None and not st.session_state.audio_recorded:
                st.session_state.audio_recorded = True
                transcription = self.get_transcription(wav_audio_data)
                if transcription:
                    st.write("Your Response:", transcription)
                    response = await st.session_state.interview_manager.process_response(transcription)
                    if response:
                        st.session_state.tts_active = True
                        self.text_to_speech(response)
                    st.session_state.current_question = await st.session_state.interview_manager.generate_question()
                    if st.session_state.current_question:
                        st.session_state.tts_active = True
                        self.text_to_speech(st.session_state.current_question)
                    # Reset the audio recording state
                    st.session_state.audio_recorded = False
                    st.rerun()
            if st.session_state.interview_manager:
                st.subheader("Interview Progress")
                for role, text in st.session_state.interview_manager.conversation_history:
                    st.markdown(f"**{'AI' if role == 'Interviewer' else 'You'}**: {text}")

        if st.session_state.interview_score:
            st.subheader("Interview Assessment")
            st.write(st.session_state.interview_score)
            
            # Save analysis after interview completion
            analysis_summary = await self.save_interview_analysis(
                db=db,
                candidate_id=selected_candidate,
                job_id=job_titles[selected_job],
                analysis_text=st.session_state.interview_score
            )
            
            # Display save confirmation
            st.success("Interview analysis saved successfully!")
            
            # Show hiring status
            if analysis_summary['is_hired']:
                st.balloons()
                st.success(f"Candidate recommended for hire with score {analysis_summary['score']}")
            else:
                st.warning(f"Candidate not recommended for hire. Score: {analysis_summary['score']}")
