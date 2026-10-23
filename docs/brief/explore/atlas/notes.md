# Atlas (direction C): notes

The brief as an infographic report. It is plain HTML, CSS and JS with no build step. Open it at `docs/brief/explore/atlas/index.html` through any static server run on `docs/`.

## Files
- `index.html`: the layout, plus the page's own components: masthead, stepper with figures, step lines and hover link.
- `atlas.css`: the tokens in `:root` (colour roles, type scale, spacing, radii, shadows, motion), then the components.
- `variants.js`: a copy of `docs/brief/variants.js` with four changes:
  - the data path;
  - the footer links;
  - a few helpers exported;
  - the questions drawn as a decision tree.
  The original is untouched. The data still loads once, from `docs/data.json` through `docs/field.js`.
- `contrast.py`: checks 31 pairs and fails on any raw colour outside the token block. It exits 0.
- `checks/acheck.py`: covers all 40 clients at 1440x900 and 390, plus the logic. `checks/ashot_state.py` takes the answered and pinned shot. Both run through the flock lock.
- `shots/`: the screenshots.

## References used, and for what
- **GE "middle market by the numbers"**:
  - warm grey paper;
  - dotted dividers;
  - the two column report with a dotted rule between the columns;
  - big condensed numerals with small spaced labels under them;
  - headings in steel, sentence case.
- **Analy dashboard**: the horizontal stepper. Each step has its value above the node, the node on one rail and the name under it. The step in focus gets a pill under its name, like "Present cycle".
- **Statistical test decision tree**: the questions. The question is the root box, a stem and crossbar lead to the answer branches, and the chosen branch runs down into a "Then" box.
- **13 principles**:
  - Emphasis: the held back figure turns burgundy.
  - Hierarchy: figures, then the headline, then the parts.
  - Repetition: the same navy circle marks a step on the stepper and at the head of its part.
  - White space: no cards, only rules.

## Layout skeleton
1. A masthead: the client on the left, and the headline with the bar and replay on the right.
2. A stepper across the full width, with one figure per step, all from data.json:
   - years a client;
   - number worth discussing;
   - number held back;
   - days to the review, or days overdue;
   - number of questions.
   When the page scrolls, the figures scroll away and the rail with its five nodes rides at the top as the report's index. The part under it marks its node as in view, using an intersection observer.
3. The report:
   - part 1 in a wide left column;
   - parts 2, 3 and 4 in the right column;
   - part 5 full width, with its decision trees and the follow up draft.

**How a step links to its part:**
- Each part starts with the same numbered circle as its node. Under the title is a step line: "From step N, name", what the step read and what it returned, and its tool calls one click away.
- Hovering or focusing a part lights its node, and the other way round.
- Clicking a node pins the link: the node gets a rose pill and a ring, the part gets a rose rule, and the part scrolls into view.

**During a replay**, each figure and part stays faded until its step is done.

## 60-30-10
- **60, paper.** #F2EFEA is the page, with #F9F7F3 for the question roots, the outcome and the draft.
- **30, navy ink and its supports.** Navy #022E4C is used for the figures, headline, nodes and pressed controls. Ink #23314A is body text. Steel #517493 is the part titles. Stone #E2D9CB fills the "Has it" panel, chart bars and the idle rail. Mist #8FA1B1 is the dotted rules.
- **10, rose #DB8084.** It marks only the step in focus: the pill under the node name, the ring round the node, and the rule and wash on the linked part. It is always a fill with navy on it, never text on paper.
- **Burgundy #56061D sits outside the 60-30-10.** It means one thing only: held back, what not to offer, or overdue. On a client with nothing held back it does not appear, so part 3 stays calm.

## Fonts
From Google Fonts, with the families and weight axes fixed in the URL:
- **Barlow Condensed 500 and 600**: figures, the headline and the client name.
- **Barlow 400, 500, 600 and italic 400**: everything you read.

Small spaced small caps appear only under the figures and on the segment, as in the GE reference. Every other label is sentence case.

## Palette and contrast (from contrast.py, all pass)
| Pair | Ratio | Needed |
|---|---|---|
| ink on paper | 11.38 | 4.5 |
| ink-3 (quiet text) on paper | 5.13 | 4.5 |
| ink-3 on rose wash | 4.76 | 4.5 |
| steel-ink (links, "Has it") on stone | 4.86 | 4.5 |
| navy on rose (pill) | 4.96 | 4.5 |
| paper on navy | 13.10 | 4.5 |
| paper on burgundy | 13.63 | 4.5 |
| burgundy on burgundy wash | 11.32 | 4.5 |
| ink-3 on burgundy wash | 4.57 | 4.5 |
| steel part titles (24px) on paper | 4.29 | 3.0 (large) |
| mist-ink connectors and glyphs on paper | 3.77 | 3.0 (marks) |

Mist #8FA1B1 and rose are never used as text. Mist on paper is 2.32, so it is used only for the decorative dotted rules.

## Hard rules
1. **The agent only prepares; the advisor decides.** The headline wording comes from the shared layer, and the context line says the advisor decides. The decision trees describe what the brief would do, never what to sell.
2. **Synthetic stays labelled.** The review figure says "Synthetic date", and so do part 4 and the timeline.
3. **No raw probability.** None is printed. The ranked component is not used.
4. **Held back products stay visible.** They show in the figure, in part 3 and in the products list, each with its reason.
5. **Every number comes from data.json.** This includes the figures, which are computed from the view and the model.
6. **The step to part link is clear.** Each part repeats its node's circle and has a step line, and hover, focus and pin are two way.

## What falls below 900px (1440x900, client 10)
- **Above the fold:** the masthead, the headline, all five figures and steps, the starts of parts 1, 2 and 3, and part 3's held back item.
- **Below the fold:**
  - part 4, which starts at about 945px;
  - part 5, the questions, which starts at about 1160px;
  - the lower half of part 1, the products list.
  The stepper rides at the top while you scroll, so the five steps stay on screen.

## Phone (390)
- There is no horizontal scroll for any of the 40 clients.
- The stepper becomes the client summary: five figures in a two column grid, each with its node and step name. It stops sticking.
- The parts stack 1 to 5. Each starts with its step circle and step line, so each step sits directly above what it made.
- The answer branches keep the tree, with smaller labels.

## Not done
- No dark mode: it is a paper report, and the main page has none either.
- No ds or scheme switcher, because this direction is its own system.

## Round 2: the user picked Atlas

### Three palettes
The switcher is in the header. The order of precedence is `?pal=fabric|calm|graphite`, then this viewer's last choice, then Fabric. The last choice is kept in localStorage under `atlas-pal`, wrapped in try/catch.

Each swatch button carries `data-pal` and paints itself from its own palette block. All colours are role tokens: paper, stone, prime, ink, second, mist, hold, focus.

| Palette | 60 (surface) | 30 (ink and supports) | 10 (focus) | Held back |
|---|---|---|---|---|
| Fabric (default) | Paper #F2EFEA | Navy, steel, stone | Rose | Burgundy #56061D |
| Calm | Ivory #F4EFE8 | Sage, darkened to #34473A for text; moss and mist | Sand | Rust #8E3317 |
| Graphite | Light grey #EDEEF0 | #0A0C12, graphite #3F3A42, slate #76828E | Light slate | #DB5227 darkened to #A9400F for text, used only for held back, what not to offer and overdue |

- No palette pairs dark navy with orange.
- The five product states keep their glyph and word in every palette.
- `contrast.py` checks 34 pairs in each of the 3 palettes: 0 failures, exit 0.

### Search client
The dialog is a native modal `<dialog>`, so the page behind it is inert and Esc closes it. Focus moves to Client ID when it opens and returns to the button when it closes. Closing clears the fields.

- **Client ID (klant ID)** matches the 40 showcase clients, for example 10, C10 or "client 10", and jumps to that client.
- **Name and date of birth** never match. They show the placeholder line. The inputs have no name attribute and the form never submits.
- The check confirms that a typed name and birth date never reach the URL, localStorage or the console.

### Critique fixes
- **Step 2 figure.** It now shows how many products were scored, with the line "Worth discussing only after the checks". There is no count of suggestions.
- **Review figure.** A review that is not due shows its date and "Not due". The check confirms that no review figure is a long day count.
- **Part titles.** They are now prime and semibold, so they no longer look like links.
- **Figures.** They are slightly smaller (52px), so the headline is the clear first read.
- **Author line.** It sits under "Client brief". Below 1600px the palette names move to a tooltip and to text that only screen readers read.
