"""what each of the agent's five steps reads, runs, returns, and which rule or model sits behind it.

the page and the notebook show this next to the logged calls, so a reviewer can see what the agent did and
why without reading the code. the knobs come from config, never typed in twice.
"""
from client_brief_agent import config


def step_specs(k=None, n_features=None):
    """k: the chosen number of client groups; n_features: how many model features the propensity models use."""
    years = config.KYC_INTERVAL_YEARS
    return [
        {"n": 1, "name": "Get segment",
         "tools": ["get_profile", "get_segment", "get_recent_changes"],
         "reads": ["age", "tenure", "recorded income", "client segment", "products held",
                   "products added and closed in the last three and six months", "activity three months ago",
                   "province history"],
         "returns": "The client's group with a plain description, the profile shown to the advisor, and change flags.",
         "rule_or_model": (f"k means with k = {k} on standardised profile and holding features, chosen by silhouette. "
                           "Change flags are fixed rules, for example: at least one product added in the last three months.")
                          if k else "k means on standardised profile and holding features; change flags are fixed rules."},
        {"n": 2, "name": "Get propensities",
         "tools": ["get_propensities"],
         "reads": [f"{n_features} behaviour and profile features" if n_features else "behaviour and profile features",
                   "history up to the month before the meeting only", "sex and place of birth are never read"],
         "returns": "A take up score for every modelled product the client does not hold yet, with the observed "
                    "take up rate of that score band in the test month and what the score leans on.",
         "rule_or_model": "One LightGBM model per product, trained on clients who did not hold it yet. "
                          "SHAP contributions turned into short phrases for the reasons."},
        {"n": 3, "name": "Check suitability",
         "tools": ["check_suitability", "check_linked", "check_care"],
         "reads": ["age", "income recorded or not", "activity trend", "vulnerability flag (synthetic)",
                   "risk profile and appetite (synthetic)", "periodic review status (synthetic)",
                   "salary, pension and payroll already arriving"],
         "returns": "Products held back with the rule that fired and its reason, products that are likely "
                    "already in progress, and whether the brief should open with a care check.",
         "rule_or_model": f"Ten transparent guardrail rules, checked for every product scoring {round(config.DEFAULT_THRESHOLD * 100)}% "
                          "or more, plus one linked income rule. A high score never overrides a rule. The care check opens the brief "
                          "when the client is marked possibly vulnerable or their activity dropped."},
        {"n": 4, "name": "Check review due",
         "tools": ["check_review_due"],
         "reads": ["KYC risk class (synthetic)", "last and next periodic review date (synthetic)", "meeting date"],
         "returns": "Whether the periodic review is overdue, due within the window or not due, and the days until it.",
         "rule_or_model": (f"Due when the next review falls within {config.REVIEW_WINDOW_DAYS} days of the meeting. "
                           f"Illustrative intervals: {years['low']} years for low risk, {years['medium']} for medium, "
                           f"{years['high']} for high.")},
        {"n": 5, "name": "Draft questions",
         "tools": ["draft_questions"],
         "reads": ["review status", "change flags", "the top suggestion and its score band"],
         "returns": "Two or three questions, each with the reason it is asked and two or three likely answers "
                    "that show how the brief would change.",
         "rule_or_model": "Fixed templates in priority order (due review, recent changes, top suggestion, open) and "
                          "fixed answer rules in branches.py. Claude may only rephrase the wording, when a key is set."},
    ]


# the claims the page may make about what is different, each one backed by something the pipeline does
NOVELTY = [
    {"point": "Says what not to offer, and why.",
     "contrast": "A typical recommender only ranks.",
     "backed_by": "agent/suitability.py: ten rules with a plain reason each."},
    {"point": "Covers a due review in the same meeting.",
     "contrast": "Reviews usually run separately.",
     "backed_by": "agent/tools.py check_review_due, on a synthetic review layer."},
    {"point": "Quotes what happened, not the raw score.",
     "contrast": "The share of similar clients who took it up.",
     "backed_by": "the observed take up rate per score band in the test month."},
    {"point": "Each question says why it is asked.",
     "contrast": "Each likely answer shows how the brief would change.",
     "backed_by": "agent/branches.py: fixed answer rules, no model decides."},
    {"point": "Logs every tool call.",
     "contrast": "The advisor decides; nothing is sent to the client.",
     "backed_by": "the tool log in every brief."},
]
