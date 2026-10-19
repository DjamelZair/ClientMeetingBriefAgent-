# Meeting brief: Client 08

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

**Care first:** Check for signs of financial difficulty first, and offer support before any product. Account activity dropped in the last three months.

## 1. Who this client is

**Everyday inactive clients** (cluster 4): Everyday individual segment (98%), mostly inactive (6% active), rarely hold a current account (28%).

Aged 37, with the bank for 14 years, recorded income about 191,000, individual segment, holds no products.

Recent changes:
- Closed 1 product in the last three months.
- Was active three months ago and is not active now.

## 2. What might help

Nothing scores above 10% after the suitability check.

## 3. What not to offer

- **Credit card** (scores 18%) is held back. Account activity has dropped in the last three months, so credit is not suggested.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 17 December 2016.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. How are you managing with your money at the moment?
   *Care first. Why: Account activity dropped in the last three months.*
   - If "Things are tight": Explain where help is available and agree a follow up.
   - If "Would rather not say": Leave the door open and mention where help is available.
   - If "Managing fine": Record that the client says they are managing.
2. Some of your products with us were closed recently. How are those needs covered now?
   *Recent change. Why: Closed 1 product in the last three months.*
   - If "Moved to another bank": Ask what made them move and record it for the advisor.
   - If "No longer needed": No change to the brief.
   - If "Something went wrong": Log the complaint and agree a follow up.

## How this brief was prepared

1. `get_profile`: aged 37, no products held
2. `get_segment`: cluster 4, Everyday inactive clients
3. `get_recent_changes`: 2 change flags
4. `get_propensities`: 8 products scored, highest Credit card (18%)
5. `check_suitability`: Credit card: blocked by credit_activity_drop
6. `check_care`: care check: Account activity dropped in the last three months.
7. `check_review_due`: not due, next review 2016-12-17 (199 days)
8. `draft_questions`: 2 questions drafted, each with a reason and answer branches
