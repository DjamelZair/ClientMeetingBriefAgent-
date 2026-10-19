# Meeting brief: Client 40

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

**Care first:** Check for signs of financial difficulty first, and offer support before any product. Marked as possibly vulnerable (synthetic flag).

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 28, joined this month, income not recorded, holds no products.

Recent changes:
- Joined this month.
- Client segment changed in the last six months.

## 2. What might help

- **Current account**, scores 31%. In the test month, 33% of the 485 clients scoring between 30% and 50% took it up. The score leans on: joined this month; changed customer segment in the last six months; aged 28.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 27 October 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How are you managing with your money at the moment?
   *Care first. Why: Marked as possibly vulnerable (synthetic flag).*
   - If "Things are tight": Nothing new is raised. Explain where help is available and agree a follow up.
   - If "Would rather not say": Nothing new is raised. Leave the door open and mention where help is available.
   - If "Managing fine": Record that the client says they are managing.
2. How have your first months with us gone, and is anything not set up yet?
   *Recent change. Why: Joined this month.*
   - If "Something is missing": Find out what is missing and set it up before anything new.
   - If "All going well": No change to the brief.
3. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 33% of the 485 clients scoring between 30% and 50% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 28, no products held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 8 products scored, highest Current account (31%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: Marked as possibly vulnerable (synthetic flag).
7. `check_review_due`: not due, next review 2017-10-27 (513 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
