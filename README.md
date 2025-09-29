# MindCare+

MindCare+ is a prototype digital mental wellness platform developed for academic purposes.
It combines **AI-driven mental health support** with **professional counseling access**, designed to address common challenges in Brunei such as stigma, accessibility, and shortage of professionals.

---

## ✨ Features (MVP)

* **User Authentication** – Registration, login, JWT-based sessions
* **AI Chatbot** – Llama3-powered mental health conversations with context
* **Check-ins** – Users can log mood, stress levels, and notes
* **Chat Sessions** – Persistent multi-session conversations linked to check-ins
* **Therapist Booking** – Counselors with availability slots, booking system (premium users)
* **Billing Upgrade (MVP)** – Freemium to premium upgrade flow (mocked)
* **Resources** – Curated mental health resources
* **Analytics (Basic)** – Tracks check-ins, sessions, bookings for user insights
* **Health Check** – `/healthz` endpoint for deployment readiness

---

## 🏗️ Tech Stack

* **Backend**: FastAPI, SQLAlchemy, SQLite (local) / MySQL (prod), JWT Auth
* **Frontend**: Vue.js
* **AI Integration**: Ollama (Llama3 model)
* **Other**: Docker-ready, CORS enabled, seed scripts for counselors & slots

---

## 📂 Project Structure

```
MINDCARE-PLUS/
│
├── backend/          # FastAPI backend
│   ├── main.py       # Core routes & API logic
│   ├── models.py     # Database models
│   ├── schema.py     # Pydantic schemas
│   ├── auth.py       # JWT auth & password hashing
│   ├── database.py   # DB engine & session
│   ├── seed_booking.py / seed.py
│   ├── requirements.txt
│   └── ...
│
└── frontend/         # Vue.js frontend
    ├── src/
    ├── public/
    ├── package.json
    └── ...
```

---

## 🚀 Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run serve
```

---

## 🔒 Notes

* `.env` and `mindcare.db` are excluded from version control for security.
* This project is **for academic demonstration only** and not intended for production use without further development.
