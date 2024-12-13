class InterviewPrompts:
    @staticmethod
    def generate_technical_question(job_title, cv_text, job_desc, conversation_history):
        return f"""
        Role: Senior Technical Interviewer specializing in {job_title} positions
        
        Context:
        Job Requirements: {job_desc}
        Previous Conversation: {conversation_history}
        
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
        
        Output Format:
        Return ONLY the question, no additional text or context.
        """

    @staticmethod
    def evaluate_response(response, job_desc):
        return f"""
        Role: Technical Assessment Expert with 15+ years industry experience
        
        Analysis Target:
        Candidate Response: {response}
        Position Requirements: {job_desc}
        
        Evaluation Criteria:
        1. Technical Accuracy (Concepts, Terminology, Implementation)
        2. Problem-Solving Approach
        3. Communication Clarity
        4. Real-World Application
        5. Best Practices Awareness
        
        Output Requirements:
        - One concise, actionable feedback paragraph
        - Maximum 3 sentences
        - Must include specific technical points
        - Balance positive aspects and improvement areas
        - Link directly to job requirements
        
        Format: Direct feedback only, no preamble or explanation.
        """

    @staticmethod
    def generate_final_evaluation(conversation_history, job_desc):
        return f"""
        Role: Chief Technical Officer conducting final candidate evaluation
        
        Complete Interview Transcript:
        {conversation_history}
        
        Position Requirements:
        {job_desc}
        
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
