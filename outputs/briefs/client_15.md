# Meeting brief: Client 15

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 22, with the bank for 7 months, income not recorded, student segment, holds 3 products: Current account, Salary paid into the account, Pension paid into the account.

Recent changes:
- Took up 2 new products in the last three months.

## 2. What might help

**Next step:** Complete the periodic review first, then discuss new products.

## 3. What not to offer

New products wait until the review is done (1 would otherwise score above the threshold).

## 4. Due anyway

The periodic client review (KYC/CDD) was due on 6 April 2016, 56 days before the meeting, and is overdue.

**Next step:** Complete the periodic review first, then discuss new products.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review overdue by 56 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 2 new products in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Help with the set up.

## How this brief was prepared

1. `get_profile`: aged 22, 3 products held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 5 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: blocked by review_overdue
6. `check_care`: care check: no signs in the data
7. `check_review_due`: overdue, next review 2016-04-06 (-56 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
