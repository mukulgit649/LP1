import streamlit as st
from utils import extract_text_from_pdf
from nlp_engine import calculate_role_fit_score, analyze_skill_gaps, get_sentence_scores, get_recruiter_metrics
from genai_engine import generate_achievement, get_sub_scores, generate_project_idea
import plotly.graph_objects as go
from annotated_text import annotated_text

st.set_page_config(page_title="AI Resume Fixer", layout="wide")

st.title("AI Resume Fixer & Career Coach")
st.markdown("Optimize your resume for the Role Fit Score, not just the ATS.")

# Sidebar for API Key
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your Gemini API Key", type="password")
    
    # Model Selection
    # User confirmed gemini-2.5-flash-lite exists via screenshot
    model_options = ["gemini-2.0-flash-exp", "gemini-2.5-flash-lite"]
    selected_model = st.selectbox("Select Gemini Model", model_options, index=0)
    
    st.markdown("[Get your API Key here](https://aistudio.google.com/app/apikey)")

# Main Interface
col1, col2 = st.columns(2)

with col1:
    st.subheader("Upload Resume")
    uploaded_file = st.file_uploader("Upload your Resume (PDF)", type=["pdf"])

with col2:
    st.subheader("Job Description")
    jd_text = st.text_area("Paste the Job Description here", height=300)

# Analyze Button Section
if st.button("Analyze Resume"):
    if not uploaded_file:
        st.error("Please upload a resume (PDF).")
    elif not jd_text:
        st.error("Please paste the Job Description.")
    else:
        with st.spinner("Analyzing..."):
            try:
                # Extract text
                resume_text = extract_text_from_pdf(uploaded_file)
                
                if resume_text:
                    # Show Extracted Text (for verification)
                    with st.expander("View Extracted Resume Text"):
                        st.text(resume_text[:1000] + "..." if len(resume_text) > 1000 else resume_text)
                    
                    # Warning for short JD
                    if len(jd_text.split()) < 50:
                        st.warning("⚠️ Your Job Description is very short. For the best Role Fit Score, paste the FULL job description (responsibilities, requirements, etc.).")

                    # Role Fit Score
                    score = calculate_role_fit_score(resume_text, jd_text)
                    
                    # Sub-Scores (Gemini)
                    sub_scores = get_sub_scores(resume_text, jd_text, api_key, selected_model)
                    
                    # Skill Gap Analysis
                    missing_skills = analyze_skill_gaps(resume_text, jd_text)
                    
                    # Recruiter Metrics
                    recruiter_metrics = get_recruiter_metrics(resume_text)
                    
                    # Heatmap Data
                    sentence_scores = get_sentence_scores(resume_text, jd_text)
                    
                    # Display Results
                    st.divider()
                    st.header("Analysis Results")
                    
                    # Top Section: Score & Radar Chart
                    col_score, col_radar = st.columns([1, 2])
                    
                    with col_score:
                        st.metric(label="Role Fit Score", value=f"{score}%")
                        if score >= 80:
                            st.success("Great Match!")
                        elif score >= 50:
                            st.warning("Good start, but needs improvement.")
                        else:
                            st.error("Low match. Significant tailoring needed.")
                            
                        st.subheader("Recruiter Persona")
                        
                        # Reading Time
                        rt_val = recruiter_metrics['reading_time_min']
                        rt_str = recruiter_metrics['reading_time']
                        st.write(f"**Reading Time:** {rt_str}")
                        if rt_val > 2:
                            st.warning("⚠️ Resume is too long. Aim for < 2 mins.")
                        else:
                            st.success("✅ Good length.")
                        
                        # Buzzwords
                        bw_count = recruiter_metrics['buzzword_count']
                        st.write(f"**Buzzwords:** {bw_count}")
                        if bw_count == 0:
                            st.success("Great! No fluff detected.")
                        elif bw_count <= 5:
                            st.info("Good balance.")
                        else:
                            st.warning("⚠️ Too much fluff.")
                            
                        # Action Verbs
                        av_count = recruiter_metrics['action_verb_count']
                        st.write(f"**Action Verbs:** {av_count}")
                        if av_count < 5:
                            st.warning("Use more strong action verbs (e.g., Led, Built).")
                        else:
                            st.success("Strong use of action verbs!")
                    
                    with col_radar:
                        st.subheader("Skill Radar")
                        categories = list(sub_scores.keys())
                        values = list(sub_scores.values())
                        
                        fig = go.Figure(data=go.Scatterpolar(
                            r=values,
                            theta=categories,
                            fill='toself'
                        ))
                        fig.update_layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100]
                                )),
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    st.divider()
                    
                    # Missing Skills with Chips
                    st.subheader("Missing Skills")
                    if missing_skills:
                        st.write("Click to see project ideas:")
                        cols = st.columns(4)
                        for i, skill in enumerate(missing_skills):
                            with cols[i % 4]:
                                if st.button(skill, key=f"skill_{i}"):
                                    idea = generate_project_idea(skill, api_key, selected_model)
                                    st.info(f"**Project Idea:** {idea}")
                    else:
                        st.success("✅ No critical skills missing! You are a strong match.")
                        
                    st.divider()
                    
                    # Resume Heatmap
                    st.subheader("Resume Heatmap")
                    st.write("Green = Strong Match, Red = Weak Match")
                    
                    heatmap_items = []
                    for sent, sim in sentence_scores:
                        if sim > 0.5:
                            heatmap_items.append((sent, "Strong", "#8fce00"))
                        elif sim > 0.3:
                            heatmap_items.append((sent, "Medium", "#ffe770"))
                        else:
                            heatmap_items.append(sent + " ") # No highlight for weak, just text
                            
                    annotated_text(*heatmap_items)
                    
                else:
                    st.error("Could not extract text from the uploaded PDF.")
            except Exception as e:
                st.error(f"An error occurred during analysis: {e}")
                import traceback
                traceback.print_exc()

st.divider()

# Achievement Generator Section
st.header("Achievement Generator")
st.markdown("Turn your basic bullet points into impressive achievements using the STAR method.")

job_title = st.text_input("Target Job Title", value="Software Engineer")
bullet_point = st.text_area("Paste a bullet point from your resume", placeholder="e.g. Managed a team of 5 developers.")

if st.button("Enhance Bullet Point"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar.")
    elif not bullet_point:
        st.warning("Please enter a bullet point to enhance.")
    else:
        with st.spinner("Generating..."):
            enhanced_text = generate_achievement(bullet_point, job_title, api_key, selected_model)
            st.subheader("Enhanced Version:")
            st.info(enhanced_text)
