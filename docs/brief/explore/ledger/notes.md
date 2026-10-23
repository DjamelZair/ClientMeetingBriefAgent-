# Ledger (direction A), notes

Open `index.html` in this folder (served from `docs/`). It reads `../../../data.json` through `../../../field.js` and a private copy of the shared layer (`brief.js`, a copy of `docs/brief/variants.js` with only the footer link path changed).

## References and what I took from each
- Anatomy of a Perfect Dashboard: the left navigation rail, KPI cards with a small bar, the serif display headline over a clean sans, and the "decision making flow": the page reads top to bottom from who the client is (insight) to the questions and the follow up draft (action).
- Science of Color: the 60 30 10 split and the contrast targets (4.5:1 text, 3:1 marks).
- Calm Kit: sage and ivory support colours, pill shaped controls, soft cards with tinted shadows, the segmented control for the score bar.
- Tokyo palette: sage #A2B9A7, teal #317371, sand #E3D1BA, brown #785F54, orange #F67E04.

## Layout
A sand rail on the left holds the client picker, an index of the five brief parts (each with its step number, a done or held back marker and what the part holds now) and the replay. The paper on the right has the client masthead, four KPI cards, the headline with the score bar, then the ledger: one row per step, the step in the left column (sticky while its part is read) and its part as a card beside it. This replaces the five column lanes of after2 with rows.

## 60 30 10
- 60: ivory paper #F6F2E9 and cards #FDFBF6.
- 30: sand for the rail (#EDE3D3, #E3D1BA in the group bars), sage and teal for structure: done step numerals, pressed controls, links, this client's group bar, worth discussing.
- 10: orange #F67E04, only for what must not be missed: the held back step numeral and status, the rule beside "What not to offer" and the held back KPI. It is a fill behind ink text, never text itself; held back words use the darkened #A04B00.

## Fonts
Google Fonts: Playfair Display 500, 600 and italic 500 (client name, headline, part titles, KPI values, step numerals, with lining figures) and Geist 400, 500, 600 (all data and UI).

## Contrast
`contrast.py` checks 48 pairs and exits 0. Lowest results: orange-text on sand 4.72, ink-3 on paper-2 4.89, st-none on its tint 4.90, teal mark on paper 4.92. Ink on paper 13.55, ink on orange 5.70, card on teal 5.31.

## Below 900px at 1440x900
The first view shows the rail index of all five parts with their status, the masthead, the KPI cards, the headline with the bar, and the start of row 1 (step 1 and the top of part 1; row 1 starts at 471 to 505px across the 40 clients). Rows 2 to 5 start between 1004 and 2830px, so parts 2 to 5 are one scroll or a click in the rail index away.

## Not done
No dark mode. On a phone the rail becomes a header and the index is hidden; each step sits directly above its part.
