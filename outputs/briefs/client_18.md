# Meeting brief: Client 18

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

**Care first:** Check for signs of financial difficulty first, and offer support before any product. Account activity dropped in the last three months.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 23, with the bank for 4 years, recorded income about 81,000, student segment, holds no products.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 2 products in the last three months.
- Was active three months ago and is not active now.

## 2. What might help

- **Current account**, scores above 50%. In the test month, 45% of the 377 clients scoring between 50% and 100% took it up. The score leans on: added 2 products in the last six months; aged 23; closed 2 products in the last three months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 10 November 2018.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How are you managing with your money at the moment?
   *Care first. Why: Account activity dropped in the last three months.*
   - If "Things are tight": Nothing new is raised. Explain where help is available and agree a follow up.
   - If "Would rather not say": Nothing new is raised. Leave the door open and mention where help is available.
   - If "Managing fine": Record that the client says they are managing.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 2 products in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
3. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 45% of the 377 clients scoring between 50% and 100% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 23, no products held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 3 change flags
4. `get_propensities`: 8 products scored, highest Current account (above 50%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: Account activity dropped in the last three months.
7. `check_review_due`: not due, next review 2018-11-10 (892 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
