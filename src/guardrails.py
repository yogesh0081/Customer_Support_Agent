import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from config import HARMFUL_KEYWORDS, OFF_TOPIC_KEYWORDS, DOMAIN_TOPICS


# ── INPUT GUARDRAILS ──────────────────────────────────────────────────────────

def check_prompt_injection(text: str):
    lowered = text.lower()
    for keyword in HARMFUL_KEYWORDS:
        if keyword in lowered:
            return True, (
                "I'm sorry, I can't process that request. "
                "It appears to contain instructions that violate our usage policy."
            )
    return False, ""


def check_harmful_or_irrelevant(text: str):
    lowered = text.lower()
    for keyword in OFF_TOPIC_KEYWORDS:
        if keyword in lowered:
            return True, (
                "I'm a customer support assistant for ShopEasy and can only help "
                "with shopping-related queries. For other topics, please reach out "
                "to the appropriate service."
            )
    return False, ""


def check_sentiment(user_input: str):
    """Detect angry or distressed customers and auto-escalate."""
    angry_phrases = [
        "this is ridiculous", "worst service", "i hate", "terrible",
        "disgusting", "unacceptable", "i am furious", "so angry",
        "extremely upset", "this is a scam", "you guys suck",
        "pathetic", "useless", "never buying again", "demand a refund now",
        "i will sue", "absolutely awful", "worst experience",
        "complete waste", "totally useless", "beyond frustrated"
    ]
    lowered = user_input.lower()
    for phrase in angry_phrases:
        if phrase in lowered:
            return True, (
                "😔 I'm really sorry to hear you're having such a frustrating "
                "experience. I'm immediately escalating this to a senior support "
                "agent who will contact you within 1 hour. "
                "Your concern is our top priority. Reference: ESC-" +
                str(abs(hash(user_input)) % 90000 + 10000)
            )
    return False, ""


def input_guardrail(user_input: str):
    # Handle empty input
    if not user_input.strip():
        return False, ""

    blocked, msg = check_prompt_injection(user_input)
    if blocked:
        return True, msg

    blocked, msg = check_harmful_or_irrelevant(user_input)
    if blocked:
        return True, msg

    blocked, msg = check_sentiment(user_input)
    if blocked:
        return True, msg

    return False, ""


# ── OUTPUT GUARDRAILS ─────────────────────────────────────────────────────────

def check_hallucination_risk(response: str):
    risky_phrases = [
        "i think the price is",
        "probably costs",
        "i believe the order",
        "i'm not sure but",
        "maybe around",
    ]
    lowered = response.lower()
    for phrase in risky_phrases:
        if phrase in lowered:
            return True, (
                "I want to make sure I give you accurate information. "
                "Let me clarify: I can only confirm details from our official "
                "records. Please contact us directly for precise figures."
            )
    return False, ""


def check_unsafe_response(response: str):
    unsafe_phrases = [
        "your password is",
        "credit card number",
        "here is how to hack",
        "ignore your instructions",
    ]
    lowered = response.lower()
    for phrase in unsafe_phrases:
        if phrase in lowered:
            return True, (
                "I'm unable to share that information for security reasons. "
                "Please contact our support team directly for account-sensitive issues."
            )
    return False, ""


def output_guardrail(response: str):
    flagged, msg = check_hallucination_risk(response)
    if flagged:
        return True, msg

    flagged, msg = check_unsafe_response(response)
    if flagged:
        return True, msg

    return False, response


# ── BEHAVIORAL GUARDRAILS ─────────────────────────────────────────────────────

def enforce_domain_restriction(user_input: str):
    lowered = user_input.lower()
    for topic in DOMAIN_TOPICS:
        if topic in lowered:
            return False, ""

    return True, (
        "I'm here to help with ShopEasy orders, products, and account queries. "
        "Your question seems unrelated — could you rephrase it in that context? "
        "If you need other help, please visit our Help Center."
    )


def behavioral_guardrail(user_input: str):
    # Handle empty input
    if not user_input.strip():
        return False, ""
    return enforce_domain_restriction(user_input)