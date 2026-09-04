from sqlalchemy import Column, BigInteger, Text, DateTime, func
from database import Base

class GateQuestion(Base):
    __tablename__ = "gate_questions"

    id = Column(BigInteger, primary_key=True, index=True)
    subject = Column(Text, nullable=True)
    topic = Column(Text, nullable=True, index=True)
    difficulty = Column(BigInteger, nullable=False, index=True)
    question = Column(Text, nullable=False)
    option_a = Column(Text, nullable=False)
    option_b = Column(Text, nullable=False)
    option_c = Column(Text, nullable=False)
    option_d = Column(Text, nullable=False)
    correct = Column(BigInteger, nullable=False)

class ReviewQueueItem(Base):
    __tablename__ = "review_queue"

    id = Column(BigInteger, primary_key=True, index=True)
    question_id = Column(BigInteger, nullable=False, unique=True, index=True)
    reason = Column(Text, default="Flagged by user")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
