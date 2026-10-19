# Meeting brief: Client 06

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Older everyday account holders** (cluster 5): Often hold an everyday account (100%), long standing clients (about 14 years with the bank), older (average age 55).

Aged 47, with the bank for 21 years, recorded income about 765,000, individual segment, holds 4 products: Bills paid by direct debit, Investment account, Everyday account, Everyday plus account.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

- **Current account**, scores above 50%. In the test month, 45% of the 377 clients scoring between 50% and 100% took it up. The score leans on: closed 1 product in the last six months; already pays bills by direct debit; with the bank for 21 years.
- **Credit card**, scores 15%. In the test month, 17% of the 1,210 clients scoring between 10% and 20% took it up. The score leans on: closed 1 product in the last six months; with the bank for 21 years; holds 4 products.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 6 October 2020.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 45% of the 377 clients scoring between 50% and 100% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Still on the brief: Credit card. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Still on the brief: Credit card. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 47, 4 products held
2. `get_segment`: cluster 5, Older everyday account holders
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Current account (above 50%)
5. `check_suitability`: Current account: allowed
6. `check_suitability`: Credit card: allowed
7. `check_care`: care check: no signs in the data
8. `check_review_due`: not due, next review 2020-10-06 (1588 days)
9. `draft_questions`: 2 questions drafted, each with a reason and answer branches
