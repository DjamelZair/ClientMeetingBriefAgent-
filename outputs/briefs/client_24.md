# Meeting brief: Client 24

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 47, with the bank for 16 years, recorded income about 208,000, individual segment, holds 4 products: Online account, Credit card, Payroll account, Tax payment account.

Recent changes:
- No notable changes in the last six months.

## 2. What might help

- **Bills paid by direct debit**, scores 10%. In the test month, 14% of the 2,684 clients scoring between 10% and 20% took it up. The score leans on: closed 1 product in the last six months; an active client; already holds a payroll account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 5 April 2021.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How do you keep track of your regular bills?
   *Top suggestion. Why: In the test month, 14% of the 2,684 clients scoring between 10% and 20% took up bills paid by direct debit. This client has no direct debits set up here.*
   - If "Open to talking about it": Discuss Bills paid by direct debit if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Bills paid by direct debit is arranged at another bank. Record where it is arranged and do not raise Bills paid by direct debit again in this meeting. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.
   - If "Not a priority now": Nothing new is raised. Bills paid by direct debit is not a priority for the client now. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.
2. What matters most to you financially over the next year?
   *Open. Why: No due review, recent change or suggestion to start from, so an open question.*
   - If "Raises something specific": Record what the client raises; the brief has no data on it.
   - If "Nothing in particular": No change to the brief.

## How this brief was prepared

1. `get_profile`: aged 47, 4 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: no change flags
4. `get_propensities`: 5 products scored, highest Bills paid by direct debit (10%)
5. `check_suitability`: Bills paid by direct debit: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2021-04-05 (1769 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
