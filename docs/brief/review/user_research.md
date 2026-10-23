# User research for the brief page (desk research)

## 1. What this is, and what it is not

There are no real users for this prototype, so this is **desk research and heuristic review**, not findings from people. Everything below is a hypothesis to test.

- **Sources read:** notes/AGENT_FOR_ADVISORS.md (intended use), the redesign brief and its six hard rules, review/critique_before.md, docs/brief/variants.js (headline, footer and care logic), and the screenshots listed below.
- **Screenshots used:** review/after/desktop_*.png (first view only, 1440x900) and review/after/phone_*.png (full page, 390 wide). Anything below 900px on desktop was judged from the phone captures and the code, and is marked as such.
- **Not covered:** clients with a care flag (08, 09, 18, 20, 40) have no screenshot, so the care first state is judged from code only. Interaction (Replay, hover links, answer branches) was not run for this review.
- **No statistics, no quotes.** The personas are proto personas built from the project notes and general knowledge of the role. Words in quotation marks are page text, never things people said.

## 2. Personas (proto personas, to be validated)

### A. The client advisor (primary)

- **Context:** a bank advisor with back to back appointments, opening the brief on a desktop between meetings or just before the client arrives. Knows the products and the review process well; does not know or care how the model works.
- **Jobs to be done:**
  - When a client is about to walk in, I want the gist of who they are and what has changed, so I do not open the meeting cold.
  - When the system suggests something, I want to know why and how sure it is, so I can judge whether to raise it at all.
  - When something must not be offered, I want to know before I say anything wrong, so I keep my duty of care.
  - When an obligation is due anyway (the periodic review), I want to fold it into this meeting, so the client is not asked back.
  - When the conversation starts, I want an opening question and to know what each answer means for the rest.
- **Must answer on the page:** Who is this? Is there anything I must not do? Is anything due? What, if anything, is worth raising? How do I open?
- **Fears:** looking pushy, being blamed for an unsuitable offer, being handed a script, missing a care signal.

### B. The team lead or compliance reviewer (secondary)

- **Context:** reviews whether the tool is safe to put in front of advisors; reads slowly and sceptically, often after the fact.
- **Jobs to be done:**
  - When I audit a brief, I want to trace each line back to the step and data that produced it.
  - When a product is held back, I want to see the rule and the reason, and confirm it never reappears as a suggestion or in the follow up.
  - When I see a number, I want to know whether it is observed take up or raw model output, and whether synthetic data is clearly marked.
- **Must answer on the page:** Which step made this? Which rule fired? Is this number a model score? Is this field synthetic? Could anything here read as an instruction to sell?

### C. The hiring panel (data scientists in the CLUE team) and the recruiter

- **Context:** opens the live link from an application, probably on a laptop, with limited time and no walkthrough. The recruiter screens for clarity and judgement; the data scientists look for modelling honesty and engineering sense.
- **Jobs to be done:**
  - When I open the link, I want to understand within a minute what this is, what data it uses and what is real versus synthetic.
  - When I explore, I want to see that the candidate thought about risk, suitability and evaluation, not just a model score.
  - When I go deeper, I want to reach model quality, fairness and code in one click.
- **Must answer on the page:** What am I looking at? Is it a real bank's data? What does the agent actually do? Where is the evidence that the models are any good?

## 3. Top tasks by time budget

### Advisor

| Budget | Task | Question it answers |
|---|---|---|
| 10 seconds | A1 Identify the client and the meeting | Who is this, and is this today's meeting? |
| 10 seconds | A2 Read the headline | Is there anything worth raising, or not? |
| 10 seconds | A3 Spot any stop signal | Is anything held back, overdue, or a care concern? |
| 1 minute | A4 Understand what changed recently | Why might they be here? |
| 1 minute | A5 Check what not to offer and why | What must I avoid, in a sentence I can repeat? |
| 1 minute | A6 Check what is due anyway | Can I cover the review in this meeting? |
| 1 minute | A7 Pick an opening question | How do I start without selling? |
| 5 minutes | A8 Understand the evidence for a suggestion | How often did similar clients take it up? |
| 5 minutes | A9 Rehearse the answer branches | What changes if they say "Moved to another bank"? |
| 5 minutes | A10 Check the products the client holds | What do they already have with us? |
| 5 minutes | A11 Look at the follow up draft | What would I send afterwards, and is it safe? |

### Reviewer

| Task | Question |
|---|---|
| R1 Trace a brief part to its step | Which step made "What not to offer"? |
| R2 Verify a held back reason | Which rule, and is it the plain reason? |
| R3 Find every model number and its label | Is any raw probability shown outside the ranked component? |
| R4 Find every synthetic field | Is each one labelled? |

### Hiring panel

| Task | Question |
|---|---|
| H1 Say what the page is in one sentence | What am I looking at? |
| H2 Say what data it uses and what is synthetic | Real bank data or not? |
| H3 Describe what the agent does | How many steps, and is it really an agent? |
| H4 Reach model quality and code | Where is the evidence? |

## 4. Where the desktop layout answers each task

Verdicts: **Yes** (answered in the first view, clearly), **Partly**, **No**.

| Task | Where on the page | Screenshot | Verdict and reason |
|---|---|---|---|
| A1 | Identity block top left: "Client 10", segment badge, "Meeting 1 June 2016" | desktop_ibm_S1_client10.png | **Partly.** Name is prominent; the meeting date is small grey text in the last line of the block. |
| A2 | Headline under the strip, for example "Worth discussing: payroll account" | desktop_ibm_S1_client04.png | **Yes.** Largest type on the page, plain wording. |
| A3 | Summary strip, fourth card "Item held back 1, Credit card" with a cherry top rule; review card "Due in 8 days" or "Overdue by 35 days" | desktop_ibm_S1_client10.png, desktop_ibm_S1_client11.png | **Yes for held back and review.** Calm when nothing is held back ("Items held back 0, Nothing held back", client 04). **Care not verified**: no screenshot of a care client. |
| A4 | Tenure card status "Closed products, last 3 months"; timeline in part 1 | desktop_ibm_S1_client10.png | **Partly.** The recent change sits inside the tenure card, so it reads as a property of tenure, and it is the third line of a card with smaller type. |
| A5 | Part 3 "What not to offer", cherry heading, tinted card with rule and reason | desktop_ibm_S1_client10.png | **Yes.** The strongest part of the redesign. The reason is a sentence the advisor can say out loud. |
| A6 | Part 4 "What is due anyway", status box "Due in 8 days. Can be covered in this meeting." | desktop_ibm_S1_client10.png | **Yes.** Labelled synthetic. Heading wraps to two lines at this width. |
| A7 | Part 5 "Questions to ask", first quote | desktop_ibm_S1_client04.png | **Yes for the first question.** The second question is cut at 900px; the third is below the fold. |
| A8 | Part 2 card "71% of 228 similar clients took it up. Why +", bar chart | desktop_ibm_S1_client04.png | **Yes.** Observed take up, not a raw score. The caption under the chart is small. |
| A9 | Answer chips under each question ("Moved to another bank") | desktop_ibm_S1_client04.png | **Partly.** Visible as buttons, but nothing says that clicking one rewrites the brief until you try it. |
| A10 | Wallet under part 1, "Products" | phone_ibm_S1_client10.png (desktop wallet is below 900px) | **Partly.** Below the fold on desktop. The per row status word "Held" sits next to "Held back" rows. |
| A11 | "Follow up draft, Show the draft +", end of part 5 | phone_ibm_S1_client10.png | **No in the first view.** Below 900px on desktop; only reachable by scrolling the longest column. |
| R1 | Numbered markers 1 to 5 on each step and each part, vertical stem from step to part | any desktop_* | **Yes.** Clear; markers repeat on the part heading. |
| R2 | Part 3 card: "No income on file: no credit" plus reason | desktop_ibm_S1_client10.png | **Yes.** |
| R3 | Step 2 lane "Returned 4 products scored, highest Credit card (above 50%)"; part 3 card on client 11 "Scores 50% to 100%" | desktop_ibm_S1_client10.png, desktop_ibm_S1_client11.png | **Partly.** These are score bands, not raw probabilities, but they show a model score outside the ranked component, unlabelled. The user should decide whether this meets hard rule 3. |
| R4 | "Periodic review, synthetic date", "Synthetic date.", "KYC risk class (synthetic)" | desktop_ibm_S1_client10.png | **Yes** for review dates. Care flags are synthetic too; not verified on screen. |
| H1 | Header "Client brief"; client picker text "Client 10: No income on file: no credit" | desktop_ibm_S1_client10.png | **Partly.** The scenario names in the picker help, but no line says this is a prototype or what it is for. |
| H2 | Footer: "Independent prototype for a job application. Not affiliated with or endorsed by Rabobank. Review dates and vulnerability flags are synthetic." | phone_ibm_S1_client10.png | **No in the first view.** The disclaimer and data source live in the footer only; the dataset is never named on the page. |
| H3 | Step lanes, "One agent, 8 logged calls", Replay | desktop_ibm_S1_client10.png | **Yes.** The five steps and Replay make the agent visible. |
| H4 | Header links "How the models perform", "Code" | any desktop_* | **Yes.** |

Notes on the three design layers: the task map is the same in ibm, mercury and linear (desktop_mercury_S1_client04.png, desktop_linear_S1_client10.png). Mercury's taller identity block pushes the steps lower (step lane starts near y 350 instead of y 315), so part 5 loses more of the first view. Linear's bolder headline helps A2.

## 5. Where it fails, ranked by likely impact

1. **The step 2 lane names the held back product as the top score.** Client 10: "Returned 4 products scored, highest Credit card (above 50%)" sits directly above "What might help: Nothing the bank sells, after the checks." A quick reader may take credit card as the suggestion, which works against hard rule 1, and the band is a model score outside the ranked component (rule 3, borderline). Client 11's held back card repeats it as "Scores 50% to 100%".
   *Layout implication:* the step 2 Returned line should give the count only ("4 products scored"), and any score for a held back item should sit behind "Why +" inside part 3, labelled as model output.

2. **"Held" and "Held back" collide.** In the wallet a product the client owns is "Held" and a product the agent will not offer is "Held back", in the same column, often in adjacent rows (phone_ibm_S1_client10.png, desktop_ibm_S1_client11.png). Under time pressure these read as the same thing. Renaming is ruled out by the brief, so the fix must be layout.
   *Layout implication:* group owned products under their own subheading and drop the per row "Held" word, keep held back items only in part 3 (with a pointer from the wallet row), or raise this with the user as the one rename worth making.

3. **The questions and the follow up draft are below the fold.** Part 5 is what the advisor carries into the room, yet it is the longest column and is cut after the first question at 900px; the follow up draft is not in the first view at all. Parts 2 to 4 often end well above the fold (desktop_ibm_S1_client10.png), leaving white space under them.
   *Layout implication:* give part 5 the widest column and narrow part 4, or show the first question with its branches and collapse the rest into "2 more questions +", and pin the "Show the draft" link at the top of part 5.

4. **The summary strip spends prime space on low value facts.** "Bank segment: Individual, No change in 6 months" repeats the badge next to the name; the tenure card carries the recent change ("Closed products, last 3 months"), which is one of the most useful facts but reads as a footnote of tenure. The identity block and strip together take about 150px before the headline.
   *Layout implication:* merge the identity block and strip into one row; replace the segment card with a "What changed" card whose value is the recent change; keep review and held back cards as they are; reserve a slot for the care status.

5. **The first view does not tell a cold visitor what this is.** The hiring panel arrives without a walkthrough. The disclaimer, the synthetic notice and the author line are in the footer; the public dataset is never named on the page. Meanwhile the design and scheme switchers, which matter only to the author, take the centre of the header.
   *Layout implication:* one line under the header, small and quiet: prototype for a job application, public Santander data, synthetic review dates and care flags, the agent prepares and the advisor decides. Move the ds and scheme switchers into a compact "View" control once a layer is chosen.

Further issues, lower impact:

6. **The threshold control reads as a sales knob.** "Only include scores above 10% 20% 30% 50%" sits next to the headline. An advisor may lower it to find something to raise, which is the opposite of the intent. Consider moving it into the step 2 lane, labelled as a setting for the model's cut off, or behind a reviewer toggle.
7. **Answer branches do not say they change the brief.** Add a short hint such as "Choosing an answer updates the brief" under the first "If the client says", or a visible change marker after a click.
8. **Small grey type carries audit detail.** "Read Age, tenure and 6 more +" and the chart caption are the smallest text on the page; fine for the advisor, hard for the reviewer. Acceptable if it passes contrast; worth a size check.
9. **Care first state is unverified on screen.** Capture clients 08, 09, 18, 20 and 40 and check that care leads both the headline and the strip.
10. **"What is due anyway" wraps to two lines** in all three layers, which breaks the heading row alignment across parts.

## 6. Phone (secondary)

From phone_ibm_S1_client10.png, phone_mercury_S1_client10.png and phone_linear_S1_client10.png (390 wide, about 3,400px long):

- **Works:** the identity block and the four summary cards come first, so A1 to A3 are answered in the first screen; each part sits directly under its step, so the step to brief link survives; no horizontal scroll is visible.
- **Fails:** the full product wallet sits inside part 1, between step 1 and step 2, so "What not to offer" starts roughly half way down the page and part 5 near the end. On phone the wallet should collapse to one line ("Holds 6 products +") so parts 2 to 5 come up sooner.
- The headline wraps to three lines at this width; acceptable, but it pushes the threshold control and Replay into the first screen ahead of the brief.

## 7. Usability test plan (3 to 5 people)

**Goal:** check that an advisor can get the gist in 10 seconds, find what not to offer without help, and open the meeting with a question; and that a technical visitor understands what the page is within a minute.

**Participants:** 3 to 5. Ideally 2 or 3 people with front office banking or advisory experience (any bank, or a similar regulated advice role) and 1 or 2 data scientists who have not seen the project. Five sessions are enough to find the main problems, not to measure rates; report counts, not percentages.

**Setup:** desktop browser at 1440x900, ds and scheme fixed to the chosen layer, one session of about 30 minutes, think aloud, screen recorded with consent. Use client 04 (a suggestion), client 10 (something held back) and client 11 (review overdue); add one care client (08) if time allows. Do not explain the page beforehand.

**Tasks and success criteria**

| # | Task (as read to the participant) | Persona | Success criterion |
|---|---|---|---|
| T1 | "You see this for 10 seconds, then I hide it. What would you do in this meeting?" (client 10, screen hidden after 10 s) | Advisor | Mentions that nothing is to be offered and that credit card must not be raised. Fail if credit card is named as something to offer. |
| T2 | Same, for client 11 | Advisor | Mentions the overdue review comes first. |
| T3 | "Is there anything you should not offer this client, and what would you tell them if they asked?" (client 10) | Advisor | Finds part 3 in under 30 s without scrolling; restates the reason in their own words. |
| T4 | "How would you open the conversation?" (client 04) | Advisor | Picks one of the drafted questions, not a product pitch. |
| T5 | "The client says they moved to another bank. What changes?" | Advisor | Clicks the matching answer and notices that the brief changed. Record whether they find it unprompted. |
| T6 | "What does this client already have with the bank?" (client 11) | Advisor | Lists held products correctly and does not count the held back payroll account as owned. Direct test of finding 2. |
| T7 | "Where would you find the message to send afterwards? Would you send it as is?" | Advisor | Finds "Show the draft" within 60 s; notes it is a draft, not sent. |
| T8 | "Which step of the agent produced 'What not to offer'?" | Reviewer | Names step 3, Check suitability, using the markers or stems. |
| T9 | "Find every place where the model's score is shown." | Reviewer | Finds the ranked output (if shown) and the step 2 band; says whether each is labelled. |
| T10 | "In one sentence, what is this page, and is the data real?" (first open, 60 s) | Hiring panel | Says it is a prototype that prepares advisor meetings, on public or synthetic data, not a real bank's records. |
| T11 | "Where would you check whether the models are any good?" | Hiring panel | Finds "How the models perform" within 30 s. |

**Measures per task:** success or fail, time to first click or answer, where they looked first, wrong turns, and any moment the page read as "sell this". After all tasks: "What would you remove?" and "What did you expect to see that was not there?"

**Analysis:** one row per participant per task; mark a problem as confirmed when 2 or more people hit it. Map each confirmed problem back to the findings in section 5 and to a layout change. Rerun T1, T3 and T6 after the change with new people.

## 8. Assumptions to check first

- Advisors open the brief on a desktop, minutes before the meeting, not on a phone in the room.
- The advisor reads the headline before the strip; if eye tracking or think aloud shows the strip is read first, the strip carries more weight than the headline and its content matters more.
- "Held" is understood as "the client holds it". Finding 2 depends on this being ambiguous in practice.
- The hiring panel opens the live link without the motivation letter beside it.
