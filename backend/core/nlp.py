import google.generativeai as genai
import os
import re
from typing import List, Set

# Configure Gemini
# Note: API Key is passed dynamically or set in env
def configure_gemini(api_key: str):
    if api_key:
        genai.configure(api_key=api_key)

def get_gemini_embedding(text: str, model="models/text-embedding-004"):
    try:
        result = genai.embed_content(
            model=model,
            content=text,
            task_type="semantic_similarity"
        )
        return result['embedding']
    except Exception as e:
        print(f"Embedding Error: {e}")
        return []

def calculate_role_fit_score(resume_text: str, jd_text: str, api_key: str) -> float:
    if not resume_text or not jd_text or not api_key:
        return 0.0
    
    configure_gemini(api_key)
    
    # Split into chunks (naive sentence splitting for speed)
    resume_sentences = [s.strip() for s in resume_text.split('.') if len(s.strip()) > 20]
    jd_sentences = [s.strip() for s in jd_text.split('.') if len(s.strip()) > 20]
    
    if not resume_sentences or not jd_sentences:
        return 0.0

    # Get Embeddings (Batching would be better but keeping it simple for now)
    # Gemini Embeddings are fast.
    
    # We will use a simplified approach: Embed the WHOLE text to get a global similarity score
    # This is much faster and often sufficient for "Role Fit"
    
    try:
        resume_emb = get_gemini_embedding(resume_text)
        jd_emb = get_gemini_embedding(jd_text)
        
        if not resume_emb or not jd_emb:
            return 0.0
            
        # Calculate Cosine Similarity manually
        def cosine_similarity(v1, v2):
            dot_product = sum(a*b for a, b in zip(v1, v2))
            magnitude1 = sum(a*a for a in v1) ** 0.5
            magnitude2 = sum(b*b for b in v2) ** 0.5
            if magnitude1 == 0 or magnitude2 == 0:
                return 0.0
            return dot_product / (magnitude1 * magnitude2)

        raw_score = cosine_similarity(resume_emb, jd_emb)
        
        # Scale score: 0.7 cosine similarity is usually very high for documents
        # Map 0.3 -> 0%, 0.8 -> 100%
        scaled_score = (raw_score - 0.3) / (0.8 - 0.3) * 100
        return round(min(100, max(0, scaled_score)), 2)
        
    except Exception as e:
        print(f"Scoring Error: {e}")
        return 0.0

def analyze_skill_gaps(resume_text: str, jd_text: str, api_key: str) -> Set[str]:
    if not resume_text or not jd_text or not api_key:
        return set()
        
    configure_gemini(api_key)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    prompt = f"""
    Act as a Senior Technical Recruiter.
    Compare the Resume and Job Description below.
    Identify strictly TECHNICAL skills that are REQUIRED in the Job Description but MISSING from the Resume.
    
    Rules:
    1. Return ONLY a comma-separated list of missing skills.
    2. Do not include soft skills (e.g., "communication", "leadership").
    3. Do not include generic terms (e.g., "development", "engineering").
    4. If no major skills are missing, return "None".
    
    JOB DESCRIPTION:
    {jd_text[:2000]}
    
    RESUME:
    {resume_text[:2000]}
    """
    
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if "None" in text or not text:
            return set()
            
        skills = {s.strip() for s in text.split(',') if s.strip()}
        return skills
    except Exception as e:
        print(f"Skill Gap Error: {e}")
        return set()

def get_sentence_scores(resume_text: str, jd_text: str, api_key: str):
    # For Heatmap: We need sentence-level scoring.
    # To save API calls, we'll just return a dummy list or a simplified version.
    # Real-time sentence embedding for 50+ sentences might be too slow/expensive for this demo.
    # Strategy: Return empty list for now to avoid OOM/Timeout, or implement a very lightweight keyword match.
    
    # Lightweight Keyword Match Fallback
    jd_words = set(jd_text.lower().split())
    sentences = [s.strip() for s in resume_text.split('.') if len(s.strip()) > 10]
    
    scores = []
    for sent in sentences:
        sent_words = set(sent.lower().split())
        overlap = len(sent_words.intersection(jd_words))
        score = min(1.0, overlap / len(sent_words)) if sent_words else 0
        scores.append((sent, score))
        
    return scores

def get_recruiter_metrics(resume_text: str):
    # Pure Python implementation (No Spacy)
    words = resume_text.split()
    word_count = len(words)
    reading_time_min = word_count / 250
    
    minutes = int(reading_time_min)
    seconds = int((reading_time_min - minutes) * 60)
    reading_time_str = f"{minutes}m {seconds}s"
    
    buzzwords = ["synergy", "hardworking", "motivated", "team player", "detail-oriented", "proactive", "passionate", "driven"]
    buzzword_count = sum(1 for word in words if word.lower() in buzzwords)
    
    # Simple heuristic for action verbs (checking first word of sentences or common verbs)
    strong_verbs_list = {"led", "built", "engineered", "developed", "managed", "created", "designed", "implemented", "orchestrated", "spearheaded", "executed", "launched"}
    action_verb_count = sum(1 for word in words if word.lower() in strong_verbs_list)
            
    return {
        "reading_time": reading_time_str,
        "reading_time_min": reading_time_min,
        "buzzword_count": buzzword_count,
        "action_verb_count": action_verb_count
    }
