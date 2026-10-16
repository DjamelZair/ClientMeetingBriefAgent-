# Meeting brief: Client 28

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 41, with the bank for 4 years, recorded income about 389,000, individual segment, holds 1 product: Current account.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

- **Direct debit**, scores 24%. In the test month, 29% of the 1,281 clients scoring between 20% and 30% took it up. The score leans on: closed 1 product in the last six months; an active client; already holds a current account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 29 September 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 41, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Direct debit (24%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: not due, next review 2017-09-29 (485 days)
7. `draft_questions`: 2 questions drafted
