# Meeting brief: Client 05

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Everyday inactive clients** (cluster 4): Everyday individual segment (98%), mostly inactive (6% active), rarely hold a current account (28%).

Aged 40, with the bank for 4 months, income not recorded, individual segment, holds 1 product: Plus account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.
- Was active three months ago and is not active now.
- Joined the bank in the last six months (4 months ago).

## 2. What might help

- **Online account**, scores above 50%. In the test month, 77% of the 151 clients scoring between 50% and 100% took it up. The score leans on: with the bank for 4 months; already holds a plus account; closed 1 product in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 25 September 2018.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You seem to use your account a little less lately. Is there anything about how you bank with us that is not working well for you?
2. How have your first months with us gone, and is there anything you expected that is not set up yet?
3. What are your thoughts on banking online or on your phone at the moment?

## How this brief was prepared

1. `get_profile`: aged 40, 1 product held
2. `get_segment`: cluster 4, Everyday inactive clients
3. `get_recent_changes`: 4 change flags
4. `get_propensities`: 7 products scored, highest Online account (above 50%)
5. `check_suitability`: Online account: allowed
6. `check_review_due`: not due, next review 2018-09-25 (846 days)
7. `draft_questions`: 3 questions drafted
