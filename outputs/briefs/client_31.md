# Meeting brief: Client 31

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 26, with the bank for 2 years, recorded income about 42,000, individual segment, holds 1 product: Credit card.

Recent changes:
- Closed 1 product in the last three months.

## 2. What might help

- **Payroll account**, scores 22%. In the test month, 17% of the 92 clients scoring between 20% and 30% took it up. The score leans on: aged 26; closed 1 product in the last three months; already holds a credit card.
- **Current account**, scores 19%. In the test month, 12% of the 722 clients scoring between 10% and 20% took it up. The score leans on: closed 1 product in the last six months; aged 26; an active client.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 30 October 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. How do you prefer to handle your income and regular payments?
   *Top suggestion. Why: In the test month, 17% of the 92 clients scoring between 20% and 30% took up payroll account. This client's salary is not paid into this bank.*
   - If "Open to talking about it": Discuss Payroll account if the client wants to.
   - If "Already arranged elsewhere": Still on the brief: Current account. Payroll account is arranged at another bank. Record where it is arranged and do not raise Payroll account again in this meeting. Record it as declined: the brief will not raise Payroll account again for 182 days.
   - If "Not a priority now": Still on the brief: Current account. Payroll account is not a priority for the client now. Record it as declined: the brief will not raise Payroll account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 26, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 7 products scored, highest Payroll account (22%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: not linked
7. `check_suitability`: Current account: allowed
8. `check_care`: care check: no signs in the data
9. `check_review_due`: not due, next review 2017-10-30 (516 days)
10. `draft_questions`: 2 questions drafted, each with a reason and answer branches
