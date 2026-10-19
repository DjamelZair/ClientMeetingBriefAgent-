# Meeting brief: Client 37

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Everyday inactive clients** (cluster 4): Everyday individual segment (98%), mostly inactive (6% active), rarely hold a current account (28%).

Aged 55, with the bank for 7 months, income not recorded, holds no products.

Recent changes:
- Client segment changed in the last six months.

## 2. What might help

- **Current account**, scores 18%. In the test month, 12% of the 722 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; with the bank for 7 months; aged 55.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 14 October 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Your situation with us has changed recently. Do your accounts still fit how you live now?
   *Recent change. Why: Client segment changed in the last six months.*
   - If "My work or studies changed": Update work and income details.
   - If "Nothing has changed": No change to the brief.
2. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 12% of the 722 clients scoring between 10% and 20% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 55, no products held
2. `get_segment`: cluster 4, Everyday inactive clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 8 products scored, highest Current account (18%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2017-10-14 (500 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
