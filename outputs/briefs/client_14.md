# Meeting brief: Client 14

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 33, with the bank for 15 months, recorded income about 48,000, individual segment, holds 1 product: Current account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 2 products in the last three months.

## 2. What might help

- **Direct debit**, scores above 50%. In the test month, 66% of the 152 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last six months; an active client; added 3 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 4 July 2016, 33 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 33, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Direct debit (above 50%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: due soon, next review 2016-07-04 (33 days)
7. `draft_questions`: 3 questions drafted
