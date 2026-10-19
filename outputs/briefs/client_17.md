# Meeting brief: Client 17

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 21, with the bank for 13 months, recorded income about 215,000, student segment, holds 3 products: Current account, Salary paid into the account, Pension paid into the account.

Recent changes:
- Took up 2 new products in the last three months.

## 2. What might help

Nothing new to suggest above 10%.

Likely already in progress:
- **Payroll account**, scores above 50%. The client already has pension paid in and salary paid in, so this is likely already in progress rather than something to suggest.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 5 July 2016, 34 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review due in 34 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 2 new products in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Help with the set up.

## How this brief was prepared

1. `get_profile`: aged 21, 3 products held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 5 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: in progress
7. `check_care`: care check: no signs in the data
8. `check_review_due`: due soon, next review 2016-07-05 (34 days)
9. `draft_questions`: 2 questions drafted, each with a reason and answer branches
