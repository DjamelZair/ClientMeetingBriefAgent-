# Meeting brief: Client 10

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 45, with the bank for 15 years, income not recorded, individual segment, holds 6 products: Bills paid by direct debit, Salary paid into the account, Pension paid into the account, Payroll account, Tax payment account, Everyday account.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Credit card** (scores above 50%) is held back. No income is recorded, so affordability cannot be checked and credit is not suggested.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 9 June 2016, 8 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review due in 8 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Log the complaint and agree a follow up.

## How this brief was prepared

1. `get_profile`: aged 45, 6 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 4 products scored, highest Credit card (above 50%)
5. `check_suitability`: Credit card: blocked by credit_income_missing
6. `check_care`: care check: no signs in the data
7. `check_review_due`: due soon, next review 2016-06-09 (8 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
