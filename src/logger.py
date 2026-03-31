import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = os.path.join(
    LOG_DIR,
    f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
)


def log_session_start():
    with open(log_filename, "a") as f:
        f.write("=" * 60 + "\n")
        f.write(f"SESSION STARTED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n")


def log_message(role: str, message: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(log_filename, "a") as f:
        f.write(f"[{timestamp}] {role.upper()}: {message}\n")
        f.write("-" * 60 + "\n")


def log_guardrail(guardrail_type: str, trigger: str):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(log_filename, "a") as f:
        f.write(f"[{timestamp}] GUARDRAIL ({guardrail_type}): {trigger}\n")
        f.write("-" * 60 + "\n")


def log_confidence(score: int):
    timestamp = datetime.now().strftime("%H:%M:%S")
    with open(log_filename, "a") as f:
        f.write(f"[{timestamp}] CONFIDENCE SCORE: {score}/10\n")
        f.write("-" * 60 + "\n")


def log_session_end():
    with open(log_filename, "a") as f:
        f.write("=" * 60 + "\n")
        f.write(f"SESSION ENDED: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")