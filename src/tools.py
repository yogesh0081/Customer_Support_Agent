import json
import os
from difflib import SequenceMatcher

faq_path = os.path.join(os.path.dirname(__file__), "../data/faq.json")
with open(faq_path, "r") as f:
    FAQ_DATA = json.load(f)["faqs"]

MOCK_ORDERS = {
    "ORD001": {"status": "Shipped", "item": "Wireless Headphones", "eta": "2 days"},
    "ORD002": {"status": "Processing", "item": "Running Shoes", "eta": "5 days"},
    "ORD003": {"status": "Delivered", "item": "Laptop Stand", "eta": "Already delivered"},
    "ORD004": {"status": "Cancelled", "item": "Phone Case", "eta": "N/A"},
}


def faq_lookup(user_query: str) -> str:
    best_score = 0
    best_answer = None

    for faq in FAQ_DATA:
        score = SequenceMatcher(
            None, user_query.lower(), faq["question"].lower()
        ).ratio()
        if score > best_score:
            best_score = score
            best_answer = faq["answer"]

    if best_score > 0.3:
        return best_answer
    return "I couldn't find a specific FAQ for your question."


def check_order_status(order_id: str) -> str:
    order_id = order_id.strip().upper()
    if order_id in MOCK_ORDERS:
        o = MOCK_ORDERS[order_id]
        return (
            f"Order {order_id}: {o['item']} — Status: {o['status']}. "
            f"ETA: {o['eta']}."
        )
    return f"No order found with ID '{order_id}'. Please double-check the order ID."


def escalate_to_human(reason: str) -> str:
    return (
        f"This conversation has been escalated to a human agent. "
        f"Reason: {reason}. "
        f"Our support team will contact you within 24 hours."
    )