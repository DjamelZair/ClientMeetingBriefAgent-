# Meeting brief: Client 03

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 36, with the bank for 4 months, income not recorded, top tier segment, holds 1 product: Plus account.

Recent changes:
- Took up 2 new products in the last three months.
- Closed 2 products in the last three months.
- Joined 4 months ago.
- Client segment changed in the last six months.

## 2. What might help

- **Online account**, scores above 50%. In the test month, 83% of the 128 clients scoring between 50% and 100% took it up. The score leans on: with the bank for 4 months; already holds a plus account; closed 2 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 4 May 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How have your first months with us gone, and is anything not set up yet?
   *Recent change. Why: Joined 4 months ago.*
   - If "Something is missing": Find out what is missing and set it up before anything new.
   - If "All going well": No change to the brief.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 2 products in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
3. How do you prefer to do your banking: in a branch, online or on your phone?
   *Top suggestion. Why: In the test month, 83% of the 128 clients scoring between 50% and 100% took up online account. This client has no online account here yet.*
   - If "Open to talking about it": Discuss Online account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Online account is arranged at another bank. Record where it is arranged and do not raise Online account again in this meeting. Record it as declined: the brief will not raise Online account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Online account is not a priority for the client now. Record it as declined: the brief will not raise Online account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 36, 1 product held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 4 change flags
4. `get_propensities`: 7 products scored, highest Online account (above 50%)
5. `check_suitability`: Online account: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: not due, next review 2017-05-04 (337 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
