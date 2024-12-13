import sqlite3
import uuid
from datetime import datetime

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('cv_analyzer.db')
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id TEXT PRIMARY KEY,
                job_id TEXT,
                name TEXT NOT NULL,
                cv_path TEXT NOT NULL,
                score FLOAT,
                analysis_result TEXT,
                email TEXT,
                phone TEXT,
                location TEXT,
                interview_score FLOAT,
                created_at TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS interview_sessions (
                id TEXT PRIMARY KEY,
                candidate_id TEXT,
                job_id TEXT,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                completion_status TEXT,
                cheating_detected BOOLEAN,
                recording_path TEXT,
                final_score FLOAT,
                notes TEXT,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS interview_results (
                id TEXT PRIMARY KEY,
                candidate_id TEXT,
                job_id TEXT,
                interview_date TIMESTAMP,
                score TEXT,
                strengths TEXT,
                improvements TEXT,
                recommendation TEXT,
                is_hired BOOLEAN,
                recording_path TEXT,
                FOREIGN KEY (candidate_id) REFERENCES candidates (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        self.conn.commit()

    def log_interview_session(self, candidate_id, job_id, status, cheating=False, recording_path=None, score=None, notes=None):
        session_id = str(uuid.uuid4())
        self.conn.execute('''
            INSERT INTO interview_sessions 
            (id, candidate_id, job_id, start_time, end_time, completion_status, 
             cheating_detected, recording_path, final_score, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (session_id, candidate_id, job_id, datetime.now(), 
              datetime.now(), status, cheating, recording_path, score, notes))
        self.conn.commit()
    def add_job(self, title, description):
        job_id = str(uuid.uuid4())
        self.conn.execute('''
            INSERT INTO jobs (id, title, description, created_at)
            VALUES (?, ?, ?, ?)
        ''', (job_id, title, description, datetime.now()))
        self.conn.commit()
        return job_id

    def add_candidate(self, job_id, name, cv_path, score, analysis, email=None, phone=None, location=None):
        candidate_id = str(uuid.uuid4())
        self.conn.execute('''
            INSERT INTO candidates (
                id, job_id, name, cv_path, score, analysis_result,
                email, phone, location, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (candidate_id, job_id, name, cv_path, score, analysis, 
              email, phone, location, datetime.now()))
        self.conn.commit()
        return candidate_id
    def get_all_jobs(self):
        cursor = self.conn.execute('SELECT * FROM jobs ORDER BY created_at DESC')
        return cursor.fetchall()
    
    def get_job_description(self, job_id):
        cursor = self.conn.execute('SELECT description FROM jobs WHERE id = ?', (job_id,))
        return cursor.fetchone()[0]
    
    def get_candidates_by_job(self, job_id):
        cursor = self.conn.execute('''
            SELECT name, score, analysis_result, created_at 
            FROM candidates 
            WHERE job_id = ?
            ORDER BY score DESC
        ''', (job_id,))
        return cursor.fetchall()

    def get_candidate_cv(self, candidate_name):
        cursor = self.conn.execute('''
            SELECT cv_path FROM candidates 
            WHERE name = ?
        ''', (candidate_name,))
        result = cursor.fetchone()
        if result:
            cv_path = result[0]
            with open(cv_path, 'r') as f:
                return f.read()
        return None

    def update_interview_score(self, candidate_id, interview_score):
        self.conn.execute('''
            UPDATE candidates 
            SET interview_score = ? 
            WHERE id = ?
        ''', (interview_score, candidate_id))
        self.conn.commit()
    def save_interview_result(self, candidate_id, job_id, interview_date, score, 
                            strengths, improvements, recommendation, is_hired, recording_path=None):
        result_id = str(uuid.uuid4())
        self.conn.execute('''
            INSERT INTO interview_results (
                id, candidate_id, job_id, interview_date, score,
                strengths, improvements, recommendation, is_hired, recording_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (result_id, candidate_id, job_id, interview_date, score,
              strengths, improvements, recommendation, is_hired, recording_path))
        self.conn.commit()
        return result_id

    def get_interview_results(self, candidate_id=None, job_id=None):
        query = 'SELECT * FROM interview_results WHERE 1=1'
        params = []
        
        if candidate_id:
            query += ' AND candidate_id = ?'
            params.append(candidate_id)
        if job_id:
            query += ' AND job_id = ?'
            params.append(job_id)
            
        query += ' ORDER BY interview_date DESC'
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()

    def get_candidate_interview_history(self, candidate_id):
        cursor = self.conn.execute('''
            SELECT ir.*, j.title as job_title 
            FROM interview_results ir
            JOIN jobs j ON ir.job_id = j.id
            WHERE ir.candidate_id = ?
            ORDER BY ir.interview_date DESC
        ''', (candidate_id,))
        return cursor.fetchall()