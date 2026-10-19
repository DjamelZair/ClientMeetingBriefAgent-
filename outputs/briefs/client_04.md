# Meeting brief: Client 04

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 51, with the bank for 2 years, income not recorded, individual segment, holds 2 products: Bills paid by direct debit, Tax payment account.

Recent changes:
- Closed 3 products in the last three months.

## 2. What might help

- **Payroll account**, scores above 50%. In the test month, 71% of the 228 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.
- **Pension paid into the account**, scores 31%. In the test month, 43% of the 779 clients scoring between 30% and 50% took it up. The score leans on: closed 3 products in the last three months; already pays bills by direct debit; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 10 May 2020.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 3 products in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. How do you prefer to handle your income and regular payments?
   *Top suggestion. Why: In the test month, 71% of the 228 clients scoring between 50% and 100% took up payroll account. This client's salary is not paid into this bank.*
   - If "Open to talking about it": Discuss Payroll account if the client wants to.
   - If "Already arranged elsewhere": Still on the brief: Pension paid into the account. Payroll account is arranged at another bank. Record where it is arranged and do not raise Payroll account again in this meeting. Record it as declined: the brief will not raise Payroll account again for 182 days.
   - If "Not a priority now": Still on the brief: Pension paid into the account. Payroll account is not a priority for the client now. Record it as declined: the brief will not raise Payroll account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 51, 2 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: not linked
7. `check_suitability`: Pension paid into the account: allowed
8. `check_linked`: Pension paid into the account: not linked
9. `check_suitability`: Salary paid into the account: allowed
10. `check_linked`: Salary paid into the account: not linked
11. `check_care`: care check: no signs in the data
12. `check_review_due`: not due, next review 2020-05-10 (1439 days)
13. `draft_questions`: 2 questions drafted, each with a reason and answer branches
