# Meeting brief: Client 36

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 34, with the bank for 9 months, recorded income about 56,000, individual segment, holds 3 products: Salary paid in, Pension paid in, Payroll account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 2 products in the last three months.
- Client segment changed in the last six months.

## 2. What might help

- **Direct debit**, scores 40%. In the test month, 38% of the 1,263 clients scoring between 30% and 50% took it up. The score leans on: closed 4 products in the last six months; an active client; added 4 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 5 June 2016, 4 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 34, 3 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 5 products scored, highest Direct debit (40%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: due soon, next review 2016-06-05 (4 days)
7. `draft_questions`: 3 questions drafted
