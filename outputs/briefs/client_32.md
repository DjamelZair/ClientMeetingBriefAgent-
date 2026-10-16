# Meeting brief: Client 32

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 22, with the bank for 19 months, income not recorded, student segment, holds 1 product: Current account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Direct debit**, scores 15%. In the test month, 15% of the 2,723 clients scoring between 10% and 20% took it up. The score leans on: closed 1 product in the last six months; an active client; already holds a current account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 25 January 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?
3. What are your thoughts on keeping on top of regular bills at the moment?

## How this brief was prepared

1. `get_profile`: aged 22, 1 product held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Direct debit (15%)
5. `check_suitability`: Direct debit: allowed
6. `check_review_due`: not due, next review 2019-01-25 (968 days)
7. `draft_questions`: 3 questions drafted
