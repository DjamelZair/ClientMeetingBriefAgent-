"""a draft follow up message for the client, from a fixed template.

the advisor checks and sends it, or not: nothing here is ever sent. it is a template on purpose, not a
language model, so it can only say what the brief says. two hard rules, both tested: it never names a
product that is held back, and it never repeats an internal note (those are for the advisor only).
"""

from client_brief_agent import config

LABEL = "Draft for the advisor to check. Not sent."

# how each item reads in a message to the client; anything not listed falls back to "a <label>"
CLIENT_WORDS = {
    "online_account": "an online account",
    "salary_deposit": "having your salary paid into your account here",
    "pension_deposit": "having your pension paid into your account here",
    "direct_debit": "paying your bills by direct debit from your account here",
}
_BY_LABEL = {v: k for k, v in config.PRODUCT_LABELS.items()}


def words(label):
    code = _BY_LABEL.get(label)
    if code in CLIENT_WORDS:
        return CLIENT_WORDS[code]
    noun = label.lower()
    return ("an " if noun[0] in "aeiou" else "a ") + noun


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def draft(meeting, products=(), flows=(), review=False, support=False, held_back=()):
    """meeting: the meeting date in words. products: labels the brief still suggests. flows: money flows
    worth asking about. review: a periodic review is part of the meeting. support: the client may be in
    financial difficulty, so the message offers help and names no product at all."""
    held = set(held_back)
    products = [p for p in products if p not in held]
    flows = [f for f in flows if f not in held]
    lines = ["Hello,", "", f"Thank you for meeting with us on {meeting}."]
    if support:
        lines.append("If money is tight at the moment, we are here to help. You can always contact me to talk it "
                     "through, with no obligation.")
    else:
        if products:
            lines.append(f"We talked briefly about {_join([words(p) for p in products])}. There is no obligation; "
                         "let me know if you would like more information.")
        if flows:
            lines.append(f"If you are interested in {_join([words(f) for f in flows])}, I can help set that up.")
    if review:
        lines.append("As discussed, we will finish updating your details as part of the periodic review.")
    lines += ["", "Kind regards,", "[advisor name]"]
    return "\n".join(lines)
