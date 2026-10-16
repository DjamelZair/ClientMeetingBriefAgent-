# Meeting brief: Client 15

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 69, with the bank for 21 years, recorded income about 160,000, individual segment, holds 5 products: Online account, Direct debit, Pension paid in, Tax payment account, Everyday account.

Recent changes:
- Closed 2 products in the last three months.

## 2. What might help

**Next step:** Complete the periodic review first, then discuss new products.

## 3. What not to offer

New products wait until the review is done (2 would otherwise score above the threshold).

## 4. Due anyway

The periodic client review (KYC/CDD) was due on 16 May 2016, 16 days before the meeting, and is overdue.

**Next step:** Complete the periodic review first, then discuss new products.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Before we look ahead, has anything changed in your work, income or home that we should update in your details?
2. You closed a product with us recently. Was there a reason we should know about?

## How this brief was prepared

1. `get_profile`: aged 69, 5 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 5 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: blocked by review_overdue
6. `check_suitability`: Salary paid in: blocked by review_overdue
7. `check_review_due`: overdue, next review 2016-05-16 (-16 days)
8. `draft_questions`: 2 questions drafted
