# Design critique: the brief page after the redesign

Scope: the desktop page at 1440x900 on scheme S1, in all three design system layers (ibm, mercury, linear), for clients 04, 10 and 11. A short phone section at 390px follows at the end.

Sources: the screenshots `after/desktop_{ibm,mercury,linear}_S1_client{04,10,11}.png` and `after/phone_*_S1_*.png`. I took fresh full page shots of client 10 in all three layers and measured every lane in a single browser run. Measurements are in CSS px at 1440x900.

| Layer | Page height (04 / 10 / 11) | Lane 1 part height | Lane 3 part | Lane 4 part | Wallet starts at y | Questions answer rows |
|---|---|---|---|---|---|---|
| ibm | 1313 / 1337 / 1245 | 734 to 827 | 140 to 233 | 210 to 246 | 826 to 880 | 3 buttons take 3 rows (124px) in many cases |
| mercury | 1434 / 1409 / 1314 | 808 to 904 | 131 to 229 | 215 to 234 | 821 to 909 | 3 buttons take 3 rows (125px) in many cases |
| linear | 1345 / 1409 / 1308 | 785 to 886 | 149 to 251 | 218 to 260 | 859 to 904 | 3 buttons take 2 rows (89px) |

Contrast: `contrast.txt` reports 468 pairs over 4 schemes and 3 layers with 0 failing, so this critique does not cover colour contrast again.

## Overall impression

The redesign does what the old page did not. In ten seconds you get the client, the review status, how much is held back, the headline and the five steps, all above the fold. The step rail with each part hanging under it is the strongest idea on the page. The biggest remaining problem is the lane heights. Lane 1 carries the full wallet and runs to about y 1260, while lanes 2, 3 and 4 end between y 580 and y 700. That leaves a block of empty canvas about 1100 by 550px under the middle of the brief, and the wallet, which is the most useful supporting detail, is the one thing that falls below the fold.

## First impression and the 10 second gist

**What the eye hits first.**
- *Client 10 and 11 (something held back):* the cherry bordered "Item held back" stat card at the top right, then the large headline. This is the right order. The held back fact is the most important fact for these clients, and the headline sub line repeats it ("Held back: credit card.").
- *Client 04 (nothing held back):* the dark avatar square, then the headline "Worth discussing: payroll account". The held back card turns grey and quiet ("0, Nothing held back"), which fits the rule: calm, but not hidden.

**The 10 second gist.** It works in all three layers. At 1440x900 you can see the identity, the four stat cards, the headline, all five step names with their status, and the start of every part. A reader who has never seen the page can say who the client is, what the agent suggests and what it holds back.

**What slows the gist.**
- Segment appears three times in the first 200px: the "Individual" badge next to the name, the "In the group" line, and the "Bank segment: Individual" stat card. The stat card adds no new fact unless the segment changed.
- The held back fact also appears three times above the fold: in the stat card, in the headline sub line, and in part 3. For client 10 that repetition is welcome, because it is the point of the meeting. Keep it there and cut the segment repeat instead.
- The ds and scheme switchers sit in the header at the same visual level as the client picker. They are review controls, not advisor controls. In mercury they are filled teal pills, which makes them the loudest thing in the header.

## Visual hierarchy

- **Reading flow.** Identity and stats, then headline, then the step rail left to right, then the parts. The rail gives a clear left to right order, and the numbered markers (1 to 5) are the best wayfinding on the page.
- **The headline.** ibm sets it at 32px weight 400 with a grey lead ("Worth discussing:") and an ink main phrase. It is the largest text but not the heaviest, so it competes with the bold card values in the summary strip. linear (28px, 600) gives the clearest headline of the three. mercury (28px, 480) sits in between.
- **Part titles.** ibm and linear use 20px weight 400. mercury uses 18px at weight 360 (`--w-title: 360`), which is lighter than its own body text weight. As a result the part titles in mercury look weaker than the bold sub headings under them ("Segment and group", "Worth discussing").
- **Step nodes.** Each node spends about 110 to 130px of height on 12px grey "Read" and "Returned" lines. That is a lot of first view height for detail that most advisors will not read. The step name and status do the linking work. The read list is supporting detail and could sit one level down.
- **What not to offer.** When something is held back, this part has the strongest treatment on the page: a cherry title, a 3px cherry top rule (`.part[data-hold]`) and a pink item. It is impossible to miss, as the brief asked. When nothing is held back it is a plain card with one grey line, which is right too (see the section below).

## Layout and use of space

1. **Empty lanes 3 and 4.** Parts 3 and 4 are 130 to 260px tall. Part 1 is 730 to 900px and part 5 is 530 to 620px. Every part starts at the same height, which is good, but their bottoms are ragged. Under lanes 2 to 4 that leaves an empty canvas roughly 1100 by 550px. On a one page brief this is the biggest waste on the page.
2. **Wallet below the fold.** The wallet starts at y 821 to 909, so at 900px you only see the "Products" heading and at most the first category. It is also squeezed into a 216px column, so a single row like "Bills paid by direct debit, Tax payment account, Salary paid into the account" wraps to four lines. The wallet is the one block that would gain the most from width, and it has the least.
3. **Narrow lanes stack the answer buttons.** Lane 5 is 296px wide, which leaves about 262px inside the card. In ibm and mercury, three short answers ("Moved to another bank", "No longer needed", "Something went wrong") often take three rows (124px for three buttons). This comes from `.v-ans .v-btn` padding (`calc(var(--ctl-px) / 2)`, so 8px a side), the 0.32px tracking on `--t-xs` in ibm, and the pill padding in mercury. linear (`--ctl-px: 14px`, no tracking) fits two a row.
4. **Part title wrap.** "What is due anyway" wraps to two lines in lane 4 (227px wide) in all three layers. The part 4 content then starts lower than parts 1 to 3, which breaks the shared baseline the grid works hard to keep.
5. **Column ratios.** The spine uses `1.1fr 1.25fr 1.05fr 1fr 1.3fr`. That gives lane 2 more width than lane 5. But lane 2 is often almost empty ("Nothing the bank sells, after the checks.") while lane 5 holds the longest text and the buttons.

## Typography

- **ibm (IBM Plex Sans 400/600).** It reads as serious and calm. The positive tracking on small text (`--ls-xs: 0.32px`, `--ls-s: 0.16px`) makes the 12px step lines and answer buttons look spaced out and wider than they need to be at this density. The 32px headline at weight 400 is elegant, but the summary values at 20px weight 400 are close enough in weight that the headline does not dominate.
- **mercury (Inter 360 to 500).** The lightest layer. Its 360 weight titles and 480 headline give it a soft, friendly tone. But the hierarchy is the flattest of the three: the part titles are lighter than their own sub headings, and the long group description at 15 to 16px with generous line height makes lane 1 the tallest of all.
- **linear (Roboto 400/500/600).** It has the strongest type contrast: a 600 headline, 400 titles, 500 for emphasis and no tracking. It is also the tightest: 12px lines fit more per row and answer buttons fit two a row. On the other hand Roboto is the most generic face of the three, and the result looks the most like a stock app.
- **All layers.** Sentence case labels and no tracked capitals: the old "ACCOUNTS" eyebrows are gone. Good.

## Consistency

| Element | Issue | Fix |
|---|---|---|
| Held back glyph | The cherry minus circle shows in the "Held back" lane heading even when nothing is held back (client 04). It is the only alarm coloured mark in an otherwise calm card. | In `C.held` (variants.js), pass `"quiet"` instead of `"heldback"` to `laneBlock` when the hold list is empty. Or add `.part:not([data-hold]) .v-lane-h .v-g { color: var(--ink-3); }` in index.html. |
| Part marker position | The step stem runs down the left edge of the lane, but the part's step number (`.v-part-h .v-from`) sits at the top right of the card. The link is drawn on the left and labelled on the right. | Put the part number on the left of the title, in line with the stem: move `fromTag(n)` before the title span in `C.partHead`, and drop `position: absolute; right: 0` from `.v-part-h .v-from` in tokens.css. |
| mercury surfaces | The part cards are tinted (`--card-bg: var(--surface-2)`) and the items inside are white (`--item-bg: var(--surface)`). This flips the depth used by the other two layers. It also puts the review box and pink held item on a grey card, which dulls the pink. | Swap them in the `[data-ds="mercury"]` block: `--card-bg: var(--surface)`, `--item-bg: var(--surface-2)`. |
| mercury switchers | The active ds, scheme and bar buttons are filled accent pills, which are louder than any content. | Use the outline or underline active state the other layers use (`--tab-on-bg: var(--surface)`, keep the ink and the line). |
| Summary values | The held back card shows "1" as its value and the product name as its status word. On the other three cards the value is the fact. | Use the product name (or "Nothing") as the value and the count as the status word, in `C.summary`. |
| Score band wording | The held item for client 11 says "Scores 50% to 100%" in the visible card. The step 2 node says "highest Credit card (above 50%)", even though credit card is held back for client 10. Both are bands, not raw probabilities, so they do not break hard rule 3. But a held back product named as "highest" in the step line reads like a top pick. | Add "held back" to the step 2 returned line when the top product is held: "highest Credit card (above 50%), held back at step 3". For a held item, move the band into a Why toggle the way `offer` items already do. |

## The step to part link

**What works**
- The numbered markers on a rail, a stem from each marker into its part, and a part number on each card make a clear, three part link.
- The status badge on the rail is colour coded to the part. In client 10 the step 3 marker and its "Held back 1" badge are cherry, and the part under it has the cherry rule. In client 11 step 4 says "Holds products" in cherry over the overdue review. That pairing is the best part of the redesign.
- Hover and focus light the whole lane (`.lane:is(:hover, :focus-within)`).

**What is weak**
- The stem is 1.5px of `--line-2` and fades into the card border. It only becomes visible in the lit state.
- The returned line was removed for steps 1 and 4 to avoid repeating text. That is the right call, but it makes those two nodes much shorter than 2, 3 and 5, so the rail looks uneven.
- Step 1 still feeds the identity block and two summary cards at the top of the page, but nothing on screen shows that. The `data-from` attribute is there, but there is no visible mark.

**Fix.** Make the stem `2px` and `var(--accent)` once the lane is done (`.lane[data-done] .stem`), not only when lit. Give each summary stat card the same small step number (`fromTag`) at its top right, so "from step 1, 3 or 4" can be seen without hovering.

## "What not to offer" with and without held back items

| Client | What it shows | Verdict |
|---|---|---|
| 10, credit card held back | Cherry title, cherry top rule, "Held back 1", a pink item with the rule in bold cherry ("No income on file: no credit.") and a plain reason. The stat card and headline sub line say the same. | Clear and explained. The rule leads, the reason follows, and the tone is factual. This is the best treated part on the page. |
| 11, payroll account waits for the review | The same treatment, with "Waits for the overdue review." The review part beside it is pink too, so lanes 3 and 4 read as one cause and one effect. | Good. One issue: "Scores 50% to 100%" is the only visible score in the part, and it draws the eye to a number that does not matter while the product is held. Put it behind Why. |
| 04, nothing held back | A plain card: "Held back. Nothing. 3 products checked against the rules." The stat card is grey: "0, Nothing held back". | Calm and honest, and it shows that a check took place. The cherry glyph next to "Held back" is the only false alarm (see Consistency). In linear and ibm the card is so short (140px) that it looks unfinished next to lane 2. Moving the wallet (issue 1 below) fixes that. |

## Does anything read as a sales instruction?

Nothing breaks hard rule 1, but four spots lean toward selling and are worth softening.

1. **"Nothing the bank sells, after the checks."** This empty state for "Worth discussing" (`C.discuss`, variants.js) is framed around selling. Use "Nothing to raise after the checks." instead.
2. **"Top suggestion"** as the reason label for a question (client 04, "How do you prefer to handle your income and regular payments?"). A question that opens with the bank's suggestion reads as a sales opener. Use "From step 2" or "Linked to what might help".
3. **The headline "Worth discussing: payroll account".** This is the largest text on the page, and it names a product. The grey lead helps, and "worth discussing" is the agreed wording. Keep it, but consider a sub line that says who decides ("If the client wants to. You decide.") when the headline names a product.
4. **"highest Credit card (above 50%)"** in the step 2 node for a client whose credit card is held back (see Consistency).

The draft follow up ("Draft for the advisor to check. Not sent.") and the answer branches ("Open to talking about it", "Not a priority now") are good. They hand the decision to the client and the advisor.

## What works well

- The summary strip, with a value, a label and a status word with its glyph on each card. The held back card is impossible to miss when it holds something and calm when it does not.
- Five parts that all start at the same height under their steps, with a matching number on each step and part.
- The headline sub line ("Held back: credit card.", "New products wait until the review is complete.") gives the gist in one sentence.
- Synthetic labels are present wherever needed: "Periodic review, synthetic date", "Synthetic date.", "9 Jun 2016, synthetic".
- The colour logic holds: cherry only for held back and overdue, teal for done and worth discussing, ochre for due.
- No tracked capitals, sentence case throughout, and 0 contrast failures.

## Issues ranked by severity

### High

1. **Lane heights leave a 1100 by 550px hole, and the wallet falls below the fold.**
   - *Fix:* take the wallet out of the part 1 card and give it a third spine row that spans lanes 1 to 4. Part 5 then spans rows 2 and 3.
   - In index.html: `.spine { grid-template-areas: "n1 n2 n3 n4 n5" "p1 p2 p3 p4 p5" "w w w w p5"; }`. Move the `#wallet` section into its own `<section class="part v-card wallet-part">` inside `.lane[data-n="1"]`, with `grid-area: w`, a "Products, from step 1" heading and `fromTag(1)`. That way it still lights with lane 1.
   - Lay the wallet categories out across the row: `.wallet-part .v-wallet { display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); }`.
   - Part 1 drops to about 430px. The wallet row is about 150px, and the page ends at about 1050px instead of 1250 to 1430.
   - The tablet and phone media queries keep `w` directly after `p1`, so the step order holds.
2. **Lane 5 is too narrow for its answer buttons.**
   - *Fix:* rebalance the spine to `minmax(0, 1.1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1.5fr)`. Lane 2 is often nearly empty, so it can give up width.
   - In tokens.css, set `letter-spacing: 0` on `.v-ans .v-btn`, so the ibm tracking does not widen the buttons.
   - Together these fit two or three answers a row in all layers.

### Medium

3. **Step nodes use about 120px of first view height for Read and Returned lines.** *Fix:* in index.html, set `readChars` lower, or render "Read" as a single "Read 8 fields +" toggle in `stepHTML`. Keep the returned line only for steps 2, 3 and 5, as now. This brings the parts up by 30 to 40px.
4. **The part number sits far from the stem** (see Consistency). *Fix:* move it to the left of the part title, in `C.partHead` and `.v-part-h .v-from`.
5. **"What is due anyway" wraps in lane 4.** *Fix:* the rebalanced columns help. Otherwise set `.v-part-h { text-wrap: balance; }` and allow `--t-l` to drop to 18px in lanes 3 and 4 only, or shorten the title to "Due anyway". This is a naming change, so it needs the user's approval.
6. **Sales leaning wording** in four places (see the section above). *Fix:* change the `C.discuss` empty state, the "Top suggestion" reason label in the question data, and the step 2 returned line for a held top product.
7. **mercury's flipped surfaces and loud switchers.** *Fix:* the `[data-ds="mercury"]` token swaps listed under Consistency.
8. **The segment stat card repeats the badge.** *Fix:* in `C.summary`, show the segment card only when the segment changed. Otherwise show "Products held" (count and categories) from the wallet, so the strip says something new.

### Low

9. **A cherry glyph on an empty held back lane.** *Fix:* `C.held` passes the quiet glyph when the list is empty.
10. **The stem is faint outside the lit state.** *Fix:* `.lane[data-done] .stem { width: 2px; background: var(--accent); }`.
11. **The held back stat card value is "1" instead of the product.** *Fix:* swap value and status word in `C.summary`.
12. **The ds and scheme switchers sit in the main header.** *Fix:* once a layer is chosen, move them into the footer (`#foot`) or behind a single "View" disclosure. The client picker should be the only control in the header centre.

## Recommendation: keep the ibm layer

**Why ibm.**
- **Light first by design.** IBM's system is built for light enterprise data screens, so it does not fight the S1 white scheme. linear is dark only by its own rules, and the brief already records that the layer is a compromise on white. That conflict cannot be fixed with tokens.
- **The real face.** It is the only layer that uses the font its file actually names (IBM Plex Sans). mercury runs on a substitute (Inter) and linear on a fallback (Roboto). So ibm is the only one of the three that is the design system it claims to be, rather than an approximation.
- **The right tone for a bank advisor.** Square cards, hairlines and no shadows suit an internal advisor tool. The held back card with a full cherry border reads as a fact, not a warning light.
- **The shortest page.** It is already the shortest (1245 to 1337px, against 1308 to 1434). After the wallet fix it is the most likely to fit in about one screen.

**Its weaknesses are all token level and fixable:**
- the tracking on small text;
- a headline that is light next to the stat values;
- answer buttons that stack.

**Borrow from linear**
- `--ls-xs: 0px` and `--ls-s: 0px` for 12 and 14px text in the ibm block. ibm's file asks for tracking, so record the change as a flagged deviation. Without it, the step lines and answer buttons will not fit at this density.
- linear's tighter control padding: `--ctl-px: 14px`.
- linear's headline weight contrast. ibm's file says not to bold headlines, so keep the 400 weight. Instead, darken the lead (`.v-head .lead { color: var(--ink-2); }` is already set) and lower the summary values to `--t-m` weight 400. That way the headline wins by size, not weight.

**Borrow from mercury**
- Its round step markers (`--r-marker: 9999px`) for the rail only. A circle reads as a step on a line more clearly than ibm's square tab, and it separates the rail markers from the square part numbers.
- Its slightly more generous reading line height for the long group description and the question text (`.v-q .qt` and `.grp .v-meta`), so the two prose blocks in the brief read easily.

## Phone (390px), secondary

From `after/phone_*_S1_client{04,10,11}.png`, 390 wide and 3280 to 3690px tall.

- **Order is right.** Identity first, then four stat cards in a two by two grid, then the headline, bar and replay, then each step with its part directly under it. There is no horizontal scroll. The step to part link holds better here than on the old page, because each node sits on top of its card.
- **The held back fact reaches the first screen.** The held back stat card is in the first 540px in all layers, so the gist survives on a phone.
- **The wallet buries part 3.** Part 1 carries the full wallet, so "What not to offer" starts about 1950 to 2050px down the page, more than two screens below the headline. The desktop wallet fix helps here too: with the `w` area placed after `p1` on phone, also collapse it by default (`V.state.open` key, a "Products held (5) +" toggle). Part 2 then starts about 500px higher.
- **The headline is three lines in ibm at 32px** ("Nothing worth / discussing after / the checks"). Set `--t-2xl` to `1.5rem` under the 760px media query.
- **The bar and replay row** takes about 120px between the headline and step 1. On a phone, put the bar under part 2, the part it changes (the `bar: "below"` option already exists in `C.discuss`).
- **Answer buttons fit two a row** at this width in ibm and linear, which is better than on desktop lane 5.
- **The stat cards wrap** awkwardly at 390: "15 years 4 / months", "No change in 6 / months". Let the tenure and review values use `--t-m` under 760px.
