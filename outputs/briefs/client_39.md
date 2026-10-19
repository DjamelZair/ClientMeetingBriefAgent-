# Meeting brief: Client 39

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 27, with the bank for 2 months, income not recorded, individual segment, holds 1 product: Current account.

Recent changes:
- Took up 1 new product in the last three months.
- Joined 2 months ago.

## 2. What might help

- **Bills paid by direct debit**, scores 10%. In the test month, 14% of the 2,684 clients scoring between 10% and 20% took it up. The score leans on: an active client; aged 27; added 1 product in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 18 August 2020.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How have your first months with us gone, and is anything not set up yet?
   *Recent change. Why: Joined 2 months ago.*
   - If "Something is missing": Find out what is missing and set it up before anything new.
   - If "All going well": No change to the brief.
2. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 1 new product in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Nothing new is raised. Help with the set up.
3. How do you keep track of your regular bills?
   *Top suggestion. Why: In the test month, 14% of the 2,684 clients scoring between 10% and 20% took up bills paid by direct debit. This client has no direct debits set up here.*
   - If "Open to talking about it": Discuss Bills paid by direct debit if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Bills paid by direct debit is arranged at another bank. Record where it is arranged and do not raise Bills paid by direct debit again in this meeting. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.
   - If "Not a priority now": Nothing new is raised. Bills paid by direct debit is not a priority for the client now. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 27, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Bills paid by direct debit (10%)
5. `check_suitability`: Bills paid by direct debit: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2020-08-18 (1539 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
