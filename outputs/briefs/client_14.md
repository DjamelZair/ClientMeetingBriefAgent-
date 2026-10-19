# Meeting brief: Client 14

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Everyday inactive clients** (cluster 4): Everyday individual segment (98%), mostly inactive (6% active), rarely hold a current account (28%).

Aged 34, joined this month, income not recorded, holds no products.

Recent changes:
- Joined this month.
- Client segment changed in the last six months.

## 2. What might help

- **Current account**, scores above 50%. In the test month, 45% of the 377 clients scoring between 50% and 100% took it up. The score leans on: joined this month; aged 34; changed customer segment in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 6 August 2016, 66 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review due in 66 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. How have your first months with us gone, and is anything not set up yet?
   *Recent change. Why: Joined this month.*
   - If "Something is missing": Find out what is missing and set it up before anything new.
   - If "All going well": No change to the brief.
3. How do you handle your everyday payments at the moment?
   *Top suggestion. Why: In the test month, 45% of the 377 clients scoring between 50% and 100% took up current account.*
   - If "Open to talking about it": Discuss Current account if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Current account is arranged at another bank. Record where it is arranged and do not raise Current account again in this meeting. Record it as declined: the brief will not raise Current account again for 182 days.
   - If "Not a priority now": Nothing new is raised. Current account is not a priority for the client now. Record it as declined: the brief will not raise Current account again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 34, no products held
2. `get_segment`: cluster 4, Everyday inactive clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 8 products scored, highest Current account (above 50%)
5. `check_suitability`: Current account: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: due soon, next review 2016-08-06 (66 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
