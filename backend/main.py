import os
import sys
from pathlib import Path

# Ensure backend directory is in sys.path regardless of execution working directory (e.g. on Render)
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import hashlib
import secrets
import json
from typing import List, Optional
from datetime import datetime

from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from sqlalchemy import text, desc

try:
    from database import engine, Base, get_db
    import models
    import schemas
except ImportError:
    from backend.database import engine, Base, get_db
    from backend import models, schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FutureMining GATE API",
    description="Backend API powering the FutureMining GATE preparation platform, ExamGoal Practice & Mock, and Millionaire Challenge",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PASSWORD SECURITY HELPERS
# ============================================================
def hash_password(password: str) -> tuple[str, str]:
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return pwd_hash, salt


def verify_password(password: str, pwd_hash: str, salt: str) -> bool:
    calc_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return secrets.compare_digest(calc_hash, pwd_hash)


# ============================================================
# SYSTEM HEALTH & ROOT
# ============================================================
@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        q_count = db.query(models.GateQuestion).count()
        return {
            "status": "ok",
            "service": "FutureMining GATE API",
            "database": "connected",
            "total_questions": q_count,
        }
    except Exception as e:
        return {
            "status": "degraded",
            "service": "FutureMining GATE API",
            "database_error": str(e),
        }


@app.get("/")
def root():
    return {
        "message": "FutureMining GATE API is running",
        "version": "2.0.0",
        "docs": "/docs",
        "modules": [
            "Authentication (/api/auth)",
            "Question Bank (/api/questions, /api/topics)",
            "Game Ladder & Verify (/api/game)",
            "Progress & Analytics (/api/progress)",
            "Review Queue (/api/reviews)",
        ],
    }


# ============================================================
# AUTHENTICATION ENDPOINTS
# ============================================================
@app.post("/api/auth/register", response_model=schemas.AuthResponse)
def register_user(payload: schemas.UserRegisterRequest, db: Session = Depends(get_db)):
    clean_username = payload.username.strip().lower()
    if not clean_username or len(clean_username) < 3:
        raise HTTPException(
            status_code=400,
            detail="Username must be at least 3 characters long",
        )
    if not payload.password or len(payload.password) < 4:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 4 characters long",
        )

    existing = db.query(models.User).filter(
        func.lower(models.User.username) == clean_username
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Username '{payload.username}' is already taken",
        )

    pwd_hash, salt = hash_password(payload.password)
    user = models.User(
        username=payload.username.strip(),
        email=payload.email.strip() if payload.email else None,
        password_hash=pwd_hash,
        salt=salt,
        full_name=payload.full_name.strip() if payload.full_name else payload.username.strip(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return schemas.AuthResponse(
        success=True,
        message="Registration successful! Welcome to FutureMining.",
        user=schemas.UserResponse.model_validate(user),
    )


@app.post("/api/auth/login", response_model=schemas.AuthResponse)
def login_user(payload: schemas.UserLoginRequest, db: Session = Depends(get_db)):
    clean_username = payload.username.strip().lower()
    user = db.query(models.User).filter(
        func.lower(models.User.username) == clean_username
    ).first()

    if not user or not verify_password(payload.password, user.password_hash, user.salt):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )

    return schemas.AuthResponse(
        success=True,
        message=f"Welcome back, {user.full_name or user.username}!",
        user=schemas.UserResponse.model_validate(user),
    )


@app.get("/api/auth/me/{user_id}", response_model=schemas.UserResponse)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return schemas.UserResponse.model_validate(user)


# ============================================================
# QUESTION BANK ENDPOINTS
# ============================================================
@app.get("/api/questions", response_model=List[schemas.QuestionWithAnswer])
def list_questions(
    topic: Optional[str] = None,
    subject: Optional[str] = None,
    difficulty: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=2000),
    randomize: bool = False,
    db: Session = Depends(get_db),
):
    query = db.query(models.GateQuestion)
    if topic:
        query = query.filter(models.GateQuestion.topic == topic)
    if subject:
        query = query.filter(models.GateQuestion.subject == subject)
    if difficulty is not None:
        query = query.filter(models.GateQuestion.difficulty == difficulty)

    if randomize:
        query = query.order_by(func.random())
    else:
        query = query.order_by(models.GateQuestion.id)

    return query.offset(skip).limit(limit).all()


@app.get("/api/questions/{question_id}", response_model=schemas.QuestionWithAnswer)
def get_question(question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.GateQuestion).filter(models.GateQuestion.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.get("/api/topics", response_model=List[schemas.TopicSummary])
def get_topics(db: Session = Depends(get_db)):
    results = (
        db.query(models.GateQuestion.topic, func.count(models.GateQuestion.id))
        .group_by(models.GateQuestion.topic)
        .order_by(func.count(models.GateQuestion.id).desc())
        .all()
    )
    return [
        schemas.TopicSummary(topic=row[0] or "General Mining", question_count=row[1])
        for row in results
        if row[0]
    ]


# ============================================================
# GAME ENDPOINTS (Millionaire Challenge)
# ============================================================
@app.get("/api/game/ladder", response_model=List[schemas.QuestionWithAnswer])
def get_game_ladder(db: Session = Depends(get_db)):
    sql = text("""
        SELECT id, subject, topic, difficulty, question, option_a, option_b, option_c, option_d, correct
        FROM (
            SELECT DISTINCT ON (difficulty) *
            FROM gate_questions
            ORDER BY difficulty, random()
        ) sub
        ORDER BY difficulty;
    """)
    rows = db.execute(sql).mappings().all()
    return [models.GateQuestion(**row) for row in rows]


@app.get("/api/game/swap", response_model=schemas.QuestionWithAnswer)
def swap_question(
    level: int = Query(..., ge=1, le=15),
    exclude_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.GateQuestion).filter(models.GateQuestion.difficulty == level)
    if exclude_id is not None:
        query = query.filter(models.GateQuestion.id != exclude_id)
    question = query.order_by(func.random()).first()
    if not question:
        question = db.query(models.GateQuestion).order_by(func.random()).first()
    return question


@app.post("/api/game/verify", response_model=schemas.VerifyAnswerResponse)
def verify_answer(payload: schemas.VerifyAnswerRequest, db: Session = Depends(get_db)):
    question = db.query(models.GateQuestion).filter(models.GateQuestion.id == payload.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    is_correct = (payload.selected_option == question.correct)
    return schemas.VerifyAnswerResponse(
        is_correct=is_correct,
        correct_option=question.correct,
        explanation=f"The correct answer is Option {chr(65 + question.correct)}.",
    )


# ============================================================
# PROGRESS TRACKING & ANALYTICS
# ============================================================
@app.post("/api/progress/attempt", response_model=schemas.RecordAttemptResponse)
def record_question_attempt(payload: schemas.RecordAttemptRequest, db: Session = Depends(get_db)):
    attempt = models.UserQuestionAttempt(
        user_id=payload.user_id,
        question_id=payload.question_id,
        selected_option=payload.selected_option,
        is_correct=payload.is_correct,
        mode=payload.mode or "practice",
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return schemas.RecordAttemptResponse(status="recorded", attempt_id=attempt.id)


@app.post("/api/progress/test-session", response_model=schemas.TestSessionResponse)
def submit_test_session(payload: schemas.SubmitTestSessionRequest, db: Session = Depends(get_db)):
    session = models.UserTestSession(
        user_id=payload.user_id,
        mode=payload.mode,
        score=payload.score,
        total_questions=payload.total_questions,
        correct_count=payload.correct_count,
        incorrect_count=payload.incorrect_count,
        unattempted_count=payload.unattempted_count,
        time_taken_seconds=payload.time_taken_seconds or 0,
        details_json=payload.details_json,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return schemas.TestSessionResponse.model_validate(session)


@app.get("/api/progress/{user_id}/summary", response_model=schemas.UserSummaryResponse)
def get_user_summary(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Overall attempt stats
    total_attempted = db.query(models.UserQuestionAttempt).filter(
        models.UserQuestionAttempt.user_id == user_id
    ).count()

    total_correct = db.query(models.UserQuestionAttempt).filter(
        models.UserQuestionAttempt.user_id == user_id,
        models.UserQuestionAttempt.is_correct == True
    ).count()

    accuracy_pct = round((total_correct / max(1, total_attempted)) * 100, 1) if total_attempted > 0 else 0.0

    # Mock test stats
    mock_sessions = db.query(models.UserTestSession).filter(
        models.UserTestSession.user_id == user_id,
        models.UserTestSession.mode == "mock_test"
    ).all()

    mock_tests_taken = len(mock_sessions)
    best_mock_score = max([s.score for s in mock_sessions], default=0.0)

    # Topic-wise performance
    topic_sql = text("""
        SELECT q.topic, COUNT(a.id) AS attempted,
               SUM(CASE WHEN a.is_correct THEN 1 ELSE 0 END) AS correct
        FROM user_question_attempts a
        JOIN gate_questions q ON a.question_id = q.id
        WHERE a.user_id = :uid AND q.topic IS NOT NULL
        GROUP BY q.topic
        ORDER BY attempted DESC
    """)
    topic_rows = db.execute(topic_sql, {"uid": user_id}).fetchall()

    topic_breakdown = []
    strong_topics = []
    weak_topics = []

    for r in topic_rows:
        t_name = r[0]
        att = int(r[1])
        corr = int(r[2] or 0)
        acc = round((corr / max(1, att)) * 100, 1)
        topic_breakdown.append(schemas.TopicPerformance(
            topic=t_name,
            attempted=att,
            correct=corr,
            accuracy_pct=acc,
        ))
        if att >= 3:
            if acc >= 70.0:
                strong_topics.append(t_name)
            elif acc < 50.0:
                weak_topics.append(t_name)

    # Recent sessions (both mock and millionaire)
    recent = (
        db.query(models.UserTestSession)
        .filter(models.UserTestSession.user_id == user_id)
        .order_by(desc(models.UserTestSession.created_at))
        .limit(10)
        .all()
    )
    recent_responses = [schemas.TestSessionResponse.model_validate(s) for s in recent]

    return schemas.UserSummaryResponse(
        user_id=user.id,
        username=user.username,
        full_name=user.full_name,
        total_attempted=total_attempted,
        total_correct=total_correct,
        accuracy_pct=accuracy_pct,
        mock_tests_taken=mock_tests_taken,
        best_mock_score=best_mock_score,
        strong_topics=strong_topics[:5],
        weak_topics=weak_topics[:5],
        topic_breakdown=topic_breakdown,
        recent_sessions=recent_responses,
    )


@app.get("/api/progress/{user_id}/history", response_model=List[schemas.TestSessionResponse])
def get_user_history(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.UserTestSession)
        .filter(models.UserTestSession.user_id == user_id)
        .order_by(desc(models.UserTestSession.created_at))
        .limit(50)
        .all()
    )
    return [schemas.TestSessionResponse.model_validate(s) for s in sessions]


# ============================================================
# REVIEW QUEUE ENDPOINTS
# ============================================================
@app.post("/api/reviews/flag", response_model=schemas.FlagQuestionResponse)
def flag_question(payload: schemas.FlagQuestionRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(models.ReviewQueueItem)
        .filter(models.ReviewQueueItem.question_id == payload.question_id)
        .first()
    )
    if existing:
        return schemas.FlagQuestionResponse(
            status="already_flagged",
            question_id=payload.question_id,
            message="Question is already in the review queue",
        )

    item = models.ReviewQueueItem(
        question_id=payload.question_id,
        reason=payload.reason or "Flagged by user",
    )
    db.add(item)
    db.commit()
    return schemas.FlagQuestionResponse(
        status="success",
        question_id=payload.question_id,
        message="Question successfully flagged for review",
    )


@app.get("/api/reviews/flagged", response_model=List[str])
def get_flagged_question_ids(db: Session = Depends(get_db)):
    items = db.query(models.ReviewQueueItem.question_id).all()
    return [str(item[0]) for item in items]

