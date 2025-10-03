import os, requests
import shutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
import re

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

# Allow local dev and deployed frontend
_default_origins = [
    "http://localhost:8080",        # Vue dev
    "http://206.189.144.251",       # your droplet (http)
    # "https://your-frontend-domain.com",  # add Firebase domain later
]
env_origins = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in env_origins.split(",") if o.strip()] or _default_origins

allow_creds = "*" not in origins  # credentials only when not wildcard

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load context + model name (path-safe)
MODEL = os.getenv("OLLAMA_MODEL", "llama3")
CONTEXT_PATH = Path(__file__).parent / "mindcare_context.txt"
STYLING_PATH = Path(__file__).parent / "chat_styling.txt"

try:
    MINDCARE_CONTEXT = CONTEXT_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"[context] {CONTEXT_PATH} not found; using empty context")
    MINDCARE_CONTEXT = ""

try:
    CHAT_STYLE = STYLING_PATH.read_text(encoding="utf-8")
except FileNotFoundError:
    print(f"[styling] {STYLING_PATH} not found; using default style")
    CHAT_STYLE = "Keep responses short, supportive, and in bullet points if possible."

# -------------------- Helpers --------------------
_CUT_MARKERS = [
    "\nUser:", "\nAI:",            # old style
    "\n<user>", "\n</user>",       # new tags
    "\n<assistant>",               # model started a new assistant block
]

_ISO_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
_ASSISTANT_TAGS = re.compile(r"</?assistant>", re.I)

def clean_reply(text: str) -> str:
    if not text:
        return ""

    s = text.strip()

    # If the model wrapped everything in <assistant>...</assistant>, unwrap once
    if s.lower().startswith("<assistant>") and s.lower().endswith("</assistant>"):
        s = _ASSISTANT_TAGS.sub("", s)

    # Cut off if it starts writing the *next* user turn
    cut_at = min((s.find(m) for m in _CUT_MARKERS if m in s), default=-1)
    if cut_at != -1:
        s = s[:cut_at].rstrip()

    # Remove leftover assistant/user tags & labels
    s = _ASSISTANT_TAGS.sub("", s)
    s = re.sub(r"</?(user)>", "", s, flags=re.I)
    s = s.replace("AI:", "").replace("User:", "").replace("Assistant:", "")

    # Remove stray ISO timestamps (sometimes echoed inside reply)
    s = _ISO_RE.sub("", s)

    # Heuristic: if it tries to reintroduce itself ("Hello, I'm MindCare+") at the start,
    # only keep that in the *very first* message (optional).
    s = re.sub(r"(?i)^hello[,!].{0,60}i[’']?m\s+mindcare\+?.*?\.\s*", "", s).lstrip()

    # Collapse spaces/newlines
    s = re.sub(r"[ \t]{2,}", " ", s)
    s = re.sub(r"\n{3,}", "\n\n", s)

    return s.strip()


def clean_reply(text: str) -> str:
    if not text:
        return ""
    # cut at next turn markers
    cut_at = min((text.find(m) for m in _CUT_MARKERS if m in text), default=-1)
    if cut_at != -1:
        text = text[:cut_at]

    # strip tags & echoes
    text = re.sub(r"</?(user|assistant)>", "", text, flags=re.I)
    text = text.replace("AI:", "").replace("User:", "")

    # drop stray ISO timestamps
    text = _ISO_RE.sub("", text)

    # collapse whitespace
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
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

def run_openai(prompt: str, timeout_sec: int | None = None) -> str:
    key = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "220"))
    temperature = float(os.getenv("OPENAI_TEMPERATURE", "0.6"))
    tout = timeout_sec or int(os.getenv("OPENAI_TIMEOUT", "30"))
    if not key:
        print("[openai] missing OPENAI_API_KEY"); return ""
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": f"You are MindCare+, an AI for mental health in Brunei.\n\nStyle guide:\n{CHAT_STYLE}\n\nKnowledge:\n{MINDCARE_CONTEXT}"},
                    {"role": "user", "content": prompt},
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=tout,
        )
        r.raise_for_status()
        data = r.json()
        return (data["choices"][0]["message"]["content"] or "").strip()
    except Exception as e:
        print("[openai] error:", e)
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

MAX_TURNS = 6  # last 6 messages (3 user+3 ai pairs)

def build_prompt(message: str, history: list[ChatTurn] | list[dict] | None = None) -> str:
    def role_of(t):  # accepts ChatTurn or dict
        return (getattr(t, "role", None) or (t.get("role") if isinstance(t, dict) else "")) or ""
    def text_of(t):
        return (getattr(t, "content", None) or (t.get("content") if isinstance(t, dict) else "")) or ""

    # optional external style
    style = ""
    try:
        with open("/opt/mindcare/app/backend/chat_styling.txt", "r", encoding="utf-8") as f:
            style = f.read().strip()
    except Exception:
        pass

    sys_preamble = (
        "You are MindCare+, a concise, supportive mental-health assistant for Brunei. "
        "Be practical, empathetic, and **brief**.\n"
        + (f"\nStyle:\n{style}\n" if style else "")
    )

    parts = [f"<<SYS>>\n{sys_preamble}\n<</SYS>>"]
    turns = (history or [])[-MAX_TURNS:]
    for t in turns:
        if role_of(t) == "user":
            parts.append(f"<user>{text_of(t)}</user>")
        else:
            parts.append(f"<assistant>{text_of(t)}</assistant>")
    parts.append(f"<user>{message}</user>\n<assistant>")
    return "\n".join(parts)

# -------------------- Routes: Public Chat (stateless demo) --------------------
def generate_reply(prompt: str) -> str:
    provider = os.getenv("PROVIDER", "ollama").lower()
    if provider == "openai":
        return run_openai(prompt, timeout_sec=int(os.getenv("OPENAI_TIMEOUT", "30"))) or ""
    # default → ollama
    model = os.getenv("OLLAMA_MODEL", MODEL)
    return run_ollama(model, prompt, timeout_sec=int(os.getenv("OLLAMA_TIMEOUT", "60"))) or ""

def normalize_reply(text: str) -> str:
    cleaned = clean_reply(text or "")
    if not cleaned or cleaned in {".", "...", "…"}:
        provider = os.getenv("PROVIDER", "ollama").lower()
        model = os.getenv("OPENAI_MODEL") if provider == "openai" else os.getenv("OLLAMA_MODEL", MODEL)
        return f"I couldn’t generate a reply right now. If this keeps happening, please check the model '{model}' is installed and reachable."
    return cleaned

@app.post("/chat", response_model=ChatOut)
def chat(body: ChatIn, db: Session = Depends(get_db)):
    prompt = build_prompt(body.message, body.history)
    reply = normalize_reply(generate_reply(prompt))
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

    prev_msgs = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == sid)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in prev_msgs]

    prompt = build_prompt(body.message, history)
    reply = normalize_reply(generate_reply(prompt))

    db.add(ChatMessage(user_id=u.id, session_id=sid, role=ChatRole.user,      content=body.message))
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
