import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import Column, BigInteger, Text, DateTime, Integer, Float, Boolean, ForeignKey, func

try:
    from database import Base
except ImportError:
    from backend.database import Base

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

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    username = Column(Text, unique=True, nullable=False, index=True)
    email = Column(Text, unique=True, nullable=True)
    password_hash = Column(Text, nullable=False)
    salt = Column(Text, nullable=False)
    full_name = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserQuestionAttempt(Base):
    __tablename__ = "user_question_attempts"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(BigInteger, ForeignKey("gate_questions.id"), nullable=False, index=True)
    selected_option = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    mode = Column(Text, default="practice", index=True)  # practice, mock_test, millionaire
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class UserTestSession(Base):
    __tablename__ = "user_test_sessions"

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    mode = Column(Text, nullable=False, index=True)  # mock_test, millionaire
    score = Column(Float, default=0.0)
    total_questions = Column(Integer, default=0)
    correct_count = Column(Integer, default=0)
    incorrect_count = Column(Integer, default=0)
    unattempted_count = Column(Integer, default=0)
    time_taken_seconds = Column(Integer, default=0)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

