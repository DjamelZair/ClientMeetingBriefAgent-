# Meeting brief: Client 09

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 50, with the bank for 17 years, recorded income about 426,000, top tier segment, holds 6 products: Online account, Direct debit, Salary paid in, Pension paid in, Payroll account, Everyday account.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Credit card** (scores above 50%) is held back. The client is marked as possibly vulnerable, so credit is not suggested.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 28 April 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You closed a product with us recently. Was there a reason we should know about?
2. What matters most to you financially over the next year?

## How this brief was prepared

1. `get_profile`: aged 50, 6 products held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 3 products scored, highest Credit card (above 50%)
5. `check_suitability`: Credit card: blocked by credit_vulnerable
6. `check_review_due`: not due, next review 2019-04-28 (1061 days)
7. `draft_questions`: 2 questions drafted
