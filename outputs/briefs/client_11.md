# Meeting brief: Client 11

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 32, with the bank for 21 months, recorded income about 176,000, student segment, holds 4 products: Current account, Direct debit, Salary paid in, Pension paid in.

Recent changes:
- Took up 2 new products in the last three months.

## 2. What might help

**Next step:** Complete the periodic review first, then discuss new products.

## 3. What not to offer

New products wait until the review is done (1 would otherwise score above the threshold).

## 4. Due anyway

The periodic client review (KYC/CDD) was due on 27 April 2016, 35 days before the meeting, and is overdue.

**Next step:** Complete the periodic review first, then discuss new products.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You started using something new with us recently. How is it working for you so far?

## How this brief was prepared

1. `get_profile`: aged 32, 4 products held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 4 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: blocked by review_overdue
6. `check_review_due`: overdue, next review 2016-04-27 (-35 days)
7. `draft_questions`: 2 questions drafted
