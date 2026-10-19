# Meeting brief: Client 16

Meeting on 1 June 2016. Prepared to support the conversation. Scores are estimates, not instructions; the advisor decides what to discuss.

## 1. Who this client is

**Younger students** (cluster 0): Mostly students (99%), younger (average age 24), newer clients (about 3 years with the bank).

Aged 26, with the bank for 3 years, recorded income about 198,000, student segment, holds 3 products: Current account, Salary paid into the account, Pension paid into the account.

Recent changes:
- Took up 2 new products in the last three months.

## 2. What might help

Nothing new to suggest above 10%.

Likely already in progress:
- **Payroll account**, scores above 50%. The client already has pension paid in and salary paid in, so this is likely already in progress rather than something to suggest.

## 3. What not to offer

No high scoring product was held back by the suitability check.

## 4. Due anyway

No periodic review is due within 90 days; the next one is on 15 July 2017.

*Review dates come from a synthetic layer made for this prototype, not real records.*

## 5. Questions to open with

1. You started using something new with us recently. How is it working for you?
   *Recent change. Why: Took up 2 new products in the last three months.*
   - If "It works well": No change to the brief.
   - If "Having trouble with it": Help with the set up.
2. What matters most to you financially over the next year?
   *Open. Why: No due review, recent change or suggestion to start from, so an open question.*
   - If "Raises something specific": Record what the client raises; the brief has no data on it.
   - If "Nothing in particular": No change to the brief.

## How this brief was prepared

1. `get_profile`: aged 26, 3 products held
2. `get_segment`: cluster 0, Younger students
3. `get_recent_changes`: 1 change flag
4. `get_propensities`: 5 products scored, highest Payroll account (above 50%)
5. `check_suitability`: Payroll account: allowed
6. `check_linked`: Payroll account: in progress
7. `check_care`: care check: no signs in the data
8. `check_review_due`: not due, next review 2017-07-15 (409 days)
9. `draft_questions`: 2 questions drafted, each with a reason and answer branches
