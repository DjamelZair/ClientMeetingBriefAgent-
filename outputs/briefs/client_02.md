# Meeting brief: Client 02

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 32, with the bank for 19 months, income not recorded, individual segment, holds 1 product: Direct debit.

Recent changes:
- Closed 3 products in the last three months.

## 2. What might help

- **Payroll account**, scores above 50%. In the test month, 72% of the 242 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.
- **Salary paid in**, scores 29%. In the test month, 26% of the 368 clients scoring between 20% and 30% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.
- **Pension paid in**, scores 24%. In the test month, 23% of the 390 clients scoring between 20% and 30% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 23 February 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. What are your thoughts on where your salary is paid at the moment?

## How this brief was prepared

1. `get_profile`: aged 32, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: not linked
7. `check_suitability`: Salary paid in: allowed
8. `check_linked`: Salary paid in: not linked
9. `check_suitability`: Pension paid in: allowed
10. `check_linked`: Pension paid in: not linked
11. `check_review_due`: not due, next review 2019-02-23 (997 days)
12. `draft_questions`: 2 questions drafted
