# Meeting brief: Client 23

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 74, with the bank for 15 years, recorded income about 285,000, individual segment, holds 1 product: Bills paid by direct debit.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

- **Current account**, scores 33%. In the test month, 33% of the 485 clients scoring between 30% and 50% took it up. The score leans on: closed 2 products in the last six months; already pays bills by direct debit; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 8 September 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 33% of the 485 clients scoring between 30% and 50% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 74, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Current account (33%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2019-09-08 (1194 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
