# Meeting brief: Client 21

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 72, with the bank for 17 years, recorded income about 106,000, top tier segment, holds 6 products: Current account, Direct debit, Pension paid in, Payroll account, Tax payment account, Term deposit.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 2 products in the last three months.
- Client segment changed in the last six months.

## 2. What might help

- **Credit card**, scores 32%. In the test month, 33% of the 289 clients scoring between 30% and 50% took it up. The score leans on: closed 4 products in the last six months; holds 6 products; aged 72.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 4 May 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on paying for larger purchases and spreading costs at the moment?

## How this brief was prepared

1. `get_profile`: aged 72, 6 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 4 products scored, highest Credit card (32%)
5. `check_suitability`: Credit card: allowed
6. `check_review_due`: not due, next review 2017-05-04 (337 days)
7. `draft_questions`: 3 questions drafted
