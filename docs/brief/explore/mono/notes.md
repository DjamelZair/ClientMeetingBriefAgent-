# Direction B, Mono

Open `index.html` from a server on the docs folder (`python -m http.server` inside `docs`, then `/brief/explore/mono/`). It reads `../../../data.json` through `../../../field.js` and a copy of `variants.js` kept in this folder, so the shared page stays untouched.

## References and what each one gave
- **Tasklify board** (`Designrules/bestoneforagenticaifornow.jpg`, the primary reference): the skeleton. It gave the warm neutral canvas around one window, the white rounded panel, the breadcrumb top bar with a black primary control (Next client), and the slim agent banner (icon square, one line, Replay). It also gave the four stat tiles with a black icon square and a "Step n" link to the step that made them, the segmented view switch (Board and Tool log, both real views), and the board itself: one column per agent step. Each column is headed by a status pill with a card count, and that step's brief items sit under it as cards.
- **Vocalyn** (`6304b2cd`): the left sidebar, where the nav items are the five agent steps (each names its part, and the pinned one turns into a black pill). It also gave the greyscale restraint and the segmented bar meters, used here as the ten segment take up meter on "worth discussing" and "worth asking about".
- **Jobgio** (`293fb722`): the stat tile anatomy (icon, value, label), the black filled pill for the active state, and the client card at the foot of the sidebar.
- **Neumorphism** (`b5b20b6b`), lightly: the soft lift on cards (`--sh-card`, a faint inset highlight plus a tinted drop). Nothing is extruded.
- **Fashion palette** (`fc8b2a32`): #0A0C12, #3F3A42, #76828E and the one signal #DB5227. The navy in that palette is not used.

## 60-30-10
- **60, surfaces:** the white panel and cards, the warm grey window (#F6F5F3) and the board floor (#F2F1EE), on a #E7E3DC canvas.
- **30, greys:** near black #0A0C12 for text, pills and icon squares; graphite #3F3A42 for secondary text; #5E646C for quiet text; slate #76828E only for marks.
- **10, signal:** #DB5227 appears only where something is held back: the held back tile, step 3's marker and pill, the rule on the held back card and wallet row, the overdue timeline dot, and the held back segment in the agent meter. For text it darkens to #B4441C. When nothing is held back the page is fully grey, which keeps it calm.

## Type
Geist 400, 500 and 600 for everything, and Geist Mono 500 for the digits in markers, counts and meters. Both come from Google Fonts with the exact families and weights in the URL. Scale: 28 headline, 20 stat value, 15 title, 14 body, 13 small, 12 caption. Sentence case only.

## Tokens
All tokens are in the `:root` block at the top of `mono.css`: colour roles, type scale, a 4px space ladder, radii and shadows. The radius rule is 22 for the window, 18 for the panel, 14 for cards and tiles and 10 for wells and icon squares; everything pressable is a full pill. The shadows are tinted to the ink, never pure black.

## Contrast (`python contrast.py`, exit 0, 29 pairs)
- Text, 4.5:1 minimum. Ink on white is 19.55; graphite on white is 11.08; #5E646C is 5.01 on the lit grey and 5.97 on white. White on ink is 19.55, and white on #B4441C is 5.55. #B4441C is 5.55 on white and 4.82 on the signal tint.
- Marks, 3:1 minimum. The signal is 4.00 on white, 3.48 on its tint and 3.54 on the board floor. Slate is 3.92 on white. A filled meter segment against an empty one is 12.71.
- The script also fails if a raw colour appears outside the token block.

## Hard rules
1. The banner says that the agent prepares and the advisor decides, and the headline keeps the shared wording ("Worth discussing", never an order).
2. Synthetic fields stay labelled: the review tile, the review card's "Synthetic date." chip, the timeline and the context line.
3. No raw probability is shown. The meters show the observed take up in the client's score band from data.json, and the tool log cuts the propensity call down to its count, as the step line does.
4. Held back items stay visible and explained, in their own card with the reason, on a tile and in the sidebar.
5. Every number comes from data.json; the HTML holds only labels.
6. Each step heads its own column, its part title sits directly under it, and its cards follow. Hovering a column lights its sidebar item, and the reverse works too. A pin turns both black, and every tile, tag and sidebar item selects its step.

## Checks
`checks/mcheck.py` walks all 40 clients at 1440x900 and 390x844 and works the bar, every first answer, a step link, the tool log, Replay and the draft on each client. Result: no empty mounts, no console errors and no horizontal scroll. No U+2013 or U+2014 appears in this folder. Screenshots are in `shots/`.

## What falls below 900px at 1440x900
Above the fold: the headline, the agent banner, the four tiles, the view switch and bar, all five step headers (twice, in the sidebar and on the board), every part title, and the first card of every column. Below 900px: the rest of column 1 (timeline and products), any second card in columns 2 and 3, the review detail on some clients, every question after the first, and the footer. On a phone the client card comes first, the steps stack in order with each column's cards directly under its step, and the products fold behind a button that counts what is inside, held back included.

## Not done
- There is no dark mode, because the direction is a light monochrome product.
- At 1180px and below, the board scrolls sideways inside the panel; this was not screenshot checked.
