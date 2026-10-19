# Meeting brief: Client 07

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 9, with the bank for 5 years, recorded income about 146,000, individual segment, holds 1 product: Pension paid into the account.

Recent changes:
- Took up 1 new product in the last three months.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Payroll account** (scores 25%) is held back. The client is under 18, so only basic accounts are suggested.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 26 July 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 1 new product in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Help with the set up.
2. What matters most to you financially over the next year?
   *Open. Why: No due review, recent change or suggestion to start from, so an open question.*
   - If "Raises something specific": Record what the client raises; the brief has no data on it.
   - If "Nothing in particular": No change to the brief.

## How this brief was prepared

1. `get_profile`: aged 9, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Payroll account (25%)
5. `check_suitability`: Payroll account: blocked by under_18_basic_only
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2017-07-26 (420 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
