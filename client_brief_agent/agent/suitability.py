"""suitability rules: a high score never overrides fit.

every rule is one small object with a name, the products it covers, a condition and a plain
reason. the same condition runs on a single client (a dict of scalars) and on the whole
population (a frame of columns), so the brief and the guardrail curve can never disagree.
"""
from dataclasses import dataclass
from typing import Callable

import numpy as np
import pandas as pd

from client_brief_agent import config

FACT_COLUMNS = ["age", "income_missing", "flag_activity_drop", "deceased", "vulnerable",
                "risk_profile_done", "risk_appetite", "review_overdue"]


@dataclass(frozen=True)
class Rule:
    name: str
    applies: Callable[[str], bool]
    condition: Callable[[object], object]
    reason: str


def _credit(product):
    return product in config.CREDIT_PRODUCTS


def _investment(product):
    return product in config.INVESTMENT_PRODUCTS


def _any(product):
    return True


def _not_basic(product):
    return product not in config.BASIC_PRODUCTS


# conditions only use operators that work the same on a scalar and on a series
RULES = [
    Rule("deceased", _any,
         lambda f: f["deceased"],
         "The client is recorded as deceased, so nothing is suggested."),
    Rule("under_18_basic_only", _not_basic,
         lambda f: f["age"] < 18,
         "The client is under 18, so only basic accounts are suggested."),
    Rule("credit_under_18", _credit,
         lambda f: f["age"] < 18,
         "The client is under 18, so credit is not suggested."),
    Rule("credit_activity_drop", _credit,
         lambda f: f["flag_activity_drop"],
         "Account activity has dropped in the last three months, so credit is not suggested."),
    Rule("credit_vulnerable", _credit,
         lambda f: f["vulnerable"],
         "The client is marked as possibly vulnerable, so credit is not suggested."),
    Rule("credit_income_missing", _credit,
         lambda f: f["income_missing"],
         "No income is recorded, so affordability cannot be checked and credit is not suggested."),
    Rule("investment_no_risk_profile", _investment,
         lambda f: np.logical_not(f["risk_profile_done"]),
         "There is no risk profile on file, so investment products are not suggested."),
    Rule("investment_account_cautious", lambda p: p == "investment_account",
         lambda f: f["risk_appetite"] == "cautious",
         "The risk profile is cautious, so an investment account does not fit."),
    # my two additions: vulnerable clients get no investment suggestions either, and an overdue
    # periodic review comes before any new product
    Rule("investment_vulnerable", _investment,
         lambda f: f["vulnerable"],
         "The client is marked as possibly vulnerable, so investment products are not suggested."),
    Rule("review_overdue", _any,
         lambda f: f["review_overdue"],
         "The periodic client review is overdue, so it should be completed before any new product."),
]

RULE_NAMES = [r.name for r in RULES]
RULE_REASONS = {r.name: r.reason for r in RULES}


def _as_bool(series):
    return series.astype("boolean").fillna(False).to_numpy(dtype=bool)


def client_facts(snapshot, synthetic, meeting_date=config.MEETING_DATE):
    """the facts the rules read, one row per client in the snapshot."""
    idx = snapshot.index
    facts = pd.DataFrame(index=idx)
    # the raw age, so a missing age is unknown rather than the median the models were given
    age_col = "age_raw" if "age_raw" in snapshot else "age"
    facts["age"] = snapshot[age_col].astype("float64") if age_col in snapshot else np.nan
    if "income_missing" in snapshot:
        facts["income_missing"] = snapshot["income_missing"].fillna(1).astype(float) > 0.5
    else:
        facts["income_missing"] = snapshot["income"].isna()
    for col in ["flag_activity_drop", "deceased"]:
        facts[col] = snapshot[col].fillna(0).astype(float) > 0.5 if col in snapshot else False

    syn = synthetic.reindex(idx)
    # a client missing from the synthetic layer is treated cautiously: no risk profile
    facts["vulnerable"] = _as_bool(syn["vulnerable"])
    facts["risk_profile_done"] = _as_bool(syn["risk_profile_done"])
    facts["risk_appetite"] = syn["risk_appetite"].astype(object).where(syn["risk_appetite"].notna(), None)
    meeting = pd.Timestamp(meeting_date)
    facts["review_overdue"] = (pd.to_datetime(syn["next_kyc_review"]) < meeting).fillna(False).astype(bool)
    return facts[FACT_COLUMNS]


def facts_row(facts, cid):
    return facts.loc[cid].to_dict()


def check(facts_one, product):
    """per client check: {'allowed', 'rules_fired': [{'rule', 'reason'}]}."""
    fired = [{"rule": r.name, "reason": r.reason} for r in RULES
             if r.applies(product) and bool(r.condition(facts_one))]
    return {"allowed": not fired, "rules_fired": fired}


def rule_matrix(facts, product):
    """clients x rules, True where that rule blocks this product."""
    out = pd.DataFrame(False, index=facts.index, columns=RULE_NAMES)
    for r in RULES:
        if r.applies(product):
            out[r.name] = np.asarray(r.condition(facts), dtype=bool)
    return out


def blocked_mask(facts, products):
    """clients x products, True where any rule blocks the product. vectorised twin of check()."""
    return pd.DataFrame({p: rule_matrix(facts, p).any(axis=1).to_numpy() for p in products},
                        index=facts.index)
