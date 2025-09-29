import os
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import Base, engine, get_db
from models import (
    User, AICheckIn, ChatMessage, Resource, ChatRole, ChatSession,
    Counselor, AvailabilitySlot, Booking, BookingStatus,
)
from schema import RegisterIn, LoginIn, ChatTurn, ChatIn, ChatOut, CheckInIn
from auth import hash_password, verify_password, make_jwt, decode_jwt

# -------------------- App bootstrap --------------------

# Load .env early so env vars (JWT secret, model, CORS, etc.) are present
load_dotenv()

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load context + model name (path-safe)
MODEL = os.getenv("OLLAMA_MODEL", "llama3")
CONTEXT_PATH = Path(__file__).parent / "mindcare_context.txt"
try:
    MINDCARE_CONTEXT = CONTEXT_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"[context] {CONTEXT_PATH} not found; using empty context")
    MINDCARE_CONTEXT = ""

# -------------------- Helpers --------------------

def run_ollama(model: str, prompt: str, timeout_sec: int = 120) -> str:
    """Run `ollama run <model>` and return stdout (trimmed) or '' on error.
    Includes basic logging and a PATH sanity check.
    """
    if not shutil.which("ollama"):
        print("[ollama] binary not found on PATH")
        return ""
    try:
        res = subprocess.run(
            ["ollama", "run", model],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=timeout_sec,
        )
        print(
            "[ollama] rc:", res.returncode,
            "| stdout:", (res.stdout or "").strip()[:120],
            "| stderr:", (res.stderr or "").strip()[:120],
        )
        if res.returncode != 0:
            return ""
        return (res.stdout or "").strip()
    except subprocess.TimeoutExpired:
        print(f"[ollama] timeout after {timeout_sec}s")
        return ""
    except Exception as e:
        print("[ollama] unexpected error:", e)
        return ""


def utcnow() -> datetime:
    return datetime.utcnow()

# -------------------- Auth helpers --------------------

def auth_user(authorization: str = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.split(" ", 1)[1]
    try:
        payload = decode_jwt(token)
    except Exception as e:
        # TEMP logging to diagnose token issues
        print("[auth] decode error:", repr(e))
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    # PATCH: ensure we use int user_id after decoding (and accept str sub)
    try:
        user_id = int(payload["sub"])  # <-- normalize to int for DB lookup
    except (KeyError, TypeError, ValueError) as e:
        print("[auth] bad token sub:", e)
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == user_id, User.deleted == False).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_premium(u: User = Depends(auth_user)) -> User:
    """Dependency: allow only premium users; returns HTTP 402 for upsell handling."""
    if getattr(u, "plan", "free") != "premium":
        raise HTTPException(status_code=402, detail="Premium required")
    return u

# -------------------- Routes: Auth --------------------

@app.post("/auth/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    exists = db.query(User).filter(User.email == body.email).first()
    if exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    token = make_jwt(str(user.id), user.email)  # PATCH: cast sub to str
    return {"token": token, "user": {"id": user.id, "email": user.email, "plan": getattr(user, 'plan', 'free')}}


@app.post("/auth/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email, User.deleted == False).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = make_jwt(str(user.id), user.email)  # PATCH: cast sub to str
    return {"token": token, "user": {"id": user.id, "email": user.email, "plan": getattr(user, 'plan', 'free')}}


@app.get("/me")
def me(u: User = Depends(auth_user)):
    return {"id": u.id, "email": u.email, "plan": getattr(u, 'plan', 'free')}

# -------------------- Routes: Billing / Upgrade (MVP) --------------------

@app.post("/billing/upgrade")
def billing_upgrade(body: dict, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    """MVP upgrade endpoint. Accepts {"code": "..."}. Any non-empty code upgrades the user.
    Replace later with a real payment flow/webhook."""
    code = (body or {}).get("code", "").strip()
    if not code:
        raise HTTPException(status_code=400, detail="Missing code")
    u.plan = "premium"
    db.add(u); db.commit(); db.refresh(u)
    return {"ok": True, "plan": u.plan}

# -------------------- Chat prompt builder --------------------

def build_prompt(message: str, history: list[ChatTurn] | None = None) -> str:
    hist = ""
    for turn in (history or []):
        who = "User" if turn.role == "user" else "AI"
        hist += f"{who}: {turn.content}\n"
    return f"""
You are MindCare+, an AI chatbot for mental health in Brunei.
Use the following knowledge when answering. If unrelated, gently redirect to mental health support.

Knowledge:
{MINDCARE_CONTEXT}

Conversation so far:
{hist}
User: {message}
AI:
"""

# -------------------- Routes: Public Chat (stateless demo) --------------------

@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, db: Session = Depends(get_db)):
    prompt = build_prompt(body.message, body.history)
    reply = run_ollama(MODEL, prompt)
    if not reply or reply.strip() in {".", "...", "…"}:
        reply = (
            "I couldn’t generate a reply right now. If this keeps happening, "
            f"please check that the Ollama model ‘{MODEL}’ is installed and reachable."
        )
    return {"reply": reply}

# -------------------- Routes: Chat Sessions (multi-session, persisted) --------------------

@app.post("/chat/sessions")
def create_session(body: dict, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    """
    Create a new chat session. Optionally link to a check-in by id.
    Freemium rule: free users can have 1 session max; premium users unlimited (for now).
    body: {"title"?: str, "checkin_id"?: int}
    """
    title = (body or {}).get("title") if body else None
    checkin_id = (body or {}).get("checkin_id") if body else None

    # Enforce freemium limit
    if getattr(u, "plan", "free") != "premium":
        existing = db.query(ChatSession).filter(ChatSession.user_id == u.id).count()
        if existing >= 1:
            raise HTTPException(status_code=402, detail="Premium required for multiple sessions")

    mood_at_start = None
    stress_at_start = None

    if checkin_id:
        chk = db.query(AICheckIn).filter(
            AICheckIn.id == checkin_id, AICheckIn.user_id == u.id
        ).first()
        if not chk:
            raise HTTPException(status_code=404, detail="Check-in not found")
        mood_at_start = chk.mood
        stress_at_start = chk.stress_level

    sess = ChatSession(
        user_id=u.id,
        title=(title or (mood_at_start or "New session")),
        checkin_id=checkin_id,
        mood_at_start=mood_at_start,
        stress_at_start=stress_at_start,
    )
    db.add(sess); db.commit(); db.refresh(sess)
    return {"id": sess.id, "title": sess.title, "checkin_id": sess.checkin_id}


@app.get("/chat/sessions")
def list_sessions(u: User = Depends(auth_user), db: Session = Depends(get_db)):
    rows = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == u.id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "created_at": r.created_at.isoformat(),
            "checkin_id": r.checkin_id,
            "mood_at_start": r.mood_at_start,
            "stress_at_start": r.stress_at_start,
        }
        for r in rows
    ]


@app.patch("/chat/sessions/{sid}")
def rename_session(sid: int, body: dict, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.id == sid, ChatSession.user_id == u.id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    new_title = (body or {}).get("title", "").strip()
    if new_title:
        sess.title = new_title
        db.add(sess); db.commit()
    return {"ok": True}


@app.delete("/chat/sessions/{sid}")
def delete_session(sid: int, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.id == sid, ChatSession.user_id == u.id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    # delete messages for this session (also covered by cascade if configured)
    db.query(ChatMessage).filter(ChatMessage.session_id == sess.id).delete()
    db.delete(sess); db.commit()
    return {"ok": True}


@app.get("/chat/sessions/{sid}/messages")
def list_messages(sid: int, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.id == sid, ChatSession.user_id == u.id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == sid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    return [
        {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
        for m in msgs
    ]


@app.post("/chat/sessions/{sid}/send", response_model=ChatOut)
def send_in_session(sid: int, body: ChatIn, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    sess = db.query(ChatSession).filter(ChatSession.id == sid, ChatSession.user_id == u.id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    # Build history from DB
    prev_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == sid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in prev_msgs]

    prompt = build_prompt(body.message, history)
    reply = run_ollama(MODEL, prompt) or "I couldn’t generate a reply right now."

    # Persist both turns
    db.add(ChatMessage(user_id=u.id, session_id=sid, role=ChatRole.user, content=body.message))
    db.add(ChatMessage(user_id=u.id, session_id=sid, role=ChatRole.assistant, content=reply))
    db.commit()

    return {"reply": reply}

# -------------------- Routes: Therapist Booking --------------------

@app.get("/counselors")
def counselors_list(db: Session = Depends(get_db)):
    rows = db.query(Counselor).filter(Counselor.is_active == True).order_by(Counselor.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "full_name": r.full_name,
            "bio": r.bio,
            "specialties": (r.specialties or ""),
            "price_cents": r.price_cents,
            "currency": r.currency,
        }
        for r in rows
    ]


@app.get("/counselors/{cid}/slots")
def counselor_slots(cid: int, days: int = 14, db: Session = Depends(get_db)):
    if days < 1 or days > 60:
        days = 14
    now = utcnow()
    end = now + timedelta(days=days)
    c = db.query(Counselor).filter(Counselor.id == cid, Counselor.is_active == True).first()
    if not c:
        raise HTTPException(404, "Counselor not found")
    slots = (
        db.query(AvailabilitySlot)
        .filter(AvailabilitySlot.counselor_id == cid,
                AvailabilitySlot.start_time >= now,
                AvailabilitySlot.start_time <= end,
                AvailabilitySlot.is_booked == False)
        .order_by(AvailabilitySlot.start_time.asc())
        .all()
    )
    return [
        {
            "id": s.id,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
        }
        for s in slots
    ]


@app.post("/bookings")
def create_booking(body: dict, u: User = Depends(require_premium), db: Session = Depends(get_db)):
    """Create a booking for a counselor slot. Premium required (freemium gating)."""
    counselor_id = (body or {}).get("counselor_id")
    slot_id = (body or {}).get("slot_id")
    if not counselor_id or not slot_id:
        raise HTTPException(400, "Missing counselor_id or slot_id")

    c = db.query(Counselor).filter(Counselor.id == counselor_id, Counselor.is_active == True).first()
    if not c:
        raise HTTPException(404, "Counselor not found")

    s = db.query(AvailabilitySlot).filter(AvailabilitySlot.id == slot_id, AvailabilitySlot.counselor_id == counselor_id).first()
    if not s:
        raise HTTPException(404, "Slot not found")
    if s.is_booked:
        raise HTTPException(409, "Slot already booked")
    if s.start_time <= utcnow():
        raise HTTPException(400, "Slot is in the past")

    # mark booked and create booking (confirm immediately for MVP)
    s.is_booked = True
    bk = Booking(user_id=u.id, counselor_id=c.id, slot_id=s.id, status=BookingStatus.confirmed)

    db.add(s); db.add(bk); db.commit(); db.refresh(bk)
    return {
        "id": bk.id,
        "status": bk.status,
        "counselor": {"id": c.id, "full_name": c.full_name},
        "slot": {"id": s.id, "start_time": s.start_time.isoformat(), "end_time": s.end_time.isoformat()},
    }


@app.get("/bookings/my")
def my_bookings(u: User = Depends(auth_user), db: Session = Depends(get_db)):
    rows = (
        db.query(Booking)
        .filter(Booking.user_id == u.id)
        .order_by(Booking.created_at.desc())
        .all()
    )
    out = []
    for b in rows:
        # join counselor & slot (SQLAlchemy relationships available)
        c = b.counselor
        s = b.slot
        out.append({
            "id": b.id,
            "status": b.status,
            "created_at": b.created_at.isoformat(),
            "counselor": {"id": c.id, "full_name": c.full_name},
            "slot": {"id": s.id, "start_time": s.start_time.isoformat(), "end_time": s.end_time.isoformat()},
        })
    return out

# -------------------- Routes: Check-ins --------------------

@app.post("/checkin")
def create_checkin(body: CheckInIn, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    if body.stress_level < 0 or body.stress_level > 10:
        raise HTTPException(status_code=400, detail="stress_level must be 0–10")
    ci = AICheckIn(
        user_id=u.id,
        mood=body.mood,
        stress_level=body.stress_level,
        notes=body.notes or "",
    )
    db.add(ci)
    db.commit()
    db.refresh(ci)
    return {"ok": True, "id": ci.id}


@app.get("/checkins")
def list_checkins(limit: int = 7, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    q = (
        db.query(AICheckIn)
        .filter(AICheckIn.user_id == u.id, AICheckIn.deleted == False)
        .order_by(AICheckIn.created_at.desc())
        .limit(max(1, min(limit, 50)))
    )
    return [
        {
            "id": r.id,
            "mood": r.mood,
            "stress_level": r.stress_level,
            "notes": r.notes,
            "created_at": r.created_at.isoformat(),
        }
        for r in q
    ]

# -------------------- Routes: Analytics (basic reporting) --------------------

@app.get("/analytics/overview")
def analytics_overview(u: User = Depends(auth_user), db: Session = Depends(get_db)):
    """High‑level usage stats for the signed‑in user.
    Returns counts for sessions, messages, and check‑ins plus last check‑in snapshot."""
    sessions_count = db.query(ChatSession).filter(ChatSession.user_id == u.id).count()
    messages_count = db.query(ChatMessage).filter(ChatMessage.user_id == u.id).count()
    checkins_count = db.query(AICheckIn).filter(AICheckIn.user_id == u.id, AICheckIn.deleted == False).count()

    last_ci = (
        db.query(AICheckIn)
        .filter(AICheckIn.user_id == u.id, AICheckIn.deleted == False)
        .order_by(AICheckIn.created_at.desc())
        .first()
    )
    last = None
    if last_ci:
        last = {
            "id": last_ci.id,
            "mood": last_ci.mood,
            "stress_level": last_ci.stress_level,
            "created_at": last_ci.created_at.isoformat(),
        }
    return {
        "sessions_count": sessions_count,
        "messages_count": messages_count,
        "checkins_count": checkins_count,
        "last_checkin": last,
    }


@app.get("/analytics/checkins")
def analytics_checkins(days: int = 30, u: User = Depends(auth_user), db: Session = Depends(get_db)):
    """Return simple trends for check‑ins over the last N days.
    Output:
      - buckets: list of { date: YYYY-MM-DD, count, avg_stress }
      - moods: histogram of mood counts in range
      - range: { start, end }
    """
    if days < 1:
        days = 1
    if days > 180:
        days = 180

    end_dt = utcnow()
    start_dt = end_dt - timedelta(days=days)

    rows = (
        db.query(AICheckIn)
        .filter(
            AICheckIn.user_id == u.id,
            AICheckIn.deleted == False,
            AICheckIn.created_at >= start_dt,
            AICheckIn.created_at <= end_dt,
        )
        .order_by(AICheckIn.created_at.asc())
        .all()
    )

    # Bucket by date (YYYY-MM-DD)
    buckets = {}
    mood_hist = {}
    for r in rows:
        day = r.created_at.date().isoformat()
        b = buckets.setdefault(day, {"date": day, "count": 0, "sum_stress": 0})
        b["count"] += 1
        try:
            b["sum_stress"] += int(r.stress_level or 0)
        except Exception:
            pass
        if r.mood:
            mood_hist[r.mood] = mood_hist.get(r.mood, 0) + 1

    # Finalize averages and make a dense list for the full range
    out = []
    for i in range(days + 1):
        d = (start_dt.date() + timedelta(days=i)).isoformat()
        if d in buckets:
            b = buckets[d]
            avg = (b["sum_stress"] / b["count"]) if b["count"] else 0
            out.append({"date": d, "count": b["count"], "avg_stress": round(avg, 2)})
        else:
            out.append({"date": d, "count": 0, "avg_stress": None})

    return {
        "range": {"start": start_dt.isoformat(), "end": end_dt.isoformat()},
        "buckets": out,
        "moods": mood_hist,
    }


# -------------------- Routes: Resources & Health --------------------

@app.get("/resources")
def resources(db: Session = Depends(get_db)):
    rows = (
        db.query(Resource)
        .filter(Resource.deleted == False)
        .order_by(Resource.created_at.desc())
        .all()
    )
    return [{"title": r.title, "desc": r.desc, "url": r.url} for r in rows]


@app.get("/healthz")
def healthz():
    return {"ok": True}
