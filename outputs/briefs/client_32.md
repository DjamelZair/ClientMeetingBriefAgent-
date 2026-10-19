# Meeting brief: Client 32

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 40, with the bank for 19 months, recorded income about 54,000, individual segment, holds 1 product: Current account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 1 product in the last three months.

## 2. What might help

- **Bills paid by direct debit**, scores 35%. In the test month, 40% of the 1,198 clients scoring between 30% and 50% took it up. The score leans on: closed 2 products in the last six months; an active client; already holds a current account.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 3 May 2018.

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

1. `get_profile`: aged 40, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Bills paid by direct debit (35%)
5. `check_suitability`: Bills paid by direct debit: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2018-05-03 (701 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
