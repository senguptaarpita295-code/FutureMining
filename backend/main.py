from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import func
from typing import List, Optional

from database import engine, Base, get_db
import models
import schemas

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="FutureMining GATE API",
    description="Backend API powering the FutureMining GATE preparation platform & Millionaire game",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "FutureMining GATE API"}

@app.get("/")
def root():
    return {
        "message": "FutureMining GATE API is running",
        "docs": "/docs",
        "endpoints": [
            "/health",
            "/api/questions",
            "/api/topics",
            "/api/game/ladder",
            "/api/game/verify",
            "/api/reviews/flag",
            "/api/reviews/flagged",
        ]
    }

@app.get("/api/questions", response_model=List[schemas.QuestionWithAnswer])
def list_questions(
    topic: Optional[str] = None,
    difficulty: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    query = db.query(models.GateQuestion)
    if topic:
        query = query.filter(models.GateQuestion.topic == topic)
    if difficulty is not None:
        query = query.filter(models.GateQuestion.difficulty == difficulty)
    return query.order_by(models.GateQuestion.id).offset(skip).limit(limit).all()

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

@app.get("/api/game/ladder", response_model=List[schemas.QuestionWithAnswer])
def get_game_ladder(db: Session = Depends(get_db)):
    from sqlalchemy import text
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
    db: Session = Depends(get_db)
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
        explanation=f"The correct answer is Option {chr(65 + question.correct)}."
    )

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
            message="Question is already in the review queue"
        )
    
    item = models.ReviewQueueItem(
        question_id=payload.question_id,
        reason=payload.reason or "Flagged by user"
    )
    db.add(item)
    db.commit()
    return schemas.FlagQuestionResponse(
        status="success",
        question_id=payload.question_id,
        message="Question successfully flagged for review"
    )

@app.get("/api/reviews/flagged", response_model=List[str])
def get_flagged_question_ids(db: Session = Depends(get_db)):
    items = db.query(models.ReviewQueueItem.question_id).all()
    return [str(item[0]) for item in items]
