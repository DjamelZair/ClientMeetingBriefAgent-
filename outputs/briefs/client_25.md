# Meeting brief: Client 25

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 47, with the bank for 6 years, recorded income about 80,000, individual segment, holds 4 products: Online account, Salary paid in, Pension paid in, Payroll account.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

- **Direct debit**, scores 29%. In the test month, 29% of the 1,281 clients scoring between 20% and 30% took it up. The score leans on: closed 3 products in the last six months; an active client; already holds a payroll account.
- **Credit card**, scores 18%. In the test month, 17% of the 1,080 clients scoring between 10% and 20% took it up. The score leans on: closed 3 products in the last six months; holds 4 products; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 4 November 2020.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 47, 4 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 4 products scored, highest Direct debit (29%)
5. `check_suitability`: Direct debit: allowed
6. `check_suitability`: Credit card: allowed
7. `check_review_due`: not due, next review 2020-11-04 (1617 days)
8. `draft_questions`: 2 questions drafted
