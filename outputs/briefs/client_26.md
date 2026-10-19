# Meeting brief: Client 26

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 56, with the bank for 6 years, recorded income about 161,000, top tier segment, holds 3 products: Current account, Term deposit, Everyday plus account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.
- Client segment changed in the last six months.

## 2. What might help

- **Credit card**, scores 23%. In the test month, 25% of the 401 clients scoring between 20% and 30% took it up. The score leans on: closed 2 products in the last six months; an active client; aged 56.
- **Bills paid by direct debit**, scores 18%. In the test month, 14% of the 2,684 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; an active client; added 2 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 31 August 2016.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 1 new product in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Nothing new is raised. Help with the set up.
3. How do you usually pay for larger purchases?
   *Top suggestion. Why: In the test month, 25% of the 401 clients scoring between 20% and 30% took up credit card. This client has no credit card with this bank.*
   - If "Open to talking about it": Discuss Credit card if the client wants to.
   - If "Already arranged elsewhere": Still on the brief: Bills paid by direct debit. Credit card is arranged at another bank. Record where it is arranged and do not raise Credit card again in this meeting. Record it as declined: the brief will not raise Credit card again for 182 days.
   - If "Not a priority now": Still on the brief: Bills paid by direct debit. Credit card is not a priority for the client now. Record it as declined: the brief will not raise Credit card again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 56, 3 products held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 7 products scored, highest Credit card (23%)
5. `check_suitability`: Credit card: allowed
6. `check_suitability`: Bills paid by direct debit: allowed
7. `check_care`: care check: no signs in the data
8. `check_review_due`: not due, next review 2016-08-31 (91 days)
9. `draft_questions`: 3 questions drafted, each with a reason and answer branches
