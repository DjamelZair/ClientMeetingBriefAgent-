# Meeting brief: Client 38

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 20, with the bank for 3 months, income not recorded, individual segment, holds 1 product: Plus account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.
- Joined the bank in the last six months (3 months ago).

## 2. What might help

- **Online account**, scores above 50%. In the test month, 77% of the 151 clients scoring between 50% and 100% took it up. The score leans on: already holds a plus account; with the bank for 3 months; closed 1 product in the last six months.
- **Current account**, scores 16%. In the test month, 12% of the 775 clients scoring between 10% and 20% took it up. The score leans on: aged 20; closed 1 product in the last six months; with the bank for 3 months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 16 November 2016.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How have your first months with us gone, and is there anything you expected that is not set up yet?
2. You closed a product with us recently. Was there a reason we should know about?
3. What are your thoughts on banking online or on your phone at the moment?

## How this brief was prepared

1. `get_profile`: aged 20, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 7 products scored, highest Online account (above 50%)
5. `check_suitability`: Online account: allowed
6. `check_suitability`: Current account: allowed
7. `check_review_due`: not due, next review 2016-11-16 (168 days)
8. `draft_questions`: 3 questions drafted
