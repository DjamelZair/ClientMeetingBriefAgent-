"""what advisors record in meetings, and the one rule that reads it.

there are no real advisors in this prototype, so the log starts empty and nothing is learned from it. the
rule is still real and tested: when a client declined a product in a meeting, the brief does not raise it
again until the cooldown has passed. learning from these records (for example as a feature or a negative
label for the propensity models) is a next step that needs real logs; i do not fake it with made up ones.
"""
import pandas as pd

from client_brief_agent import config

COLUMNS = ["client_id", "product", "answer", "date"]
# the answers that mean "do not raise this again for now"
DECLINE_ANSWERS = {"Already arranged elsewhere", "Not a priority now"}
REASON = f"The client declined it in a meeting less than {config.DECLINE_COOLDOWN_DAYS} days ago, so it is not raised again yet."


def empty():
    return pd.DataFrame(columns=COLUMNS)


def load(path=config.ADVISOR_LOG_PATH):
    """the advisor log, or an empty one when no advisor has recorded anything."""
    try:
        return pd.read_csv(path, dtype={"product": str, "answer": str})[COLUMNS]
    except FileNotFoundError:
        return empty()


def record(log, client_id, product, answer, date):
    """one more row; the caller decides where to save it."""
    row = pd.DataFrame([{"client_id": client_id, "product": product, "answer": answer, "date": date}])
    return pd.concat([log, row], ignore_index=True) if len(log) else row


def declined(log, client_id, product, meeting_date):
    """True when this client declined this product within the cooldown before the meeting."""
    if log is None or not len(log):
        return False
    rows = log[(log["client_id"] == client_id) & (log["product"] == product) & log["answer"].isin(DECLINE_ANSWERS)]
    if not len(rows):
        return False
    days = (pd.Timestamp(meeting_date) - pd.to_datetime(rows["date"])).dt.days
    return bool(((days >= 0) & (days < config.DECLINE_COOLDOWN_DAYS)).any())
