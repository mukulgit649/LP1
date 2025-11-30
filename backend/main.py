from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
import sys

# Add current directory to path so we can import core modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.nlp import calculate_role_fit_score, analyze_skill_gaps, get_recruiter_metrics, get_sentence_scores
from core.genai import generate_achievement, get_sub_scores, generate_project_idea
from core.utils import extract_text_from_pdf_bytes

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now (dev mode)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    jd_text: str
    resume_text: Optional[str] = None

class GenAIRequest(BaseModel):
    prompt: str
    api_key: str
    model_name: str
    context: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "AI Resume Fixer API is running"}

@app.post("/api/analyze")
async def analyze_resume(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    api_key: str = Form(...),
    model_name: str = Form(...)
):
    try:
        # Extract text from PDF bytes
        content = await resume_file.read()
        resume_text = extract_text_from_pdf_bytes(content)
        
        if not resume_text:
            raise HTTPException(status_code=400, detail="Could not extract text from PDF")
            
        # NLP Analysis
        score = calculate_role_fit_score(resume_text, jd_text, api_key)
        missing_skills = list(analyze_skill_gaps(resume_text, jd_text, api_key))
        recruiter_metrics = get_recruiter_metrics(resume_text)
        sentence_scores = get_sentence_scores(resume_text, jd_text, api_key)
        
        # GenAI Analysis (Sub-scores)
        sub_scores = get_sub_scores(resume_text, jd_text, api_key, model_name)
        
        return {
            "score": score,
            "missing_skills": missing_skills,
            "recruiter_metrics": recruiter_metrics,
            "sentence_scores": sentence_scores,
            "sub_scores": sub_scores,
            "resume_text": resume_text[:1000] + "..." # Preview
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-achievement")
async def generate_achievement_endpoint(
    bullet_point: str = Form(...),
    job_title: str = Form(...),
    api_key: str = Form(...),
    model_name: str = Form(...)
):
    try:
        enhanced_text = generate_achievement(bullet_point, job_title, api_key, model_name)
        return {"enhanced_text": enhanced_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-project")
async def generate_project_endpoint(
    skill: str = Form(...),
    api_key: str = Form(...),
    model_name: str = Form(...)
):
    try:
        idea = generate_project_idea(skill, api_key, model_name)
        return {"idea": idea}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
