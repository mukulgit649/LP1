
import sys
import os

print("Testing imports...")
try:
    import spacy
    print("spacy imported")
except ImportError as e:
    print(f"Failed to import spacy: {e}")

try:
    from sentence_transformers import SentenceTransformer, util
    print("sentence_transformers imported")
except ImportError as e:
    print(f"Failed to import sentence_transformers: {e}")

try:
    import google.generativeai as genai
    print("google.generativeai imported")
except ImportError as e:
    print(f"Failed to import google.generativeai: {e}")

print("\nTesting NLP Engine...")
try:
    from nlp_engine import calculate_role_fit_score, analyze_skill_gaps
    print("nlp_engine imported")
    
    resume = "I am a software engineer with experience in Python and SQL."
    jd = "We need a software engineer who knows Python, SQL, and Docker."
    
    print("Calculating score...")
    score = calculate_role_fit_score(resume, jd)
    print(f"Score: {score}")
    
    print("Analyzing gaps...")
    gaps = analyze_skill_gaps(resume, jd)
    print(f"Gaps: {gaps}")
    
except Exception as e:
    print(f"NLP Engine Test Failed: {e}")
    import traceback
    traceback.print_exc()

print("\nDone.")
