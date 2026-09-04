from typing import List, Optional
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
