# Critique of the current brief page (before)

Screenshots: before/desktop_client04.png, client10, client11, and the phone versions.

## What exists
- **Profile column (left):** identity card, fact chips, timeline, and the product wallet by category. It is about 280px wide and spans the full height.
- **Stage header:** the headline ("Worth discussing: ..." or "Nothing worth discussing after the checks") with the threshold bar on the right.
- **Agent pipeline:** five step nodes in one card, each with status, Read and Returned, plus Replay.
- **Five columns (data-col 1 to 5) under the pipeline.** V.boot renders into them:

  | Column | Holds | Mounts |
  |---|---|---|
  | 1 | segment and group | #group |
  | 2 | worth discussing and worth asking about | #discuss, #ask |
  | 3 | care, held back and in progress | #care, #held, #aside |
  | 4 | review | #review |
  | 5 | questions and the follow up draft | #questions, #followup |

- **How rendering works.** `V.boot({chrome, mounts})` maps a selector to a component function, which is already a widget registry. Data loads once through field.js.

## What is hard to scan
1. **There is no summary.** The facts an advisor needs first (segment, tenure, review status, how much is held back) are spread over the chips in the left column and the step nodes. Nothing gives the gist in one line of numbers.
2. **The left column competes with the stage.** The wallet is tall and dense, with many tinted rows, and it carries as much visual weight as the brief.
3. **"What not to offer" is easy to miss when it matters.** It sits as the third of five equal narrow columns. For client 10, the most important fact (credit card held back) is a small pink card in column 3.

## Where the hierarchy is weak
4. **Five equal column widths.** Text-heavy parts (group description, questions) get the same width as nearly empty ones (review). Column 1 holds a long paragraph in a 150px column, while columns 2 and 4 are often short.
5. **Repeated text.** The step nodes repeat what the cards below say ("Returned: Growing payroll account holders" sits right above the "Growing payroll account holders" card).

## Where the step to brief link gets lost
6. **The connection is too thin.** It is only a 1px stem and a small circled number. On phone width the pipeline stacks first and the brief cards follow, so the link between step and output disappears.
7. **Some steps feed more than one part, without saying so.** Step 3 produces care, held back and in progress, while step 1 also feeds the profile card on the left. That second link is not shown.

## What feels generic
8. **The same tinted card everywhere.** Steps, columns and wallet rows are all bordered cards on a light page with a soft tint, which is the stock SaaS look.
9. **Weak type contrast.** Too many sizes between 12 and 16px, and every label weighs about the same.
10. **Tracked capital eyebrows** in the wallet ("ACCOUNTS", "PAYMENTS AND INCOME").
