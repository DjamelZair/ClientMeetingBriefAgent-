<div align="center">

# Client meeting brief agent

###  &nbsp;[**OPEN THE LIVE INTERACTIVE PAGE**](https://djamelzair.github.io/ClientMeetingBriefAgent-/)&nbsp; 

**What should the advisor know before the client walks in?**

📓 [Read the walkthrough notebook](https://djamelzair.github.io/ClientMeetingBriefAgent-/notebook.html) &nbsp;·&nbsp; 💻 source code below

</div>

---

## What this is

I built this for my application to the CLUE team (Client Lifecycle Understanding Engine), which asked how I would use an AI agent to support a client advisor in their client interaction. My answer is a small agent that prepares the meeting and then gets out of the way.

Before a meeting it writes a one page brief with five parts:

1. **Who the client is**: their cluster and what changed recently (new products, closed products, a drop in activity, a move).
2. **What might help**: the products the model scores highest, each with what the score leans on and how often scores like it came true in the test month.
3. **What not to offer**: products that score high but fail a suitability check. A high score never overrides fit.
4. **What is due anyway**: whether the periodic client review (KYC/CDD) is coming up, so it can be covered in the same conversation.
5. **Questions to ask**: two or three questions about the client's situation, each with the signal it comes from
   (for example "Periodic review due in 88 days") and two or three likely answers that show how the brief would change.

The agent only prepares. The advisor decides.

## The data: real, public, plus a small synthetic layer

Client profiles and product holdings come from the public [Kaggle Santander Product Recommendation](https://www.kaggle.com/competitions/santander-product-recommendation) dataset: monthly snapshots of anonymised retail clients of a Spanish bank, January 2015 to May 2016. I work on a fixed sample of clients drawn with seed 42.

No public dataset has KYC review dates, risk profiles or vulnerability flags, so those few fields are **synthetic**: generated in code with a fixed seed, independently of the real data, and labelled as synthetic wherever they appear. The review intervals and rules are illustrative and made up for this prototype. Nothing here uses or describes any real bank's data, systems, products or processes, and the product names are generic.

## Results

The table below is written by the pipeline from `docs/data.json`, so it always matches the page.

<!-- results:start -->
- **Data:** 13,647,309 monthly rows for 956,645 clients over 17 months; I sample 200,000 clients with seed 42.
- **Segments:** k = 6, adjusted Rand index against a Gaussian mixture 0.707.
- **Products modelled:** 8 of 17; the rest have too few take ups.

Test month, clients who did not hold the product yet:

| Product | Take ups in test | PR AUC logistic | PR AUC LightGBM | PR AUC lift [95% CI] | ROC AUC LightGBM |
|---|---|---|---|---|---|
| Payroll account | 501 | 0.272 | 0.414 | +0.142 [+0.104, +0.174] | 0.939 |
| Online account | 583 | 0.185 | 0.369 | +0.184 [+0.156, +0.210] | 0.941 |
| Salary paid into the account | 1,182 | 0.294 | 0.357 | +0.063 [+0.043, +0.081] | 0.961 |
| Pension paid into the account | 1,184 | 0.278 | 0.347 | +0.068 [+0.046, +0.087] | 0.950 |
| Bills paid by direct debit | 2,190 | 0.256 | 0.318 | +0.061 [+0.049, +0.076] | 0.955 |
| Current account | 784 | 0.243 | 0.300 | +0.057 [+0.037, +0.080] | 0.912 |
| Credit card | 955 | 0.135 | 0.192 | +0.057 [+0.040, +0.072] | 0.961 |
| Plus account | 113 | 0.088 | 0.102 | +0.014 [-0.014, +0.038] | 0.982 |

- **At the default threshold of 10.0%:** 9,885 suggestions for 8,825 clients; the guardrail held back 852.
- **Likely already in progress** (salary, pension or payroll already arriving): 3,298, shown separately and not as suggestions.
- **Reviews (synthetic):** 20,678 clients (10.4%) have a periodic review due within 90 days, 8,062 of them overdue; 579 clients with a suggestion could cover a due review in the same meeting.
<!-- results:end -->

## How it works

```
client_brief_agent/
  config.py             every path, seed and knob in one place
  data/load.py          raw parquet parts into a slim monthly panel for the sampled clients
  data/convert.py       the official train_ver2.csv into those parquet parts
  data/synthetic.py     the made up compliance layer (review dates, risk profile, vulnerability)
  features/build.py     behaviour features and change flags at month T from history up to T minus 1 only
  models/segment.py     k means for k = 2 to 10, silhouette plus elbow, gaussian mixture for agreement
  models/propensity.py  lightgbm per product, logistic regression as the baseline, paired bootstrap cis
  models/explain.py     shap for lightgbm, exact linear contributions for logistic regression, plain phrases
  models/tune.py        optuna search on the validation month; a product only switches when it beats my default
  agent/suitability.py  the guardrail rules, one small function each, with a plain reason
  agent/branches.py     every question's reason and its answer branches, as rules you can read
  agent/steps.py        what each of the five steps reads, runs, returns, and the rule or model behind it
  agent/feedback.py     what advisors record; a product declined less than 182 days ago is not raised again
  agent/follow_up.py    a template follow up draft for the client, never sent, never naming a held back product
  agent/tools.py        the tools the agent calls, every call logged
  agent/run.py          assembles the five part brief, the product holdings and renders it as markdown
  report/fairness.py    suggestion and held back rates and ranking quality per audit group, with plain flags
  report/               figures (300 dpi), tables, docs/data.json and the briefs
main.py                 runs everything end to end
docs/                   the github pages site: brief/ (the agent and the brief) and model.html read data.json
                        brief/ takes ?ds=ibm|mercury|linear (type, space, depth) and ?scheme=S1 to S4 (colour)
outputs/                figures/, tables/, briefs/
```

A few choices worth knowing about:

- **Propensity means take up, not holding.** For a target month I only use history up to the month before, and the label is "took it up this month". Training only on clients who do not hold the product yet is what makes the score useful; predicting who already has a current account is easy and pointless.
- **Time split, not random split.** Training on target months up to March 2016, validation on April, test on May.
- **Sex and place of birth are not model features.** A duty of care tool should not score anyone on those.
- **I tried isotonic calibration and dropped it.** It did not improve the Brier score, cost ranking quality and pushed some scores to exactly 100%. The brief shows each score next to the observed take up rate in its score band instead.
- **The agent runs fully offline** with deterministic templates. If `ANTHROPIC_API_KEY` is set and the `anthropic` package is installed, it may use Claude only to rephrase the conversation questions, with the structured facts passed in and an instruction never to add any.

## Run it yourself

```bash
pip install -r requirements.txt
```

**Get the data.** The raw data is not in this repository and never will be. Download it yourself from the competition page after accepting its rules:

1. Sign in to Kaggle, open the [competition data page](https://www.kaggle.com/competitions/santander-product-recommendation/data) and accept the rules.
2. Download the training file, `train_ver2.csv`, either from the page or with the Kaggle CLI:
   `kaggle competitions download -c santander-product-recommendation`
3. Unzip it and convert it into the parquet parts the pipeline reads:

```bash
python -m client_brief_agent.data.convert path/to/train_ver2.csv
```

That writes `data/raw/santander/parquet/part.*.parquet`. If you already have the data as parquet parts, put them there directly.

**Run the pipeline and the tests:**

```bash
python main.py          # about ten minutes on 8 cores; rebuilds everything
python main.py --reuse  # reuses the cached panel, snapshots and models
python main.py --tune   # runs the validation month search first, then retrains with what it chose
python -m pytest -q
python -m client_brief_agent.report.notebook   # reruns the walkthrough and exports docs/notebook.html
```

Then serve the page locally (it fetches `data.json`, so opening the file directly will not work):

```bash
cd docs && python -m http.server 8000
```

## What this cannot tell you

The page keeps this to five points in its Limits tab. In short: the scores are correlations in 2016 Spanish retail data, not intent; salary, pension and payroll products move together, so some "suggestions" are things already in progress; the compliance layer is made up; the test is one month; and nothing here has been checked with a real advisor.

## Licence

The code is MIT licensed. The data is not mine and is not redistributed here; its use is governed by the Kaggle competition rules.
