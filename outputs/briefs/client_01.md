# Meeting brief: Client 01

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 25, with the bank for 3 years, recorded income about 38,000, student segment, holds 1 product: Payroll account.

Recent changes:
- No notable changes in the last six months.

## 2. What might help

- **Current account**, scores above 50%. In the test month, 45% of the 377 clients scoring between 50% and 100% took it up. The score leans on: already holds a payroll account; aged 25; holds 1 product.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 18 October 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 45% of the 377 clients scoring between 50% and 100% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.
2. What matters most to you financially over the next year?
   *Open. Why: No due review, recent change or suggestion to start from, so an open question.*
   - If "Raises something specific": Record what the client raises; the brief has no data on it.
   - If "Nothing in particular": No change to the brief.

## How this brief was prepared

1. `get_profile`: aged 25, 1 product held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: no change flags
4. `get_propensities`: 7 products scored, highest Current account (above 50%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2019-10-18 (1234 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
