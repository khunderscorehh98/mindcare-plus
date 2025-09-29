from database import Base, engine, SessionLocal
from models import Resource
from datetime import datetime

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    if not db.query(Resource).first():
        items = [
            Resource(title="Brunei Healthline (MOH)", desc="Official health services", url="https://www.moh.gov.bn"),
            Resource(title="WHO Mental Health", desc="Global guidance on mental health", url="https://www.who.int/health-topics/mental-health"),
        ]
        db.add_all(items)
        db.commit()
    db.close()

if __name__ == "__main__":
    seed()