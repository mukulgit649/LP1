# AI Role Fit Engine 🧠

> **"It doesn't just check if you wrote 'Python'; it checks if you have the context of a Python developer."**

The **AI Role Fit Engine** is a next-generation resume analyzer that goes beyond simple keyword matching. By leveraging **Google Gemini (GenAI)** and **Semantic Vector Embeddings**, it understands the *context* of your experience and evaluates how well you fit a specific job description.

![AI Role Fit Engine Screenshot](https://via.placeholder.com/800x400?text=AI+Role+Fit+Engine+Dashboard)

## 🚀 Why This Exists?
Traditional ATS (Applicant Tracking Systems) are broken. They look for exact keyword matches, often rejecting qualified candidates because they used "Software Engineering" instead of "Software Development."

**This engine is different.** It uses:
*   **Semantic Analysis:** Calculates a "Role Fit Score" based on meaning, not just words.
*   **Contextual Understanding:** Distinguishes between "I used Python once" and "I built a scalable backend in Python."
*   **Recruiter Persona:** Estimates reading time, buzzword density, and action verb usage to help you pass the 6-second recruiter scan.

## 🏗️ Architecture & Tech Stack

This project is built with a **Modern, Type-Safe, and AI-Native** stack designed for performance and scalability.

### **Frontend (Client-Side)**
*   **Framework:** [Next.js 15](https://nextjs.org/) (App Router, Server Components)
*   **Language:** TypeScript (Strict Mode)
*   **Styling:** Tailwind CSS v4 (Utility-first)
*   **UI Components:** Custom accessible components (Radix UI primitives)
*   **Visualization:** Recharts (D3-based responsive charts)
*   **State Management:** React Hooks (`useState`, `useEffect`)

### **Backend (Server-Side)**
*   **API Framework:** [FastAPI](https://fastapi.tiangolo.com/) (High-performance, Async Python)
*   **Validation:** Pydantic (Data validation & settings management)
*   **Runtime:** Python 3.11+ (Serverless compatible)

### **AI & NLP Engine**
*   **LLM Orchestration:** Google Gemini 2.0 Flash (Low latency, high reasoning capability)
*   **Vector Embeddings:** `sentence-transformers` (HuggingFace `all-MiniLM-L6-v2`) for semantic search.
*   **NLP Processing:** `spaCy` (`en_core_web_sm`) for Named Entity Recognition (NER) and Noun Chunking.
*   **PDF Parsing:** `pdfplumber` for high-fidelity text extraction.

### **Infrastructure**
*   **Hosting:** Vercel (Frontend & Backend as Serverless Functions)
*   **CI/CD:** GitHub Actions (Automated deployments)

## ✨ Key Features
1.  **Semantic Role Fit Score:** A 0-100% score indicating how well your resume matches the JD's intent.
2.  **Skill Gap Analysis:** Identifies missing hard/soft skills but filters out generic fluff.
3.  **Resume Heatmap:** Visually highlights which sentences in your resume strongly match the job description.
4.  **Recruiter Metrics:** Checks Reading Time (aiming for < 2.5 mins), Buzzword Overload, and Action Verb usage.
5.  **Privacy First:** Your API Key is used only for the session and never stored.

## 🏃‍♂️ How to Run Locally

### Prerequisites
*   Node.js 18+
*   Python 3.10+
*   Google Gemini API Key

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
# Server starts at http://localhost:8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
# App starts at http://localhost:3000
```

## 🚀 Deployment (Vercel)
This project is configured for a **Monorepo Deployment** on Vercel.
1.  Push code to GitHub.
2.  Import project into Vercel.
3.  Vercel will automatically detect `vercel.json` and deploy both Frontend and Backend as serverless functions.

## 🤝 Contributing
Open to PRs! If you have ideas for better prompting or new metrics, feel free to fork.

## 📄 License
MIT
