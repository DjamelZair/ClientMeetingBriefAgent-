# Meeting brief: Client 23

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 64, with the bank for 16 years, recorded income about 157,000, top tier segment, holds 5 products: Current account, Online account, Credit card, Term deposit, Investment account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Direct debit**, scores 11%. In the test month, 15% of the 2,723 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; an active client; holds 5 products.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 17 June 2016, 16 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 64, 5 products held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 5 products scored, highest Direct debit (11%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: due soon, next review 2016-06-17 (16 days)
7. `draft_questions`: 3 questions drafted
