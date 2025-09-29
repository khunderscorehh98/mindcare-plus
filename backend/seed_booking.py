"""
Seed a few counselors and their availability slots (next 14 days).
- Stores datetimes in UTC (DB expects naive UTC DateTime in this project).
- Slot times are defined in Brunei time (BNT, UTC+8) then converted to UTC.

Run: python3 seed_booking.py
"""
from datetime import datetime, timedelta

from database import Base, engine, SessionLocal  # assumes SessionLocal exists in database.py
from models import Counselor, AvailabilitySlot

# --- config ---
DAYS_AHEAD = 14
# in Brunei time (UTC+8); we convert before saving
DAILY_TIMES_BNT = [(9, 0), (14, 0), (20, 0)]  # 09:00, 14:00, 20:00
SLOT_MINUTES = 50
UTC_OFFSET_HOURS = 8  # BNT = UTC+8

COUNSELORS = [
    dict(
        full_name="Aisyah Salleh, RP(Brunei)",
        bio="Registered counselor with experience in anxiety and adolescent well‑being.",
        specialties="anxiety,stress,students",
        price_cents=4500,
        currency="BND",
    ),
    dict(
        full_name="Hafiz Rahman, MS Psych",
        bio="Trauma-informed therapist; CBT & mindfulness.",
        specialties="trauma,cbt,mindfulness",
        price_cents=6000,
        currency="BND",
    ),
]


def bnt_to_utc(dt_bnt: datetime) -> datetime:
    """Convert naive BNT (UTC+8) to naive UTC for storage."""
    return dt_bnt - timedelta(hours=UTC_OFFSET_HOURS)


def ensure_counselors(db):
    created = []
    for c in COUNSELORS:
        exists = db.query(Counselor).filter(Counselor.full_name == c["full_name"]).first()
        if exists:
            created.append(exists)
            continue
        obj = Counselor(**c)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        created.append(obj)
        print(f"[seed] counselor: {obj.full_name} (id={obj.id})")
    return created


def ensure_slots(db, counselor, days_ahead=DAYS_AHEAD):
    today_bnt = datetime.utcnow() + timedelta(hours=UTC_OFFSET_HOURS)
    start_date_bnt = today_bnt.replace(hour=0, minute=0, second=0, microsecond=0)

    for d in range(days_ahead):
        day_bnt = start_date_bnt + timedelta(days=d)
        for (hh, mm) in DAILY_TIMES_BNT:
            start_bnt = day_bnt.replace(hour=hh, minute=mm)
            end_bnt = start_bnt + timedelta(minutes=SLOT_MINUTES)
            start_utc = bnt_to_utc(start_bnt)
            end_utc = bnt_to_utc(end_bnt)

            # idempotency: skip if slot already exists for same start time
            exists = (
                db.query(AvailabilitySlot)
                .filter(AvailabilitySlot.counselor_id == counselor.id,
                        AvailabilitySlot.start_time == start_utc)
                .first()
            )
            if exists:
                continue

            slot = AvailabilitySlot(
                counselor_id=counselor.id,
                start_time=start_utc,
                end_time=end_utc,
                is_booked=False,
            )
            db.add(slot)
    db.commit()
    print(f"[seed] slots created for {counselor.full_name}")


if __name__ == "__main__":
    # Create tables if not yet created
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        counselors = ensure_counselors(db)
        for c in counselors:
            ensure_slots(db, c)
        print("[seed] done.")
    finally:
        db.close()
