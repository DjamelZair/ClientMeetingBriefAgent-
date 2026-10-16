# Meeting brief: Client 12

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 53, with the bank for 19 years, recorded income about 98,000, top tier segment, holds 10 products: Current account, Online account, Credit card, Direct debit, Tax payment account, Term deposit, Investment fund, Pension plan, Everyday plus account, Mortgage.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 5 products in the last three months.

## 2. What might help

- **Salary paid in**, scores above 50%. In the test month, 56% of the 338 clients scoring between 50% and 100% took it up. The score leans on: closed 5 products in the last three months; already pays bills by direct debit; an active client.
- **Pension paid in**, scores above 50%. In the test month, 55% of the 273 clients scoring between 50% and 100% took it up. The score leans on: closed 5 products in the last three months; already pays bills by direct debit; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 28 August 2016, 88 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on where your salary is paid at the moment?

## How this brief was prepared

1. `get_profile`: aged 53, 10 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 4 products scored, highest Salary paid in (above 50%)
5. `check_suitability`: Salary paid in: allowed
6. `check_linked`: Salary paid in: not linked
7. `check_suitability`: Pension paid in: allowed
8. `check_linked`: Pension paid in: not linked
9. `check_review_due`: due soon, next review 2016-08-28 (88 days)
10. `draft_questions`: 3 questions drafted
