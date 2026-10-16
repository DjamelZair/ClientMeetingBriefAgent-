# Meeting brief: Client 37

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 32, with the bank for 8 months, income not recorded, individual segment, holds 1 product: Payroll account.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 4 products in the last three months.

## 2. What might help

- **Direct debit**, scores 17%. In the test month, 15% of the 2,723 clients scoring between 10% and 20% took it up. The score leans on: closed 6 products in the last six months; an active client; already holds a payroll account.

Likely already in progress:
- **Pension paid in**, scores 47%. The client already has a payroll account, so this is likely already in progress rather than something to suggest.
- **Salary paid in**, scores 41%. The client already has a payroll account, so this is likely already in progress rather than something to suggest.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 23 April 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 32, 1 product held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Pension paid in (47%)
5. `check_suitability`: Pension paid in: allowed
6. `check_linked`: Pension paid in: in progress
7. `check_suitability`: Salary paid in: allowed
8. `check_linked`: Salary paid in: in progress
9. `check_suitability`: Direct debit: allowed
10. `check_review_due`: not due, next review 2019-04-23 (1056 days)
11. `draft_questions`: 3 questions drafted
