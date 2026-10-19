# Meeting brief: Client 34

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Growing payroll account holders** (cluster 3): Often hold a payroll account (84%), recently adding products (about 1.9 on average in the last six months), many products (4.4 on average).

Aged 28, with the bank for 14 months, recorded income about 284,000, student segment, holds 3 products: Salary paid into the account, Pension paid into the account, Payroll account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Bills paid by direct debit**, scores 32%. In the test month, 40% of the 1,198 clients scoring between 30% and 50% took it up. The score leans on: closed 2 products in the last six months; an active client; already holds a payroll account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 14 November 2019.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
2. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 1 new product in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Nothing new is raised. Help with the set up.
3. How do you keep track of your regular bills?
   *Top suggestion. Why: In the test month, 40% of the 1,198 clients scoring between 30% and 50% took up bills paid by direct debit. This client has no direct debits set up here.*
   - If "Open to talking about it": Discuss Bills paid by direct debit if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Bills paid by direct debit is arranged at another bank. Record where it is arranged and do not raise Bills paid by direct debit again in this meeting. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.
   - If "Not a priority now": Nothing new is raised. Bills paid by direct debit is not a priority for the client now. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 28, 3 products held
2. `get_segment`: cluster 3, Growing payroll account holders
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 5 products scored, highest Bills paid by direct debit (32%)
5. `check_suitability`: Bills paid by direct debit: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2019-11-14 (1261 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
