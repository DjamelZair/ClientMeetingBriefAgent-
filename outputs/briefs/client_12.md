# Meeting brief: Client 12

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 53, with the bank for 19 years, recorded income about 98,000, top tier segment, holds 10 products: Current account, Online account, Credit card, Bills paid by direct debit, Tax payment account, Term deposit, Investment fund, Pension plan, Everyday plus account, Mortgage.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 5 products in the last three months.

## 2. What might help

- **Salary paid into the account**, scores above 50%. In the test month, 57% of the 382 clients scoring between 50% and 100% took it up. The score leans on: closed 5 products in the last three months; already pays bills by direct debit; holds 10 products.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 28 August 2016, 88 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review due in 88 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 5 products in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
3. How do you prefer to handle your income and regular payments?
   *Top suggestion. Why: In the test month, 57% of the 382 clients scoring between 50% and 100% took up salary paid into the account. This client's salary is not paid into this bank.*
   - If "Open to talking about it": Discuss Salary paid into the account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Salary paid into the account is arranged at another bank. Record where it is arranged and do not raise Salary paid into the account again in this meeting. Record it as declined: the brief will not raise Salary paid into the account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Salary paid into the account is not a priority for the client now. Record it as declined: the brief will not raise Salary paid into the account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 53, 10 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 4 products scored, highest Salary paid into the account (above 50%)
5. `check_suitability`: Salary paid into the account: allowed
6. `check_linked`: Salary paid into the account: not linked
7. `check_suitability`: Pension paid into the account: allowed
8. `check_linked`: Pension paid into the account: not linked
9. `check_care`: care check: no signs in the data
10. `check_review_due`: due soon, next review 2016-08-28 (88 days)
11. `draft_questions`: 3 questions drafted, each with a reason and answer branches
