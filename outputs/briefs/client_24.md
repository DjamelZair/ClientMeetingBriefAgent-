# Meeting brief: Client 24

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 54, with the bank for 14 years, recorded income about 556,000, individual segment, holds 3 products: Direct debit, Tax payment account, Everyday plus account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Current account**, scores above 50%. In the test month, 44% of the 456 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last six months; already pays bills by direct debit; added 2 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 13 April 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on your everyday money at the moment?

## How this brief was prepared

1. `get_profile`: aged 54, 3 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Current account (above 50%)
5. `check_suitability`: Current account: allowed
6. `check_review_due`: not due, next review 2019-04-13 (1046 days)
7. `draft_questions`: 3 questions drafted
