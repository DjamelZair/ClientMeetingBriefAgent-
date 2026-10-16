# Meeting brief: Client 26

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 60, with the bank for 6 years, recorded income about 546,000, individual segment, holds 2 products: Current account, Direct debit.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Credit card**, scores 10%. In the test month, 17% of the 1,080 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; an active client; aged 60.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 13 December 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on paying for larger purchases and spreading costs at the moment?

## How this brief was prepared

1. `get_profile`: aged 60, 2 products held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 6 products scored, highest Credit card (10%)
5. `check_suitability`: Credit card: allowed
6. `check_review_due`: not due, next review 2019-12-13 (1290 days)
7. `draft_questions`: 3 questions drafted
