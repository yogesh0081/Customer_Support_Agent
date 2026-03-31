import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """
You are a helpful customer support agent for ShopEasy, an online retail store.
You ONLY answer questions related to:
- Orders and shipping
- Returns and refunds
- Product information
- Account issues

If a question is outside these topics, politely say you can only help with
ShopEasy-related queries and suggest the user contact the right department.

Always be polite, concise, and factual. Never make up order details or policies.
When unsure, escalate to a human agent.
"""

HARMFUL_KEYWORDS = [
    "hack", "exploit", "inject", "drop table", "ignore previous",
    "jailbreak", "forget your instructions", "act as", "pretend you are",
    "you are now", "disregard", "override"
]

OFF_TOPIC_KEYWORDS = [
    "politics", "religion", "violence", "adult content",
    "stock market", "crypto", "medical advice", "legal advice"
]

DOMAIN_TOPICS = [
    "order", "shipping", "delivery", "return", "refund", "product",
    "account", "password", "payment", "tracking", "cancel", "invoice",
    "purchase", "item", "package", "store", "shopease", "discount", "coupon",
    "track", "status", "exchange", "replace", "damaged", "missing",
    "dispatch", "courier", "address", "receipt", "bought", "buy"
]