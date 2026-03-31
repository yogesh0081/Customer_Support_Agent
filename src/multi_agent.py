import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from groq import Groq
from config import GROQ_API_KEY, MODEL
from tools import faq_lookup, check_order_status, escalate_to_human

client = Groq(api_key=GROQ_API_KEY)


# ── AGENT 1: PLANNER ─────────────────────────────────────────────────────────

def planner_agent(user_input: str) -> dict:
    """
    Decides which tool to use and what the plan is.
    Returns a plan dictionary.
    """
    prompt = f"""
You are a planning agent for a customer support system.
Given the user query, decide:
1. Which tool to use: faq_lookup, order_status, escalate, or none
2. What information is needed
3. What the goal of the response should be

User query: {user_input}

Reply in this exact format:
TOOL: <faq_lookup|order_status|escalate|none>
ORDER_ID: <order id if mentioned, else none>
GOAL: <one sentence describing what the response should achieve>
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=100,
    )

    raw = response.choices[0].message.content.strip()
    plan = {"tool": "none", "order_id": None, "goal": "Answer the user query helpfully."}

    for line in raw.split("\n"):
        if line.startswith("TOOL:"):
            plan["tool"] = line.replace("TOOL:", "").strip().lower()
        elif line.startswith("ORDER_ID:"):
            val = line.replace("ORDER_ID:", "").strip()
            plan["order_id"] = val if val.lower() != "none" else None
        elif line.startswith("GOAL:"):
            plan["goal"] = line.replace("GOAL:", "").strip()

    return plan


# ── AGENT 2: EXECUTOR ────────────────────────────────────────────────────────

def executor_agent(user_input: str, plan: dict) -> str:
    """
    Executes the plan by calling the right tool and generating a response.
    """
    # Call the right tool based on planner's decision
    tool_result = ""
    tool = plan.get("tool", "none")

    if tool == "faq_lookup":
        tool_result = faq_lookup(user_input)
    elif tool == "order_status":
        order_id = plan.get("order_id") or ""
        if not order_id:
            words = user_input.upper().split()
            for word in words:
                if word.startswith("ORD"):
                    order_id = word
                    break
        tool_result = check_order_status(order_id) if order_id else "No order ID found."
    elif tool == "escalate":
        tool_result = escalate_to_human("Customer needs human assistance.")
    else:
        tool_result = faq_lookup(user_input)

    # Generate response using tool result
    prompt = f"""
You are a helpful customer support agent for ShopEasy.
Your goal: {plan['goal']}

Tool result: {tool_result}
User question: {user_input}

Write a polite, concise, helpful response using the tool result above.
Do not make up any information not in the tool result.
"""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=250,
    )

    return response.choices[0].message.content.strip()


# ── AGENT 3: CRITIC ──────────────────────────────────────────────────────────

def critic_agent(user_input: str, response: str) -> dict:
    """
    Reviews the executor's response for quality, accuracy, and safety.
    Returns approved response or a corrected one.
    """
    prompt = f"""
You are a quality control critic for a customer support AI system.
Review this response and check:
1. Is it polite and professional?
2. Does it actually answer the question?
3. Does it contain any made-up information?
4. Is it concise (not too long)?
5. Is it safe and appropriate?

User question: {user_input}
Response to review: {response}

Reply in this exact format:
APPROVED: <yes|no>
SCORE: <1-10>
ISSUE: <describe issue if not approved, else none>
IMPROVED: <improved response if not approved, else none>
"""
    result = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        max_tokens=300,
    )

    raw = result.choices[0].message.content.strip()
    review = {
        "approved": True,
        "score": 8,
        "issue": None,
        "final_response": response
    }

    lines = raw.split("\n")
    improved_lines = []
    in_improved = False

    for line in lines:
        if line.startswith("APPROVED:"):
            val = line.replace("APPROVED:", "").strip().lower()
            review["approved"] = val == "yes"
        elif line.startswith("SCORE:"):
            try:
                review["score"] = int(line.replace("SCORE:", "").strip())
            except ValueError:
                review["score"] = 7
        elif line.startswith("ISSUE:"):
            issue = line.replace("ISSUE:", "").strip()
            review["issue"] = None if issue.lower() == "none" else issue
        elif line.startswith("IMPROVED:"):
            val = line.replace("IMPROVED:", "").strip()
            if val.lower() != "none":
                improved_lines.append(val)
            in_improved = True
        elif in_improved and line.strip():
            improved_lines.append(line.strip())

    if not review["approved"] and improved_lines:
        review["final_response"] = " ".join(improved_lines)

    return review


# ── FULL MULTI-AGENT PIPELINE ─────────────────────────────────────────────────

def run_multi_agent(user_input: str) -> dict:
    """
    Runs the full Planner → Executor → Critic pipeline.
    Returns final response with metadata.
    """
    print("\n  [Planner] Analyzing query...")
    plan = planner_agent(user_input)
    print(f"  [Planner] Tool: {plan['tool']} | Goal: {plan['goal'][:60]}...")

    print("  [Executor] Running tool and generating response...")
    raw_response = executor_agent(user_input, plan)

    print("  [Critic] Reviewing response quality...")
    review = critic_agent(user_input, raw_response)
    print(f"  [Critic] Score: {review['score']}/10 | Approved: {review['approved']}")

    return {
        "plan": plan,
        "raw_response": raw_response,
        "approved": review["approved"],
        "critic_score": review["score"],
        "issue": review["issue"],
        "final_response": review["final_response"]
    }