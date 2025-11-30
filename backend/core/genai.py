import google.generativeai as genai

def generate_achievement(bullet_point, job_title, api_key, model_name="gemini-2.0-flash-exp"):
    if not api_key:
        return "Please provide a valid API Key."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert Resume Writer.
        Rewrite the following resume bullet point using the STAR method (Situation, Task, Action, Result).
        Target Job Title: {job_title}
        Original Bullet Point: "{bullet_point}"
        
        Rules:
        1. Start with a strong action verb.
        2. Quantify results where possible (add numbers/percentages).
        3. Make it sound professional and impactful.
        4. Keep it to 1-2 sentences max.
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error generating content: {e}"

def get_sub_scores(resume_text, jd_text, api_key, model_name="gemini-2.0-flash-exp"):
    if not api_key:
        return {"Hard Skills": 0, "Soft Skills": 0, "Experience": 0, "Education": 0}
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are an expert Resume Grader.
        Analyze the following Resume against the Job Description.
        Provide a score from 0 to 100 for each of the following categories:
        1. Hard Skills (Technical match)
        2. Soft Skills (Communication, Leadership, etc.)
        3. Experience (Years, Relevance)
        4. Education (Degree match)
        
        Resume:
        {resume_text[:2000]}... (truncated)
        
        Job Description:
        {jd_text[:1000]}... (truncated)
        
        Return ONLY a valid JSON string in the following format:
        {{
            "Hard Skills": 85,
            "Soft Skills": 70,
            "Experience": 60,
            "Education": 90
        }}
        """
        
        response = model.generate_content(prompt)
        import json
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        return json.loads(text)
    except Exception as e:
        print(f"Error getting sub-scores: {e}")
        return {"Hard Skills": 50, "Soft Skills": 50, "Experience": 50, "Education": 50}

def generate_project_idea(skill, api_key, model_name="gemini-2.0-flash-exp"):
    if not api_key:
        return f"Build a project using {skill}."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
        You are a Career Coach.
        Suggest ONE specific, impressive project idea that a candidate can build to demonstrate the skill: "{skill}".
        Keep it concise (1 sentence).
        Example for SQL: "Build a Library Management System using MySQL to handle complex queries and transactions."
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Build a project using {skill}."
