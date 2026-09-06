from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class QuestionBase(BaseModel):
    id: int
    subject: Optional[str] = None
    topic: Optional[str] = None
    difficulty: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True

class QuestionWithAnswer(QuestionBase):
    correct: int

class TopicSummary(BaseModel):
    topic: str
    question_count: int

class VerifyAnswerRequest(BaseModel):
    question_id: int
    selected_option: int

class VerifyAnswerResponse(BaseModel):
    is_correct: bool
    correct_option: int
    explanation: Optional[str] = None

class FlagQuestionRequest(BaseModel):
    question_id: int
    reason: Optional[str] = "Flagged by user during challenge"

class FlagQuestionResponse(BaseModel):
    status: str
    question_id: int
    message: str

# --- AUTH SCHEMAS ---
class UserRegisterRequest(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    email: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None

    class Config:
        from_attributes = True

class AuthResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None

# --- PROGRESS SCHEMAS ---
class RecordAttemptRequest(BaseModel):
    user_id: int
    question_id: int
    selected_option: int
    is_correct: bool
    mode: Optional[str] = "practice"

class RecordAttemptResponse(BaseModel):
    status: str
    attempt_id: int

class SubmitTestSessionRequest(BaseModel):
    user_id: int
    mode: str  # mock_test, millionaire
    score: float
    total_questions: int
    correct_count: int
    incorrect_count: int
    unattempted_count: int
    time_taken_seconds: Optional[int] = 0
    details_json: Optional[str] = None

class TestSessionResponse(BaseModel):
    id: int
    user_id: int
    mode: str
    score: float
    total_questions: int
    correct_count: int
    incorrect_count: int
    unattempted_count: int
    time_taken_seconds: Optional[int] = 0
    created_at: Optional[Any] = None

    class Config:
        from_attributes = True

class TopicPerformance(BaseModel):
    topic: str
    attempted: int
    correct: int
    accuracy_pct: float

class UserSummaryResponse(BaseModel):
    user_id: int
    username: str
    full_name: Optional[str] = None
    total_attempted: int
    total_correct: int
    accuracy_pct: float
    mock_tests_taken: int
    best_mock_score: float
    strong_topics: List[str] = []
    weak_topics: List[str] = []
    topic_breakdown: List[TopicPerformance] = []
    recent_sessions: List[TestSessionResponse] = []

