import os
import requests
from typing import List, Dict, Any, Optional

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TIMEOUT = 8.0

def get_api_status() -> bool:
    """Check if the FastAPI backend is online and responding."""
    try:
        resp = requests.get(f"{API_BASE_URL}/health", timeout=1.5)
        return resp.status_code == 200
    except Exception:
        return False

def fetch_game_ladder() -> Optional[List[Dict[str, Any]]]:
    """Fetch 15 progressive difficulty questions for the Millionaire challenge."""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/game/ladder", timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def fetch_swap_question(level: int, exclude_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """Fetch an alternate question for a specific level."""
    try:
        params = {"level": level}
        if exclude_id is not None:
            params["exclude_id"] = exclude_id
        resp = requests.get(f"{API_BASE_URL}/api/game/swap", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def fetch_topics() -> List[Dict[str, Any]]:
    """Fetch all mining engineering topics with question counts."""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/topics", timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []

def fetch_questions(
    topic: Optional[str] = None,
    difficulty: Optional[int] = None,
    limit: int = 50,
    skip: int = 0
) -> List[Dict[str, Any]]:
    """Fetch questions filtered by topic and difficulty for ExamGoal practice/mock."""
    try:
        params: Dict[str, Any] = {"limit": limit, "skip": skip}
        if topic:
            params["topic"] = topic
        if difficulty is not None:
            params["difficulty"] = difficulty
        resp = requests.get(f"{API_BASE_URL}/api/questions", params=params, timeout=TIMEOUT)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return []

def verify_answer_server(question_id: int, selected_option: int) -> Optional[Dict[str, Any]]:
    """Verify an answer securely via FastAPI backend."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/game/verify",
            json={"question_id": question_id, "selected_option": selected_option},
            timeout=TIMEOUT
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None

def flag_question_server(question_id: int, reason: str = "Flagged by user") -> bool:
    """Flag a question directly in Supabase PostgreSQL."""
    try:
        resp = requests.post(
            f"{API_BASE_URL}/api/reviews/flag",
            json={"question_id": int(question_id), "reason": reason},
            timeout=TIMEOUT
        )
        return resp.status_code == 200
    except Exception:
        return False

def get_flagged_question_ids() -> set[str]:
    """Retrieve all flagged question IDs from Supabase PostgreSQL."""
    try:
        resp = requests.get(f"{API_BASE_URL}/api/reviews/flagged", timeout=TIMEOUT)
        if resp.status_code == 200:
            return set(resp.json())
    except Exception:
        pass
    return set()
