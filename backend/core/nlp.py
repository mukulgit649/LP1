import spacy
from sentence_transformers import SentenceTransformer, util
import os

# Global variables for caching models
# In serverless, these might reload on cold starts, which is acceptable for this scale.
_nlp_model = None
_st_model = None

def load_spacy_model():
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            import sys
            subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            _nlp_model = spacy.load("en_core_web_sm")
    return _nlp_model

def load_sentence_transformer():
    global _st_model
    if _st_model is None:
        try:
            # Load a smaller model for faster serverless startup if possible
            _st_model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            print(f"Error loading SentenceTransformer: {e}")
            return None
    return _st_model

def calculate_role_fit_score(resume_text, jd_text):
    model = load_sentence_transformer()
    nlp = load_spacy_model()
    
    if not resume_text or not jd_text or model is None:
        return 0.0

    resume_doc = nlp(resume_text)
    jd_doc = nlp(jd_text)
    
    resume_sentences = [sent.text.strip() for sent in resume_doc.sents if len(sent.text.strip()) > 10]
    jd_sentences = [sent.text.strip() for sent in jd_doc.sents if len(sent.text.strip()) > 10]
    
    if not resume_sentences or not jd_sentences:
        return 0.0

    resume_embeddings = model.encode(resume_sentences, convert_to_tensor=True)
    jd_embeddings = model.encode(jd_sentences, convert_to_tensor=True)

    cosine_scores = util.cos_sim(jd_embeddings, resume_embeddings)
    max_scores_per_jd_sent, _ = cosine_scores.max(dim=1)
    
    relevant_scores = [score.item() for score in max_scores_per_jd_sent if score.item() > 0.35]
    
    if not relevant_scores:
        return 10.0
        
    avg_score = sum(relevant_scores) / len(jd_sentences)
    final_score = (avg_score / 0.8) * 100
    
    return round(min(100, max(0, final_score)), 2)

def extract_nouns(text):
    nlp = load_spacy_model()
    doc = nlp(text)
    
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
    if not resume_text or not jd_text:
        return set()
    jd_nouns = extract_nouns(jd_text)
    resume_nouns = extract_nouns(resume_text)
    return jd_nouns - resume_nouns

def get_sentence_scores(resume_text, jd_text):
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
    word_count = len(resume_text.split())
    reading_time_min = word_count / 250
    
    minutes = int(reading_time_min)
    seconds = int((reading_time_min - minutes) * 60)
    reading_time_str = f"{minutes}m {seconds}s"
    
    buzzwords = ["synergy", "hardworking", "motivated", "team player", "detail-oriented", "proactive", "passionate", "driven"]
    buzzword_count = sum(1 for word in resume_text.lower().split() if word in buzzwords)
    
    nlp = load_spacy_model()
    doc = nlp(resume_text)
    
    strong_verbs_list = {"led", "built", "engineered", "developed", "managed", "created", "designed", "implemented", "orchestrated", "spearheaded", "executed", "launched"}
    
    found_verbs = set()
    for token in doc:
        if (token.pos_ == "VERB" and token.tag_ in ["VBD", "VBN"]) or (token.text.lower() in strong_verbs_list):
            found_verbs.add(token.text.lower())
            
    action_verb_count = len(found_verbs)
            
    return {
        "reading_time": reading_time_str,
        "reading_time_min": reading_time_min,
        "buzzword_count": buzzword_count,
        "action_verb_count": action_verb_count
    }
