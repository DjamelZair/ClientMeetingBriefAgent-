# Meeting brief: Client 27

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 62, with the bank for 6 years, recorded income about 56,000, top tier segment, holds 3 products: Current account, Online account, Term deposit.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 2 products in the last three months.
- Moved to a different province in the last six months.

## 2. What might help

- **Direct debit**, scores 16%. In the test month, 15% of the 2,723 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; an active client; already holds a current account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 14 March 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You have moved recently. Is there anything we can help you settle, such as addresses or regular payments?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 62, 3 products held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 6 products scored, highest Direct debit (16%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: not due, next review 2019-03-14 (1016 days)
7. `draft_questions`: 3 questions drafted
