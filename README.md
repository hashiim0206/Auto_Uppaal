# Auto Uppaal – LLM-Powered UPPAAL Model Generator

This project automatically generates UPPAAL XML models and verifies them using **LLMs + UPPAAL’s verifyta engine**.  
The system allows users to describe a timed automaton in natural language and instantly obtain:

- A valid UPPAAL XML model
- Verification results for given queries
- A clean frontend interface
- A Python backend using Groq API + UPPAAL model checker

---

## ⚙️ Backend Overview

- Uses Flask/FastAPI to handle `/generate` endpoint  
- Sends structured prompts to Groq API (via Mixtral or Llama models) 
- Generates UPPAAL XML using a fixed XML skeleton  
- Runs the XML through verifyta to compute model-checking results  
- Sends final XML + verification output back to the frontend

---

## 🎨 Frontend Overview

- Built with **React + Vite**
- User enters:
  - UPPAAL model description
  - Queries (list format)
- Displays:
  - Model XML preview
  - Verification results
- Clean UI for demo presentations

---

## 🧠 Algorithms Used (Brief)

- **Instruction prompting**: Converts natural-language descriptions into structured XML.
- **XML-repair heuristics**: Ensures missing attributes or malformed tags are corrected.
- **Model-checker parsing**: Extracts errors/warnings from verifyta output.
- **Schema-guided LLM generation**: Forces response to match the UPPAAL XML template.

---

## 📚 Tech Stack

- **Backend:** Python, Groq API, UPPAAL Verifyta
- **Frontend:** React + Vite
- **LLM:** Groq (Llama 3.3)
- **Tools:** XML parser, subprocess management, prompt templates

---

## 🏁 How to Run

### Backend
- cd backend
- pip install -r requirements.txt
- python src/api.py

### Frontend
- cd frontend
- npm install
- npm run dev

---

## 📌 Future Improvements

- Add RAG for knowledge-grounded UPPAAL rules
- Better chain-of-thought restriction
- Multi-template model generation

---

## 👤 Author
- Hashiim Mohammed Sheriff Sathick Batcha  
- Florida Institute of Technology

---

## 👤 Professor
- Siddhartha Bhattacharyya
- Florida Institute of Technology
