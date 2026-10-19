"""every path, seed and knob in one place, so nothing hides inside a module."""
from pathlib import Path

SEED = 42

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw" / "santander" / "parquet"
INTERIM_DIR = ROOT / "data" / "interim"
# what advisors record in meetings; there are none in this prototype, so the file usually does not exist
ADVISOR_LOG_PATH = ROOT / "data" / "advisor_log.csv"
DECLINE_COOLDOWN_DAYS = 182
OUTPUTS = ROOT / "outputs"
FIG_DIR = OUTPUTS / "figures"
TABLE_DIR = OUTPUTS / "tables"
BRIEF_DIR = OUTPUTS / "briefs"
DOCS_DIR = ROOT / "docs"
DOCS_FIG_DIR = DOCS_DIR / "figures"

# the machine has about 6 gb free, so i work on a fixed sample of clients
N_CLIENTS = 200_000

# a target month T uses history up to T-1 only. label = took the product up in T
TRAIN_TARGETS = ["2015-08", "2015-09", "2015-10", "2015-11", "2015-12",
                 "2016-01", "2016-02", "2016-03"]
VAL_TARGET = "2016-04"
TEST_TARGET = "2016-05"
# the brief looks ahead to june 2016, which the data does not contain, so it has no label
BRIEF_TARGET = "2016-06"
MEETING_DATE = "2016-06-01"

# raw column -> short code. only the codes kept in PRODUCTS get a model
PRODUCT_COLUMNS = {
    "ind_cco_fin_ult1": "current_account",
    "ind_ecue_fin_ult1": "online_account",
    "ind_tjcr_fin_ult1": "credit_card",
    "ind_recibo_ult1": "direct_debit",
    "ind_nomina_ult1": "salary_deposit",
    "ind_nom_pens_ult1": "pension_deposit",
    "ind_cno_fin_ult1": "payroll_account",
    "ind_reca_fin_ult1": "tax_account",
    "ind_dela_fin_ult1": "term_deposit",
    "ind_fond_fin_ult1": "investment_fund",
    "ind_valo_fin_ult1": "investment_account",
    "ind_plan_fin_ult1": "pension_plan",
    "ind_ctma_fin_ult1": "plus_account",
    "ind_ctop_fin_ult1": "particular_account",
    "ind_ctpp_fin_ult1": "particular_plus_account",
    "ind_hip_fin_ult1": "mortgage",
    "ind_pres_fin_ult1": "personal_loan",
}

# plain names shown to the advisor
PRODUCT_LABELS = {
    "current_account": "Current account",
    "online_account": "Online account",
    "credit_card": "Credit card",
    "direct_debit": "Bills paid by direct debit",
    "salary_deposit": "Salary paid into the account",
    "pension_deposit": "Pension paid into the account",
    "payroll_account": "Payroll account",
    "tax_account": "Tax payment account",
    "term_deposit": "Term deposit",
    "investment_fund": "Investment fund",
    "investment_account": "Investment account",
    "pension_plan": "Pension plan",
    "plus_account": "Plus account",
    "particular_account": "Everyday account",
    "particular_plus_account": "Everyday plus account",
    "mortgage": "Mortgage",
    "personal_loan": "Personal loan",
}

# a product only gets a model if the sample has enough take ups to learn and test on
MIN_TEST_POSITIVES = 100
MIN_TRAIN_POSITIVES = 500

# products the guardrail treats as credit or as investment
CREDIT_PRODUCTS = {"credit_card", "mortgage", "personal_loan"}
INVESTMENT_PRODUCTS = {"investment_fund", "investment_account", "pension_plan"}

# illustrative only, made up for this prototype, not any bank's policy
KYC_INTERVAL_YEARS = {"low": 5, "medium": 3, "high": 1}
REVIEW_WINDOW_DAYS = 90

DEFAULT_THRESHOLD = 0.10
N_SHOWCASE = 40

# ---- agent b (models): knobs for segmentation and propensity ----
N_JOBS = 4
MODEL_DIR = INTERIM_DIR / "models"
SEGMENT_K_RANGE = list(range(2, 11))
SEGMENT_SELECTION_SAMPLE = 30_000
SILHOUETTE_SAMPLE = 10_000
# if two k are this close on silhouette i treat them as tied and let the elbow decide
SILHOUETTE_TIE = 0.01
PCA_PLOT_SAMPLE = 3_000
# a feature only enters a cluster description if its cluster mean sits this many sds from the overall mean
SEGMENT_Z_THRESHOLD = 0.5
N_BOOTSTRAP = 200
SHAP_SAMPLE = 5_000
LGBM_PARAMS = {
    "n_estimators": 2000,
    "learning_rate": 0.05,
    "num_leaves": 31,
    "min_child_samples": 100,
    "subsample": 0.8,
    "subsample_freq": 1,
    "colsample_bytree": 0.8,
    "reg_lambda": 1.0,
}
EARLY_STOPPING_ROUNDS = 100

# agent c additions: the brief, the guardrail and the export
# basic accounts are the only thing a client under 18 can be suggested
BASIC_PRODUCTS = {"current_account", "online_account", "particular_account"}
# a one page brief, so i show at most three suggestions and three blocked products
MAX_SUGGESTIONS = 3
MAX_BLOCKED_SHOWN = 3
MAX_QUESTIONS = 3
# thresholds for the guardrail curve, 0.01 to 0.60
GUARDRAIL_THRESHOLDS = [round(i / 100, 2) for i in range(1, 61)]
# only used when an api key is set and the anthropic package is installed
CLAUDE_MODEL = "claude-sonnet-5-5"

# ---- added by the data and features step (agent a) ----
# synthetic compliance layer, illustrative probabilities only
KYC_CLASS_PROBS = {"low": 0.70, "medium": 0.25, "high": 0.05}
# last review is spread over the interval plus this many days, so a small share is already overdue
KYC_OVERDUE_SLACK_DAYS = 60
RISK_PROFILE_DONE_PROB = 0.60
RISK_PROFILE_MAX_AGE_DAYS = 3 * 365
RISK_APPETITE_PROBS = {"cautious": 0.35, "balanced": 0.50, "adventurous": 0.15}
VULNERABLE_PROB = 0.03
# channel one hots: the 8 most common named entry channels in the sample at 2015-07, before every target,
# so the columns never move between snapshots. features.build.top_channels recomputes it as a check
CHANNEL_REFERENCE_MONTH = "2015-07"
CHANNEL_FEATURES = ["KHE", "KAT", "KFC", "KFA", "KHK", "KHD", "KAS", "KAY"]

# ---- agent b (models), added on the lead's request ----
# protected attributes: a duty of care tool should not score or segment on sex or place of birth,
# and the source does not document how sex is coded anyway
EXCLUDED_FEATURES = ["sex_male", "foreign_birth"]

# ---- agent c, second round: score display, linked products, public showcase ----
# fixed calibration band edges, the same ones the bands table uses
BAND_EDGES = [0.0, 0.01, 0.02, 0.05, 0.10, 0.20, 0.30, 0.50, 1.0]
MIN_BAND_CLIENTS = 30
# a score of 50% or more is only ever shown as "above 50%"
SCORE_DISPLAY_CAP = 0.50
# salary, pension and payroll move together: holding one means the others are likely under way
LINKED_INCOME_PRODUCTS = {"payroll_account", "salary_deposit", "pension_deposit"}

# the data counts these as products, but a bank does not sell them: they say where the client's money flows.
# the brief asks about them instead of offering them
MONEY_FLOWS = {"salary_deposit", "pension_deposit", "direct_debit"}
# salary and pension paid in start in the same month for almost every client in the data, so the brief shows
# them as one signal: the second one found is folded into the first
SAME_SIGNAL = {"salary_deposit": "pension_deposit", "pension_deposit": "salary_deposit"}
INCOME_ROUNDING = 1000
CODE_URL = "https://github.com/DjamelZair/ClientMeetingBriefAgent"
MAX_PCA_POINTS = 3000

# ---- round three: holdings by category, tuning, fairness audit ----
# how the 17 products group in the client panel. insurance has no column in the santander data,
# so it is listed with no products and the page says so instead of inventing anything
PRODUCT_CATEGORIES = [
    ("Accounts", ["current_account", "payroll_account", "online_account", "plus_account",
                  "particular_account", "particular_plus_account"]),
    ("Cards", ["credit_card"]),
    ("Payments and income", ["direct_debit", "tax_account", "salary_deposit"]),
    ("Savings and deposits", ["term_deposit"]),
    ("Investments and funds", ["investment_fund", "investment_account"]),
    ("Pensions", ["pension_plan", "pension_deposit"]),
    ("Loans and mortgage", ["personal_loan", "mortgage"]),
    ("Insurance", []),
]

# hyperparameter search: optuna tpe, tuned on the validation month only, the test month stays untouched
TUNING_TRIALS = 30
# trials train on a fixed random share of the training rows to keep the search affordable on this
# machine; the chosen setting is then refitted on all training rows
TUNING_TRAIN_ROWS = 400_000
TUNED_PARAMS_PATH = OUTPUTS / "tables" / "lgbm_tuned_params.json"

# fairness audit: groups are only used to check the output, never as model features
FAIRNESS_MIN_POSITIVES = 30
# a group's suggestion or held back rate outside these ratios of the overall rate gets flagged
FAIRNESS_RATE_RATIO = (0.8, 1.25)
# a group's roc auc this far below the overall roc auc for a product gets flagged
FAIRNESS_AUC_GAP = 0.05
AGE_BANDS = [(0, 25, "under 25"), (25, 45, "25 to 44"), (45, 65, "45 to 64"), (65, 200, "65 and over")]
