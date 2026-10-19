# Meeting brief: Client 19

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Premium multi product clients** (cluster 2): Premium segment (100%), many products (3.9 on average), often hold an online account (51%).

Aged 38, with the bank for 3 months, income not recorded, top tier segment, holds 1 product: Plus account.

Recent changes:
- Took up 1 new product in the last three months.
- Moved to a different province in the last six months.
- Joined 3 months ago.
- Client segment changed in the last six months.

## 2. What might help

- **Online account**, scores above 50%. In the test month, 83% of the 128 clients scoring between 50% and 100% took it up. The score leans on: already holds a plus account; with the bank for 3 months; an active client.
- **Current account**, scores 16%. In the test month, 12% of the 722 clients scoring between 10% and 20% took it up. The score leans on: with the bank for 3 months; an active client; moved to a different province in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 9 March 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You moved recently. Is everything at your new address set up the way you need it?
   *Recent change. Why: Moved to a different province in the last six months.*
   - If "Details still need updating": Update the address and any regular payments.
   - If "All set": No change to the brief.
2. How have your first months with us gone, and is anything not set up yet?
   *Recent change. Why: Joined 3 months ago.*
   - If "Something is missing": Find out what is missing and set it up before anything new.
   - If "All going well": No change to the brief.
3. How do you prefer to do your banking: in a branch, online or on your phone?
   *Top suggestion. Why: In the test month, 83% of the 128 clients scoring between 50% and 100% took up online account. This client has no online account here yet.*
   - If "Open to talking about it": Discuss Online account if the client wants to.
   - If "Already arranged elsewhere": Still on the brief: Current account. Online account is arranged at another bank. Record where it is arranged and do not raise Online account again in this meeting. Record it as declined: the brief will not raise Online account again for 182 days.
   - If "Not a priority now": Still on the brief: Current account. Online account is not a priority for the client now. Record it as declined: the brief will not raise Online account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 38, 1 product held
2. `get_segment`: cluster 2, Premium multi product clients
3. `get_recent_changes`: 4 change flags
4. `get_propensities`: 7 products scored, highest Online account (above 50%)
5. `check_suitability`: Online account: allowed
6. `check_suitability`: Current account: allowed
7. `check_care`: care check: no signs in the data
8. `check_review_due`: not due, next review 2017-03-09 (281 days)
9. `draft_questions`: 3 questions drafted, each with a reason and answer branches
