import spacy
from sentence_transformers import SentenceTransformer, util
import streamlit as st
import subprocess
import sys

# Load models with caching
@st.cache_resource
def load_spacy_model():
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Fallback if model isn't found
        print("Downloading spacy model...")
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        return spacy.load("en_core_web_sm")

@st.cache_resource
def load_sentence_transformer():
    try:
        return SentenceTransformer('all-MiniLM-L6-v2')
    except Exception as e:
        print(f"Error loading SentenceTransformer: {e}")
        return None

def calculate_role_fit_score(resume_text, jd_text):
    """
    Calculates the Role Fit Score using a stricter Semantic Coverage approach.
    We check how well the TOP requirements in the JD are covered by the resume.
    """
    model = load_sentence_transformer()
    nlp = load_spacy_model()
    
    if not resume_text or not jd_text or model is None:
        return 0.0

    # Split into sentences
    resume_doc = nlp(resume_text)
    jd_doc = nlp(jd_text)
    
    resume_sentences = [sent.text.strip() for sent in resume_doc.sents if len(sent.text.strip()) > 10]
    jd_sentences = [sent.text.strip() for sent in jd_doc.sents if len(sent.text.strip()) > 10]
    
    if not resume_sentences or not jd_sentences:
        return 0.0

    # Compute embeddings
    resume_embeddings = model.encode(resume_sentences, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_sentences, convert_to_tensor=True)

    # Compute cosine similarity matrix
    # Shape: (num_jd_sentences, num_resume_sentences)
    cosine_scores = util.cos_sim(jd_embeddings, resume_embeddings)
    
    # For each JD sentence, find the max similarity score in the resume
    max_scores_per_jd_sent, _ = cosine_scores.max(dim=1)
    
    # STRICTER SCORING LOGIC:
    # 1. Thresholding: Ignore weak matches (< 0.4) entirely.
    # 2. Top-K Average: Focus on the top 75% of JD sentences (ignore filler sentences).
    # 3. No artificial boosting.
    
    # Filter out very low scores (noise)
    relevant_scores = [score.item() for score in max_scores_per_jd_sent if score.item() > 0.35]
    
    if not relevant_scores:
        return 10.0 # Minimum score for effort
        
    # Calculate average of relevant matches
    avg_score = sum(relevant_scores) / len(jd_sentences) # Divide by TOTAL JD sentences to penalize missing parts
    
    # Scale: A raw cosine similarity of 0.8 is practically perfect.
    # Map 0.0 - 0.8 to 0 - 100
    final_score = (avg_score / 0.8) * 100
    
    return round(min(100, max(0, final_score)), 2)

def extract_nouns(text):
    """
    Extracts nouns and proper nouns from text using spaCy, filtering out common resume stop words.
    """
    nlp = load_spacy_model()
    doc = nlp(text)
    
    # Common words in resumes/JDs that are NOT skills
    resume_stop_words = {
        "experience", "role", "team", "project", "work", "skills", "years", "months", "time",
        "company", "responsibilities", "requirements", "degree", "university", "college",
        "candidate", "application", "opportunity", "business", "solutions", "services",
        "development", "management", "analysis", "data", "system", "support", "knowledge",
        "understanding", "proficiency", "ability", "track", "record", "hands", "familiarity",
        "expertise", "bachelor", "master", "phd", "job", "description", "summary", "objective",
        "education", "certification", "qualifications", "key", "tasks", "products", "designs",
        "scale", "engineer", "artificial", "intelligence", "domain", "source", "title", "junior",
        "senior", "lead", "manager", "intern", "internship", "students", "projects", "technologies"
    }
    
    nouns = set()
    for token in doc:
        if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and not token.is_punct:
            word = token.text.lower()
            if len(word) > 2 and word not in resume_stop_words:
                nouns.add(word)
                
    return nouns

def analyze_skill_gaps(resume_text, jd_text):
    """
    Identifies missing skills (nouns/proper nouns) from the JD that are not in the Resume.
    Returns a set of missing keywords.
    """
    if not resume_text or not jd_text:
        return set()

    jd_nouns = extract_nouns(jd_text)
    resume_nouns = extract_nouns(resume_text)

    # Find missing skills
    missing_skills = jd_nouns - resume_nouns
    
    return missing_skills

def get_sentence_scores(resume_text, jd_text):
    """
    Splits resume into sentences and calculates similarity with JD for each.
    Returns a list of (sentence, score) tuples.
    """
    model = load_sentence_transformer()
    nlp = load_spacy_model()
    
    if not resume_text or not jd_text or model is None:
        return []
        
    doc = nlp(resume_text)
    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
    
    jd_embedding = model.encode(jd_text, convert_to_tensor=True)
    
    sentence_scores = []
    for sent in sentences:
        sent_embedding = model.encode(sent, convert_to_tensor=True)
        similarity = util.cos_sim(sent_embedding, jd_embedding).item()
        sentence_scores.append((sent, similarity))
        
    return sentence_scores

def get_recruiter_metrics(resume_text):
    """
    Calculates reading time, buzzword count, and action verb count.
    """
    word_count = len(resume_text.split())
    # Reading time in minutes (Skimming speed ~250 wpm)
    reading_time_min = word_count / 250
    
    # Format reading time as "Xm Ys"
    minutes = int(reading_time_min)
    seconds = int((reading_time_min - minutes) * 60)
    reading_time_str = f"{minutes}m {seconds}s"
    
    buzzwords = ["synergy", "hardworking", "motivated", "team player", "detail-oriented", "proactive", "passionate", "driven"]
    
    buzzword_count = sum(1 for word in resume_text.lower().split() if word in buzzwords)
    
    # Action Verbs using spaCy
    nlp = load_spacy_model()
    doc = nlp(resume_text)
    
    # We look for verbs (VERB) in past tense (VBD) or present participle (VBG) which are often used in resumes
    # Also check for specific strong verbs if POS tagging misses them
    strong_verbs_list = {"led", "built", "engineered", "developed", "managed", "created", "designed", "implemented", "orchestrated", "spearheaded", "executed", "launched"}
    
    # Refined approach: Count unique action verbs found
    found_verbs = set()
    for token in doc:
        if (token.pos_ == "VERB" and token.tag_ in ["VBD", "VBN"]) or (token.text.lower() in strong_verbs_list):
            found_verbs.add(token.text.lower())
            
    action_verb_count = len(found_verbs)
            
    return {
        "reading_time": reading_time_str,
        "reading_time_min": reading_time_min, # Keep float for logic checks
        "buzzword_count": buzzword_count,
        "action_verb_count": action_verb_count
    }
