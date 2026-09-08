# ⛏️ FutureMining — GATE Mining Engineering Platform

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://futuremining.streamlit.app/)
[![API Status](https://img.shields.io/badge/Backend-FastAPI-009688.svg?logo=fastapi&logoColor=white)](https://futuremining-1.onrender.com/health)
[![Database](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E.svg?logo=supabase&logoColor=white)](https://supabase.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Machine Learning](https://img.shields.io/badge/ML-NLP%20%2B%20Ridge%20Regression-orange.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary%20%2F%20All%20Rights%20Reserved-red.svg)](LICENSE.md)

> **FutureMining** is a full-stack, gamified learning and exam preparation platform built specifically for **GATE Mining Engineering** aspirants. It combines an interactive, high-stakes game-show format (*Kaun Banega Crorepati* style) with rigorous official GATE-pattern timed mock tests, dynamic analytics, and machine learning difficulty calibration.

---

## 🌟 Key Features

### 🎮 1. The Knowledge Challenge (KBC Mode)
- **15 Progressive Difficulty Tiers**: Questions scale from ₹1,000 up to ₹1,00,00,000 (1 Crore), perfectly aligned with our 15-level NLP difficulty model.
- **Milestone Safe Havens**: Guaranteed prize checkpoints at Level 5 (₹10,000) and Level 10 (₹3,20,000).
- **Interactive Lifelines**:
  - **50:50**: Eliminates two incorrect options.
  - **Flip / Swap Question**: Swaps the current question with a fresh server-verified question of the exact same difficulty level.
  - **Ask the Audience / AI Expert**: Generates intelligent probabilistic distributions weighted by question complexity.
  - **Double Dip**: Grants two attempts to lock in the correct answer.
- **Procedural Game-Show Sound Engine**: Synthesizes custom harmonic audio cues (clock ticks, tension hums, lock chimes, win fanfares) directly in-memory using pure Python with zero heavy audio file dependencies.
- **Rich LaTeX Rendering**: High-fidelity mathematical and chemical notation for complex mining formulas, matrices, and units.

---

### 📝 2. ExamGoal Practice & Timed Mock Tests
- **Authentic GATE Pattern**: Full-scale simulation adhering to official GATE marking (+1.0 Mark for correct answers, -0.33 negative marking for incorrect answers).
- **Interactive Question Palette**: Color-coded tracking for *Answered*, *Not Answered*, *Marked for Review*, and *Not Visited*.
- **Topic-Wise Practice**: Drill into dedicated mining modules including *Mine Ventilation, Opencast Mining, Rock Mechanics, Mine Legislation, Mining Machinery, and Engineering Mathematics*.
- **Crowdsourced Review Queue**: Users can flag ambiguous or errant questions in real-time, instantly persisting reports for administrative quality moderation.

---

### 🧠 3. Machine Learning Difficulty Pipeline
Questions are calibrated using a custom **NLP & Linguistic Feature Ensemble**:
- **Domain Lexicon Analysis**: Scans for 100+ mining engineering keywords (*longwall, room and pillar, UCS, powder factor, semivariogram, kriging, Atkinson's friction law*).
- **Readability & Complexity Metrics**: Incorporates Gunning Fog index, Flesch-Kincaid grade level, syllable counts, mathematical operator frequency, and character Shannon entropy.
- **TF-IDF + Ridge Regression**: Predicts continuous difficulty scores using combined word and character n-grams, subsequently mapped into **15 calibrated quantile tiers**.

---

### 🛡️ 4. Multi-Tier Resilient Architecture
Built for continuous availability with automatic three-tier fallback routing:
1. **Tier 1 (FastAPI REST Backend)**: Primary high-speed API hosted on Render with automated cold-start wake-up pings.
2. **Tier 2 (Direct Database Fallback)**: Transparent failover to direct pooled PostgreSQL connections (Supabase) via SQLAlchemy and `pg8000`.
3. **Tier 3 (Local Offline Mode)**: Bundled verified CSV dataset (`GATE_800_Questions_Classified.csv`) ensuring gameplay even without internet or cloud availability.

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    User["👤 Aspirant / User"] -->|"HTTPS"| Streamlit["💻 Streamlit Frontend (app.py)"]
    
    subgraph FrontendLayer["Frontend Modules"]
        AudioEngine["🎵 In-Memory Audio Synthesizer"]
        ExamGoal["📝 ExamGoal Practice & Mock Test"]
        LaTeXEngine["📐 LaTeX Math Engine"]
    end

    Streamlit --> AudioEngine
    Streamlit --> ExamGoal
    Streamlit --> LaTeXEngine

    Streamlit -->|"api_client.py"| Router{"🛡️ 3-Tier Fallback Router"}

    subgraph BackendLayer["Backend & Storage"]
        FastAPI["⚡ FastAPI Backend (Render)"]
        Supabase[("🗄️ Supabase PostgreSQL")]
        CSV[("📁 Bundled CSV Dataset")]
    end

    Router -->|"1. REST API"| FastAPI
    Router -->|"2. Direct SQL"| Supabase
    Router -->|"3. Offline Mode"| CSV

    FastAPI -->|"SQLAlchemy 2.0"| Supabase

    subgraph MLLayer["Data & ML Engineering"]
        RawData["📄 Raw GATE Questions"] --> NLP["🔍 NLP & Complexity Scoring"]
        NLP --> Ridge["📈 Ridge Regression Model"]
        Ridge --> ClassifiedData["🎯 15-Tier Classified Bank"]
    end
```

---

## 📂 Project Structure

```bash
FutureMining/
├── app.py                     # Main Streamlit application & KBC game engine
├── api_client.py              # 3-tier resilient client (FastAPI -> DB -> CSV)
├── examgoal.py                # ExamGoal practice mode, mock test & analytics
├── requirements.txt           # Frontend dependencies
├── Procfile                   # Process file for cloud deployment
├── render.yaml                # Render Infrastructure-as-Code blueprint
│
├── backend/                   # FastAPI Backend Service
│   ├── main.py                # API routing, authentication & game logic
│   ├── models.py              # SQLAlchemy database ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── database.py            # PostgreSQL connection pool configuration
│   ├── requirements.txt       # Backend dependencies
│   └── Dockerfile             # Container configuration
│
├── data/                      # Dataset & Moderation Queue
│   ├── GATE_800_Questions_Classified.csv   # 800 ML-classified questions (Tiers 1-15)
│   ├── GATE_800_Questions_Raw.csv          # Raw questions before classification
│   └── review_queue.json                   # Local fallback moderation queue
│
├── models/                    # Trained Machine Learning Models
│   ├── gate_difficulty_model.pkl
│   └── gate_nlp_model.pkl
│
└── util/                      # ML & Data Pipeline Scripts
    ├── classification_pipeline.py  # NLP feature engineering & Ridge training
    ├── generate_dataset.py         # LLM-guided syllabus question generation
    ├── integrity_check.py          # Automated database integrity audit
    └── test_env.py                 # Environment verification utility
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git
- (Optional) PostgreSQL database instance or free [Supabase](https://supabase.com) project

### 1. Clone the Repository
```bash
git clone https://github.com/tysonfgh/FutureMining.git
cd FutureMining
```

### 2. Frontend Setup (Streamlit)
```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the Streamlit application
streamlit run app.py
```

### 3. Backend Setup (FastAPI - Optional for local development)
```bash
# In a separate terminal
cd backend
pip install -r requirements.txt

# Configure your environment variables (.env)
# DATABASE_URL=postgresql+pg8000://<user>:<password>@<host>:<port>/postgres

# Launch FastAPI server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🔌 API Endpoints Reference

The FastAPI backend exposes comprehensive RESTful services documented interactively at `/docs` (Swagger UI):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Service health status and live question count |
| `POST` | `/api/auth/register` | Register user account with salted password hashing |
| `POST` | `/api/auth/login` | Authenticate user and issue session profile |
| `GET` | `/api/questions` | Query questions filtered by subject, topic, or difficulty |
| `GET` | `/api/topics` | Retrieve all mining topics and active question counts |
| `GET` | `/api/game/ladder` | Fetch 15-question progressive game show ladder |
| `GET` | `/api/game/swap` | Lifeline: Securely swap a question for a given level |
| `POST` | `/api/game/verify` | Server-side secure answer verification |
| `POST` | `/api/progress/attempt` | Log question attempt for performance analytics |
| `POST` | `/api/progress/test-session` | Save complete timed mock test session results |
| `GET` | `/api/progress/{user_id}/summary` | Retrieve comprehensive user performance analytics |
| `POST` | `/api/reviews/flag` | Flag a question for administrative review |

---

## 👨‍🏫 Project Mentorship & Guidance

Heartfelt thanks and sincere gratitude to our esteemed mentor and guide:

### **Dr. LINGAMPALLY SAI VINAY**
*Associate Professor, Department of Mining Engineering*  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/dr-lingampally-sai-vinay-110638118/)

> *"Project Conception, Supervision, Technical Guidance & Continuous Motivation"*
>
> We extend our deepest gratitude to our mentor, **Dr. Lingampally Sai Vinay**, for conceptualizing the foundational idea of transforming GATE Mining preparation into an interactive, gamified platform, and for his supervision, domain guidance, and encouragement throughout every phase of conception, system design, and execution. His technical insights in mining engineering, constructive feedback, and academic mentorship were instrumental in navigating complex domain challenges and bringing **FutureMining** to reality.

---

## 👥 The Team & Key Contributions

FutureMining is the result of close multidisciplinary teamwork, combining game design, NLP machine learning, database engineering, and distributed backend systems:

| Team Member | Domain & Role | Key Architectural & Engineering Contributions | Profile |
| :--- | :--- | :--- | :--- |
| **Sayandeep Guin** | **Core Product, Game Logic & NLP Engineering** | • Architected the end-to-end technical foundation, game architecture, and interactive state management<br>• Designed the Streamlit UI/UX, responsive styling, and dynamic KBC game show engine<br>• Engineered the OCR and Regex parsing pipeline to extract and validate GATE Mining PDFs into structured CSV datasets<br>• Co-developed the NLP difficulty pipeline (TF-IDF, Gunning Fog index, Ridge Regression) calibrating mining subjects into a 15-tier difficulty matrix | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/sayandeep-guin-041576356/) |
| **Sabuj Kishore Mondal** | **Core Product, Game Logic & NLP Engineering** | • Co-architected the technical foundation, interactive UI components, and state synchronization<br>• Built the ExamGoal-style exam simulation engine, timed mock tests, and color-coded status palette<br>• Engineered the procedural in-memory audio synthesizer generating harmonic audio cues with zero external audio assets<br>• Co-developed the PDF-to-CSV OCR/Regex pipeline and NLP feature engineering pipeline for difficulty classification | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/sabuj-m-392855381/) |
| **Sagar Pal** | **Database Architecture** | • Designed and modeled the relational database schema for questions, categories, attempts, and test sessions<br>• Architected Supabase PostgreSQL clustering, connection pooling, and live cloud synchronization<br>• Managed data migrations and built automated database integrity audit scripts (`integrity_check.py`) | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/sagar-pal-681912383/) |
| **Arpita Sengupta** | **Backend Architecture & APIs** | • Engineered high-performance FastAPI REST services with Pydantic validation and SQLAlchemy ORM<br>• Designed and implemented the resilient 3-tier automatic failover routing (FastAPI ➡️ Supabase Direct ➡️ Offline Bundled CSV)<br>• Developed salted authentication, session management, review moderation endpoints, and cloud deployment on Render | [![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-blue?logo=linkedin)](https://www.linkedin.com/in/arpita-sengupta-4085913ab/) |

---

## 📜 Intellectual Property & Commercialization License

Copyright © 2026 FutureMining Project Team & Dr. Lingampally Sai Vinay. All rights reserved.

> [!IMPORTANT]
> **Commercialization & Mobile Application Notice**  
> This project, its source code, architecture, NLP difficulty pipelines, and question datasets are **proprietary and confidential**. FutureMining is slated for commercialization and dedicated mobile application release under the supervision of **Dr. Lingampally Sai Vinay** and the core development team.

- **All Commercial & Mobile Rights Reserved**: Unauthorized reproduction, redistribution, commercial deployment, sublicensing, reverse engineering, or publishing on mobile app stores (Google Play Store, Apple App Store, etc.) or web SaaS platforms without prior explicit written permission from the copyright owners is strictly prohibited.
- **Academic & Portfolio Evaluation**: Inspection and non-commercial evaluation of this repository is permitted solely for academic review and portfolio assessment.

For full legal terms and conditions, please consult [LICENSE.md](LICENSE.md).
