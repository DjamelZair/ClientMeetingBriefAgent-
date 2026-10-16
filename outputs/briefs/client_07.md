# Meeting brief: Client 07

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 14, with the bank for 4 years, recorded income about 199,000, individual segment, holds 1 product: Pension paid in.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Payroll account** (scores 13%) is held back. The client is under 18, so only basic accounts are suggested.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 12 January 2018.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. You started using something new with us recently. How is it working for you so far?

## How this brief was prepared

1. `get_profile`: aged 14, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Payroll account (13%)
5. `check_suitability`: Payroll account: blocked by under_18_basic_only
6. `check_review_due`: not due, next review 2018-01-12 (590 days)
7. `draft_questions`: 2 questions drafted
