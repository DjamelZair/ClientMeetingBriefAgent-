# Meeting brief: Client 13

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Active everyday clients** (cluster 1): Mostly active (99% active), everyday individual segment (99%), often hold a current account (92%).

Aged 33, with the bank for 15 months, recorded income about 48,000, individual segment, holds 1 product: Current account.

Recent changes:
- Took up 1 new product in the last three months.
- Closed 2 products in the last three months.

## 2. What might help

- **Bills paid by direct debit**, scores above 50%. In the test month, 67% of the 113 clients scoring between 50% and 100% took it up. The score leans on: closed 3 products in the last six months; an active client; added 3 products in the last six months.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

The periodic client review (KYC/CDD) is due on 4 July 2016, 33 days after the meeting.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. Has anything changed in your work, income or home since we last updated your details?
   *Periodic review. Why: Periodic review due in 33 days (synthetic date).*
   - If "My income changed": Update income in the periodic review.
   - If "I moved home": Update the address in the periodic review.
   - If "Nothing has changed": Confirm the details and complete the review in this meeting.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 2 products in the last three months.*
   - If "Moved to another bank": Nothing new is raised. Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Nothing new is raised. Log the complaint and agree a follow up.
3. How do you keep track of your regular bills?
   *Top suggestion. Why: In the test month, 67% of the 113 clients scoring between 50% and 100% took up bills paid by direct debit. This client has no direct debits set up here.*
   - If "Open to talking about it": Discuss Bills paid by direct debit if the client wants to.
   - If "Already arranged elsewhere": Nothing new is raised. Bills paid by direct debit is arranged at another bank. Record where it is arranged and do not raise Bills paid by direct debit again in this meeting. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.
   - If "Not a priority now": Nothing new is raised. Bills paid by direct debit is not a priority for the client now. Record it as declined: the brief will not raise Bills paid by direct debit again for 182 days.

## How this brief was prepared

1. `get_profile`: aged 33, 1 product held
2. `get_segment`: cluster 1, Active everyday clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 7 products scored, highest Bills paid by direct debit (above 50%)
5. `check_suitability`: Bills paid by direct debit: allowed
6. `check_care`: care check: no signs in the data
7. `check_review_due`: due soon, next review 2016-07-04 (33 days)
8. `draft_questions`: 3 questions drafted, each with a reason and answer branches
