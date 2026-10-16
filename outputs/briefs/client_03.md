# Meeting brief: Client 03

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 36, with the bank for 4 months, income not recorded, top tier segment, holds 1 product: Plus account.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 2 products in the last three months.
- Joined the bank in the last six months (4 months ago).
- Client segment changed in the last six months.

## 2. What might help

- **Online account**, scores above 50%. In the test month, 77% of the 151 clients scoring between 50% and 100% took it up. The score leans on: with the bank for 4 months; already holds a plus account; closed 2 products in the last six months.
- **Current account**, scores 11%. In the test month, 12% of the 775 clients scoring between 10% and 20% took it up. The score leans on: closed 2 products in the last six months; an active client; aged 36.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 4 May 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How have your first months with us gone, and is there anything you expected that is not set up yet?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on banking online or on your phone at the moment?

## How this brief was prepared

1. `get_profile`: aged 36, 1 product held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 4 change flags
4. `get_propensities`: 7 products scored, highest Online account (above 50%)
5. `check_suitability`: Online account: allowed
6. `check_suitability`: Current account: allowed
7. `check_review_due`: not due, next review 2017-05-04 (337 days)
8. `draft_questions`: 3 questions drafted
