import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MEMORY_FILE = os.path.join(BASE_DIR, "data", "user_memory.json")


def load_memory(user_id: str = "default") -> dict:
    """Load user memory from JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return _empty_memory(user_id)
    try:
        with open(MEMORY_FILE, "r") as f:
            all_memory = json.load(f)
        return all_memory.get(user_id, _empty_memory(user_id))
    except Exception:
        return _empty_memory(user_id)


def save_memory(memory: dict, user_id: str = "default"):
    """Save user memory to JSON file."""
    all_memory = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                all_memory = json.load(f)
        except Exception:
            pass
    all_memory[user_id] = memory
    with open(MEMORY_FILE, "w") as f:
        json.dump(all_memory, f, indent=2)


def update_memory(memory: dict, key: str, value):
    """Update a specific field in memory."""
    memory[key] = value
    memory["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return memory


def add_issue_to_history(memory: dict, issue: str) -> dict:
    """Add a new issue to the user's history."""
    if "issue_history" not in memory:
        memory["issue_history"] = []
    memory["issue_history"].append({
        "issue": issue,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })
    # Keep only last 10 issues
    memory["issue_history"] = memory["issue_history"][-10:]
    return memory


def _empty_memory(user_id: str) -> dict:
    return {
        "user_id": user_id,
        "name": None,
        "email": None,
        "last_seen": None,
        "issue_history": [],
        "preferred_language": "english",
        "total_sessions": 0
    }


def get_memory_summary(memory: dict) -> str:
    """Return a string summary of memory for the LLM context."""
    parts = []
    if memory.get("name"):
        parts.append(f"Customer name: {memory['name']}")
    if memory.get("email"):
        parts.append(f"Email: {memory['email']}")
    if memory.get("last_seen"):
        parts.append(f"Last contact: {memory['last_seen']}")
    if memory.get("issue_history"):
        last = memory["issue_history"][-1]
        parts.append(f"Last issue: {last['issue']} on {last['date']}")
    if memory.get("total_sessions", 0) > 1:
        parts.append(f"Returning customer ({memory['total_sessions']} sessions)")
    return " | ".join(parts) if parts else "New customer, no history"