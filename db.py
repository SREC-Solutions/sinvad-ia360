from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Conversation

engine = create_engine("sqlite:///db.sqlite3")
SessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def log_conversation(session_id: str, user_input: str, ai_response: str):
    db = SessionLocal()
    record = Conversation(
        session_id=session_id,
        user_input=user_input,
        ai_response=ai_response
    )
    db.add(record)
    db.commit()
    db.close()
