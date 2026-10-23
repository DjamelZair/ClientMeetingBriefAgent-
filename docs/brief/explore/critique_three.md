# Ledger, Mono and Atlas compared

## 1. Scope and method

This is a heuristic critique with desk research. No real advisors, reviewers or panel members took part, so every verdict below is a hypothesis. The personas are the same proto personas as in review/user_research.md: the client advisor (primary), the team lead or compliance reviewer, and the CLUE hiring panel with the recruiter.

**Sources read:**
- the three notes.md files;
- the three shots/ folders: desktop clients 04, 10 and 11, the full page for client 10, the phone view for client 10, the Mono tool log and the Atlas answered state;
- compare_three_client10.png and ledger_palettes_client10.png;
- the Tasklify reference.

I took no new screenshots, because the existing set covers every question asked. All desktop judgements are at 1440x900. No page code was edited.

Words in quotation marks are text on the page, never things people said.

## 2. Summary verdict

| Criterion | Ledger | Mono | Atlas |
|---|---|---|---|
| 10 second gist (advisor) | Good | Good, but the client is not named in the main panel | Strongest numbers, but they compete with the headline |
| Step to brief link (rule 6) | Clear, one row per step | Clearest: each step heads its own column | Clear: a stepper node plus a "From step N" line |
| Reads as a sales instruction | No | Mild: the product name is set in bold in the headline | Yes, on one point: "2 worth discussing or asking" as a big figure |
| Hierarchy | Calm, with one clear focal point | Tiles compete with the headline | Two focal points: the figures and the headline |
| Above the fold at 1440x900 | Only part 1 | The top of all five parts | Parts 1 to 3 |
| Agentic AI evidence (panel) | Weak: reads as an editorial report | Strong: a board of steps, a tool log and an agent banner | Medium: reads as a process report |

**Recommendation: Mono.** It is the only direction where all five agent steps and the first output of each step are visible in the first view. It is also the one a hiring panel will read as an agent at work rather than as a styled report. It matches the reference the user named as best for agentic AI.

If Ledger is kept as a fallback, use the **Calm** palette (section 4).

## 3. Each direction

### A. Ledger

**Overall impression:** quiet, expensive and easy to read. It feels like a private banking letter, which suits the advisor and undersells the agent.

**10 second gist.** It works well:
- The masthead names the client ("Client 10", age, income recorded, meeting date).
- Four KPI cards follow, with the held back card ruled in the accent colour.
- The serif headline "Nothing worth discussing after the checks" reads at once.
- The rail index repeats the status of each part ("1 held back", "Due in 8 days", "2 questions and a draft"). That is the best summary of the three directions.

**Step to brief link.** The rule is met:
- Each row puts the step on the left, sticky, with its part as a card on the right. A short connector joins them.
- The number in the rail, on the step and on the part heading is the same.

**Sales reading.** I found no instruction to sell:
- On client 04, "Worth discussing:" is set in italic and the product in roman, which is restrained.
- "Worth discussing" and "Worth asking about" sit as quiet teal words in the product list.

**Hierarchy.** It has a clear order: name, KPI cards, headline, rows. Part titles in serif with a numbered badge are elegant. The cost is length. Each row is a full width block with a lot of air, and part 2 for client 10 is one sentence in a 140px tall card.

**Below the fold.** Only part 1 is visible at 900px. Parts 2 to 5 start at about 1000 to 2800px.
- What not to offer: one scroll down.
- Questions and follow up draft: the very end.
This repeats failure 3 from the earlier research, and is worse than the current page.

**Hiring panel.** The steps read as section labels ("Get segment, Done"), not as tool calls:
- Replay is in a small rail card.
- Nothing shows tool names or the order of calls.
A panel will see good taste and a careful brief. It will not see much agent.

**What works:** the rail index with a live status for each part, the plain step summaries ("Read ... Returned ..."), and the serif headline.

### B. Mono

**Overall impression:** the closest match to the Tasklify reference, and the most product like of the three. On client 10, the one signal colour lands on the held back tile and the step 3 column, exactly where the eye should go.

**10 second gist.** It is good, with one gap:
- The headline is the first text in the panel.
- The agent banner says "One agent ran five tool steps", with a five segment meter in which step 3 is in the signal colour. It also says "It prepares the brief; the advisor decides."
- Four tiles answer what changed, tenure, review and held back.
- The gap: the client's name and meeting date appear only in the breadcrumb and in the client card at the foot of the sidebar. For task A1 ("Who is this, and is it today's meeting?") the advisor has to look bottom left.

**Step to brief link.** This is the strongest of the three:
- Each column is headed by its step number, a status pill with a count, and the step name.
- Under the header come what the step read and returned, then a divider with the part title ("What not to offer, Step 3").
- Under that are the part's cards.
- Hovering a column lights its sidebar item, and the reverse works too.
- The Tool log view keeps the same five columns, with the real function names (get_profile, check_suitability, check_care) and one line on each method.
One redundancy: column 1 shows "Step 1" in the tile, in the header and again on the divider. Three links to the same place dilute it.

**Sales reading.** It is mostly safe:
- The tiles count nothing that could be sold.
- The take up meter is labelled "Similar clients who took it up" and comes from data.json, so it is not a raw score.
- One mild issue on client 04: in "Worth discussing: payroll account", the product name is black and bold after a grey prefix. The product therefore reads as the message. The shared wording is fine. The weight split is what pushes it.

**Hierarchy.** The headline is 28px and the tile values are 20px bold. On client 10 the held back tile, in signal colour, wins the first glance. That is acceptable for a stop signal, but the four tiles together outweigh the headline. Card text in columns 2 to 4 is about 190px wide, which leads to long thin wraps (the held back reason runs to six lines).

**Below the fold.** The top of every part is visible: the first card of each column and the first question with its reason. Below the fold:
- the rest of the products in column 1;
- every question after the first;
- every answer branch, which means the "if the client says" pills are never in the first view.
Column 5 carries the most content, yet it gets the same width as column 4, which holds one card.

**Hiring panel.** This is the clearest evidence of an agentic prototype:
- a board with one column per tool step;
- a status for each step;
- a meter of the run;
- Replay;
- a tool log naming the functions, the model (LightGBM per product, SHAP for reasons), the guardrail rules, and the line "Claude may only rephrase the wording, when a key is set".
The author line is only in the footer, though, so a cold visitor does not know whose work this is until the end.

**Phone.** It keeps working:
- the client card comes first;
- each column stacks with its cards directly under its step;
- the products fold behind "Show: Has it 6, Held back 1 +";
- there is no sideways scroll.
The tiles take two screens before the board starts. Acceptable.

**What works:** the board as the agent's run, the one signal colour, the tool log, and the folded products on phone.

### C. Atlas

**Overall impression:** the most original of the three, and the most "data scientist" in tone. The figures and the decision tree are excellent ideas, but the figures carry the wrong weight in places.

**10 second gist.** It is strong, but split:
- The five large figures sit over a stepper and give a gist at a glance.
- The condensed headline on the right is just as large, so the eye has two places to start.
- On client 04 the review figure reads "1439 DAYS TO THE REVIEW". The largest number on the page is a synthetic date four years away, which is noise.

**Step to brief link.** This is very clear:
- Each part repeats its node's navy circle and opens with "From step 2, Get propensities. Read ... Returned ...".
- Hover, focus and pin work both ways.
- The rail sticks to the top on scroll, so the five steps stay on screen while the advisor reads part 5.
This is the best treatment for the reviewer, task R1.

**Sales reading.** There is one real problem. "2 WORTH DISCUSSING OR ASKING" (client 04) as a display figure turns suggestions into a count, and a count reads like a target. The same slot shows "0 worth discussing" on client 10, which reads as a shortfall. Showing held back as a figure is right, because it is a stop signal. Counting suggestions is not.

**Hierarchy.** Part titles are in light steel blue at 24px. They look like links and sit below the body headings ("Growing payroll account holders" is bolder than "Who the client is"). Without cards, rules carry the whole structure, and the two column body is calm.

**Below the fold.** Parts 1 to 3 start in the first view, including the held back reason. Below the fold:
- part 4 (about 945px);
- part 5, the questions (about 1160px);
- the products.

**Answer branches.** This is the best of the three:
- A root box holds the question and a stem leads to the pills.
- The chosen pill turns navy and drops into a "Then" box that says what the brief now does, for example "Current account moved to Not raised".
- The intro line "Pick an answer to see what the brief does then" fixes failure 7 from the earlier research outright.

**Hiring panel.** The stepper shows a pipeline, and the header names the author and the role ("Djamel Zair, application for Junior Data Scientist, CLUE"), which is the only first view author line in the three. It reads as a strong report on an agent's output, not as the agent itself, and there is no tool log.

**What works:** the decision tree, the author line, the "From step N" lines, and the sticky stepper.

## 4. Ledger palettes

Judged from ledger_palettes_client10.png, on client 10, where the held back state is the test.

| Palette | Held back signal against the other steps | Tone | Verdict |
|---|---|---|---|
| Tokyo | Orange step 3 against teal; clear | Warm, but the orange rule and title are loud for a calm brief | Good |
| **Calm** | Orange step 3 against muted sage; the clearest single warm note on the page | Quiet and closest to the Calm Kit; the 60 30 10 reads best | **Recommended** |
| Berry | Rose step 3 against navy; visible but soft | Cool; pink held back reads as gentle, not as a stop | Second |
| Bordeaux | Burgundy step 3 against navy steps; hard to tell apart at rail size | Serious, but the stop signal is lost in the rail | Not recommended |
| Sunset | Orange against teal, with orange bars in the group chart too | The accent is spent on decoration, so it no longer means held back | Not recommended |

None of the five uses a dark blue plus orange pairing as the identity. Berry and Bordeaux lead with navy but pair it with rose or burgundy.

## 5. Recommendation and top three borrowings

**Take Mono as the base.** Borrow these three things from the other two directions, in order of impact.

1. **From Atlas: the decision tree for answer branches, with its "Then" box and intro line.**
   - Why: in Mono the branches are a column of small pills in a 190px column, below the fold. Nothing says that a click rewrites the brief (failure 7 in the earlier research).
   - How: give the questions column more width, or open a question into a full width row under the board. Draw the root, stem and pills, and show the "Then" outcome in place. Keep "Pick an answer to see what the brief does then" as the first line of part 5.
   - Watch: do not add Atlas's "worth discussing" count figure along with it.

2. **From Atlas: the masthead with the client and the author line.**
   - Why: Mono's main panel never names the client, and a cold visitor learns whose work it is only in the footer.
   - How:
     - put "Client 10", the segment badge, age, income recorded and meeting date on one line above the headline, where the context line is now;
     - move the client card out of the sidebar foot;
     - add Atlas's quiet "Djamel Zair, application for Junior Data Scientist, CLUE" next to "Client brief" in the sidebar header.
   - This answers A1 and H1 in the first view.

3. **From Ledger: a live status under each sidebar step.**
   - Why: Mono's sidebar subtitles repeat the part names ("Who the client is"), which the board headers already show. Ledger's rail gives each part's result instead ("Has it: 6 products", "Nothing to discuss", "1 held back", "Due in 8 days", "2 questions and a draft").
   - How: replace the subtitle with that status, keeping the signal colour for held back only. The sidebar then becomes the summary that survives scrolling, and the advisor gets the gist from the left edge alone.

**Smaller fixes inside Mono:**
- set the whole headline in one weight, so the product name does not read as the message;
- drop the third "Step n" link on each column divider, because the header already names the step;
- make column 5 wider than column 4;
- check the board at 1280x800, where the notes say a sideways scroll starts below 1180px but nothing has been screenshot checked.
