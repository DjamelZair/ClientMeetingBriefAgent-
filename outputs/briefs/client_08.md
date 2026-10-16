# Meeting brief: Client 08

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Everyday inactive clients** (cluster 4): Everyday individual segment (98%), mostly inactive (6% active), rarely hold a current account (28%).

Aged 71, with the bank for 13 years, recorded income about 178,000, individual segment, holds no products.

Recent changes:
- Closed 1 product in the last three months.
- Was active three months ago and is not active now.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Credit card** (scores 38%) is held back. Account activity has dropped in the last three months, so credit is not suggested.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 9 July 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You seem to use your account a little less lately. Is there anything about how you bank with us that is not working well for you?
2. You closed a product with us recently. Was there a reason we should know about?

## How this brief was prepared

1. `get_profile`: aged 71, no products held
2. `get_segment`: cluster 4, Everyday inactive clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 8 products scored, highest Credit card (38%)
5. `check_suitability`: Credit card: blocked by credit_activity_drop
6. `check_review_due`: not due, next review 2017-07-09 (403 days)
7. `draft_questions`: 2 questions drafted
