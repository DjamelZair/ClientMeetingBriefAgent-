# Meeting brief: Client 04

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 45, with the bank for 17 years, recorded income about 81,000, individual segment, holds 6 products: Online account, Credit card, Direct debit, Tax payment account, Pension plan, Everyday account.

Recent changes:
- Took up 3 new products in the last three months.
- Closed 3 products in the last three months.

## 2. What might help

- **Payroll account**, scores above 50%. In the test month, 72% of the 242 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.
- **Salary paid in**, scores above 50%. In the test month, 56% of the 338 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.
- **Pension paid in**, scores above 50%. In the test month, 55% of the 273 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 21 April 2018.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on where your salary is paid at the moment?

## How this brief was prepared

1. `get_profile`: aged 45, 6 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 5 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: not linked
7. `check_suitability`: Salary paid in: allowed
8. `check_linked`: Salary paid in: not linked
9. `check_suitability`: Pension paid in: allowed
10. `check_linked`: Pension paid in: not linked
11. `check_suitability`: Current account: allowed
12. `check_review_due`: not due, next review 2018-04-21 (689 days)
13. `draft_questions`: 3 questions drafted
