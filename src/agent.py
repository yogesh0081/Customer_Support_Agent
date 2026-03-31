import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq
from config import GROQ_API_KEY, MODEL, SYSTEM_PROMPT
from guardrails import input_guardrail, output_guardrail, behavioral_guardrail
from multi_agent import run_multi_agent
from memory import load_memory, save_memory, update_memory, add_issue_to_history, get_memory_summary
from logger import log_session_start, log_message, log_guardrail, log_confidence, log_session_end

client = Groq(api_key=GROQ_API_KEY)
conversation_history = []

# Load memory at startup
user_memory = load_memory("default")


def extract_name_from_input(user_input: str):
    """Try to extract user's name from intro messages."""
    lowered = user_input.lower()
    triggers = ["my name is", "i am ", "i'm ", "this is "]
    for trigger in triggers:
        if trigger in lowered:
            idx = lowered.index(trigger) + len(trigger)
            name = user_input[idx:].split()[0].strip(".,!?")
            if len(name) > 1:
                return name.capitalize()
    return None


def run_agent(user_input: str) -> str:
    global user_memory
    log_message("user", user_input)

    # Try to extract name if we don't have it
    if not user_memory.get("name"):
        name = extract_name_from_input(user_input)
        if name:
            user_memory = update_memory(user_memory, "name", name)
            save_memory(user_memory)

    # Step 1 — input guardrail
    blocked, msg = input_guardrail(user_input)
    if blocked:
        log_guardrail("INPUT", user_input)
        log_message("agent", msg)
        return msg

    # Step 2 — behavioral guardrail
    blocked, msg = behavioral_guardrail(user_input)
    if blocked:
        log_guardrail("BEHAVIORAL", user_input)
        log_message("agent", msg)
        return msg

    # Step 3 — add issue to history
    user_memory = add_issue_to_history(user_memory, user_input)
    save_memory(user_memory)

    # Step 4 — run multi-agent pipeline with memory context
    memory_context = get_memory_summary(user_memory)
    enriched_input = f"{user_input}\n[Customer context: {memory_context}]"

    result = run_multi_agent(enriched_input)
    raw_answer = result["final_response"]

    # Step 5 — output guardrail
    modified, safe_answer = output_guardrail(raw_answer)
    if modified:
        log_guardrail("OUTPUT", raw_answer)

    # Step 6 — quality score
    score = result["critic_score"]
    log_confidence(score)

    if score <= 4:
        safe_answer += (
            f"\n\n⚠️  Low confidence ({score}/10) — "
            f"Please contact our support team to verify."
        )
    else:
        safe_answer += f"\n\n📊 Quality score: {score}/10"

    log_message("agent", safe_answer)
    conversation_history.append({"role": "assistant", "content": safe_answer})

    return safe_answer


def main():
    global user_memory

    # Update session count
    user_memory["total_sessions"] = user_memory.get("total_sessions", 0) + 1
    save_memory(user_memory)

    log_session_start()

    print("=" * 50)
    print("  ShopEasy Customer Support Agent")
    print("  Multi-Agent: Planner + Executor + Critic")
    print("  Type 'quit' to exit")
    print("=" * 50)

    # Greet returning users
    if user_memory.get("name"):
        print(f"\n  Welcome back, {user_memory['name']}! 👋")
    if user_memory.get("issue_history"):
        last = user_memory["issue_history"][-1]
        print(f"  Last contact: {last['date']}")
    print()

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["quit", "exit"]:
            log_session_end()
            print("Goodbye! Session saved to logs/")
            break

        response = run_agent(user_input)
        print(f"\nAgent: {response}")


if __name__ == "__main__":
    main()