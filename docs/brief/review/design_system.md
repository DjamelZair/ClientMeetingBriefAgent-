# Design system audit of docs/brief

Scope: docs/brief/tokens.css, docs/brief/variants.js, docs/brief/index.html and docs/brief/contrast.py, as they stand on 23 October 2026. The DESIGN.md files for IBM, Mercury and Linear were read as reference values only. No page code was changed. Desktop (1440x900, 1280x800) is the main target; the phone layout (390px) is a secondary target and is covered in the breakpoint rows of each component table.

## Summary

**Components reviewed:** 29 registered in `V.components` (22 mounted by index.html, 7 not mounted) | **Issues found:** 41 | **Score:** 68/100

The base is sound. Every colour on the page is a token, the four schemes and three ds layers are cleanly split, and contrast.py passes: 468 pairs, 0 failing, exit code 0. Where it falls short:

1. **Colour tokens repeat each other.** Eight colour roles have the same value as another role in every scheme. Two more match in three schemes out of four. Five tokens are never used.
2. **Some colours slip past the check.** The scheme swatches in variants.js are raw colour literals that contrast.py never scans, and they pick different token roles in each scheme.
3. **The type scale is wider than it needs to be.** There are 8 rendered sizes on desktop: six tokens plus a 10px and an 11px literal in the band chart. One token (`--t-xl`) is used by a single element. Six line heights and one letter spacing value are literals.
4. **Small gaps are off the scale.** Gaps of 2, 3, 5 and 6px appear 40 times beside the 4px scale. Component sizes (28, 20, 44, 26, 13.25, 34, 38px) are bare literals.
5. **States differ between controls.** There are four different "pressed" looks and three different "lit" looks. One clickable card has no hover and no keyboard route. Held back emphasis looks different in each ds layer. In Mercury the skeleton cannot be seen inside a part.
6. **Names collide.** `.sw`, `.lbl`, `.nm` and `.st` each mean two or three different things. "lane" names three different things. `data-s`, `data-st`, `data-status` and `data-tone` all carry state. Mercury and Linear map `--w-title` to the wrong weight from their own files.

## 1. Token inventory

### 1.1 Colour, per scheme (tokens.css lines 9 to 176)

35 colour tokens per scheme, plus `--shadow`, which is not a colour and is unused. The table marks values that are identical to another token in that scheme (`=`) or within 2% lightness and 0.01 chroma of it (`~`).

| Token | S1 teal and cherry | S2 calm banking | S3 dark slate | S4 warm paper | Used | Finding |
|---|---|---|---|---|---|---|
| `--bg` | 98.4% 0.003 220 | 95.6% 0.005 255 | 18.5% 0.016 252 | 96.2% 0.013 85 | yes | |
| `--surface` | 99.8% 0.001 220 | 99.6% 0.002 255 | 22.5% 0.018 252 | 98.6% 0.008 85 | yes | |
| `--surface-2` | 96.6% 0.006 220 | 96.4% 0.006 255 | 26.5% 0.02 252 | 93.6% 0.016 82 | yes | |
| `--line` | 90.5% 0.007 220 | 90% 0.009 255 | 32% 0.02 252 | 87.5% 0.018 80 | yes | |
| `--line-2` | 80% 0.012 220 | 80% 0.016 255 | 44% 0.022 252 | 76% 0.025 75 | yes | |
| `--ink`, `--ink-2`, `--ink-3` | 23.5 / 42 / 50% | 25 / 41 / 49% | 95.5 / 81 / 72% | 24 / 41 / 48% | yes | |
| `--accent` | #1F4E5F | 33% 0.095 262 | 80% 0.075 248 | 41% 0.07 195 | yes | |
| `--on-accent` | 98.8% 0.004 220 | 98.8% 0.004 255 | 19% 0.03 252 | 98.6% 0.008 85 | yes | S4: `= --surface` |
| `--accent-soft` | 94.6% 0.018 215 | 94% 0.02 258 | 31% 0.04 250 | 92.8% 0.025 190 | yes | |
| `--accent-text` | #1F4E5F | 36% 0.1 262 | 84% 0.07 248 | 40% 0.07 195 | yes | S1 `= --accent`, S4 `~ --accent` |
| `--mark` | #1F4E5F | 33% 0.095 262 | 80% 0.075 248 | 61% 0.13 68 | 1 rule | S1 to S3 `= --accent`; name collides with "marker" |
| `--alarm` | #982649 | 47% 0.16 18 | 73% 0.15 12 | 46% 0.15 30 | yes | S1, S2, S4 `= --st-heldback`; S3 `~` |
| `--alarm-soft` | 95.6% 0.018 5 | 95.6% 0.02 15 | 30% 0.06 12 | 94.4% 0.025 35 | yes | `= --st-heldback-bg` in all four |
| `--alarm-text` | #982649 | 47% 0.16 18 | 80% 0.12 12 | 45% 0.15 30 | yes | S1, S2 `= --st-heldback`; S3, S4 `~` |
| `--st-held` / `-bg` | 36% 0.025 245 / 94.6% | 36% 0.06 262 / 94.4% | 84% 0.04 250 / 30% | 34% 0.03 60 / 92.8% | fg yes, bg **no** | `-bg` unused since the wallet lost its tints |
| `--st-discuss` / `-bg` | 43% 0.075 205 / 94.4% | 45% 0.11 152 / 95% | 82% 0.13 165 / 30% | 42% 0.075 192 / 93.4% | yes / 1 rule | |
| `--st-progress` / `-bg` | 47% 0.095 65 / 95.4% | 48% 0.1 68 / 95.6% | 85% 0.13 85 / 31% | 46% 0.1 68 / 93.8% | fg yes, bg **no** | |
| `--st-heldback` / `-bg` | #982649 / 95.6% | 47% 0.16 18 / 95.6% | 78% 0.13 12 / 30% | 46% 0.15 30 / 94.4% | yes | |
| `--st-none` / `-bg` | 50% 0.008 225 / 97% | 50% 0.012 255 / 97% | 72% 0.012 250 / 24% | 49% 0.02 70 / 95.4% | fg yes, bg **no** | |
| `--care-ink`, `--care-bg` | 37% 0.06 265 / 95.4% | 38% 0.07 235 / 95% | 85% 0.07 295 / 29% | 37% 0.055 255 / 93.6% | yes | a sixth hue, kept apart from the states on purpose |
| `--avatar-bg`, `--avatar-ink` | #1F4E5F / 98.8% | 33% 0.095 262 / 98.8% | 31% 0.04 250 / 88% | 68% 0.13 72 / 22% | 1 rule each | S1, S2 `= --accent` / `--on-accent`; S3 bg `= --accent-soft` |
| `--chart-bar` | 83% 0.012 220 | 84% 0.015 255 | 40% 0.02 252 | 82% 0.025 80 | 1 rule | |
| `--chart-me` | 43% 0.075 205 | 45% 0.11 152 | 82% 0.13 165 | 42% 0.075 192 | 1 rule | `= --st-discuss` in all four |
| `--chart-rule` | 42% 0.02 225 | 41% 0.045 262 | 81% 0.014 250 | 41% 0.022 60 | 1 rule | `= --ink-2` in all four |
| `--lit-bg` | 95.2% 0.03 205 | 95% 0.035 152 | 29% 0.045 165 | 92.6% 0.04 85 | yes | S2 `= --st-discuss-bg`, S1 `~` |
| `--lit-line` | 43% 0.075 205 | 45% 0.11 152 | 82% 0.13 165 | 51% 0.11 68 | yes | S1 to S3 `= --st-discuss` |
| `--focus` | #1F4E5F | 33% 0.095 262 | 80% 0.075 248 | 41% 0.07 195 | 1 rule | `= --accent` in all four |
| `--shadow` | 0 1px 2px ... | two layer | inset 1px | 0 1px 2px ... | **no** | dead in every scheme |

The five product states keep one meaning across schemes: held (neutral ink, filled tick), worth discussing (teal or green, speech bubble), likely in progress (amber or ochre, half circle), held back (cherry or red, barred circle), not in data (grey, dashed circle). This audit changes none of their values, glyphs or words.

### 1.2 Typography (ds blocks, lines 184 to 432)

| Token | IBM | Mercury | Linear | Used by |
|---|---|---|---|---|
| `--f-ui`, `--f-head`, `--f-read` | Plex Sans x3 | Inter x3 | Roboto x3 | the three are identical in every layer |
| `--f-code` (shared) | ui-monospace stack | same | same | `.v-tool` only |
| `--t-xs` / `--lh-xs` / `--ls-xs` | 12 / 1.33 / 0.32px | 12 / 1.4 / 0.24px | 12 / 1.4 / 0 | 30+ rules |
| `--t-s` / `--lh-s` / `--ls-s` | 14 / 1.29 / 0.16px | 14 / 1.4 / 0.07px | 14 / 1.5 / 0 | 25+ rules |
| `--t-m` / `--lh-m` / `--ls-m` | 16 / 1.5 / 0.16px | 16 / 1.4 / 0 | 16 / 1.5 / -0.05px | body, step names, questions |
| `--t-l` / `--lh-l` / `--ls-l` | 20 / 1.4 / 0 | 18 / 1.35 / 0 | 20 / 1.4 / -0.2px | part titles, stat values |
| `--t-xl` / `--lh-xl` / `--ls-xl` | 24 / 1.33 / 0 | 24 / 1.2 / 0.48px | 22 / 1.25 / -0.4px | **`.v-name` only** |
| `--t-2xl` / `--lh-2xl` / `--ls-2xl` | 32 / 1.25 / 0 | 28 / 1.2 / 0.42px | 28 / 1.2 / -0.6px | `.v-head` only |
| literal 11px, 10px | | | | `.v-ilad .me-t`, `.v-ilad .ax-t` (tokens.css 677, 678) |

Weights:

| Token | IBM | Mercury | Linear | Finding |
|---|---|---|---|---|
| `--w-body` | 400 | 400 | 400 | |
| `--w-ui` | 400 | 420 | 500 | |
| `--w-strong` | 600 | 500 | 500 | carries 20 roles: badges, state words, item names, lane heads, step names, markers |
| `--w-title` | 400 | **360** | **400** | Mercury 360 is its body-lg (description) weight, not a heading weight; heading-2 is 480. Linear card-title is 500. Both are mismapped. |
| `--w-head` | 400 | 480 | 600 | |

Literal line heights that bypass the scale: `1.2` (`.v-btn`), `1.25` (`.v-step-btn`), `1.3` (`.v-item .nm`), `1.4` (`.v-tool`), `1.5` (`.v-fu-t`), and `/1` x3 for markers and badges. The `/1` cases are fine because they centre a single line.

`--ls-*` is applied in some caption rules and not in others. These rules miss it: `.v-badge`, `.v-st`, `.v-wrow .sw`, `.v-legend`, `.v-ans-l`, `.v-fu-a`, `.v-review .syn`, `.v-bar`, `.v-switch .lbl`, `.v-tl-key`, `.v-care`, `.v-out`. In IBM that means two kinds of 12px text with different tracking, side by side.

The `.t-xs` and `.t-s` utilities (tokens.css 465, 466) are never output by variants.js or index.html.

### 1.3 Spacing

| Token | IBM | Mercury | Linear | Used |
|---|---|---|---|---|
| `--sp-1` to `--sp-6` | 4, 8, 12, 16, 24, 32 | same (file base is 8; 4 is a flagged fallback) | same | yes |
| `--sp-7` | 48 | 40 | 48 | **no** |
| `--card-pad` | 16 | 12px 16px | 16 | parts, stat cards |
| `--row-py` | 4 | 10 | 4 | wallet rows |
| `--badge-pad` | 2px 8px | 2px 8px | 2px 8px | identical in all three, so it belongs in the shared block |

Off-scale literals in component CSS (tokens.css 434 to 746 and the index.html style block): `2px` x19 (mostly row gaps), `3px` x9, `5px` x6, `6px` x8, `1px` padding x2, `padding: 0 5px` on `.v-from`, `margin-top: 1px/2px` glyph nudges x5.

Component sizes that are bare literals: step marker `28px` (x9 including `grid-template-columns`, `min-height`, `padding-right`), from tag `20px`, avatar `44px`, brand mark `26px`, rail offsets `13.25px`, `34px` and `38px`, status offset `top: 5px`, select `padding-right: 28px` and chevron `right: 12px`, picker `max-width: 300px` and `width: 240px`.

### 1.4 Radii

| Token | IBM | Mercury | Linear | Used by | Finding |
|---|---|---|---|---|---|
| `--r-s` | 2 | 4 | 4 | skeleton, skip link, brand mark | |
| `--r-m` | 0 | 8 | 8 | items, review, care, out, select, picker buttons, every `[data-from]` | `[data-from]` sets a radius on spans, svg groups and list rows, and `.v-wrow` has to undo it |
| `--r-l` | 0 | 12 | 12 | cards, stat cards, avatar | |
| `--r-btn` | 0 | 40 | 8 | `.v-btn`, answer buttons | the picker's prev and next use `--r-m` instead |
| `--r-pill` | 9999 | 9999 | 9999 | **unused** | |
| `--r-marker` | 0 | 9999 | 9999 | step marker, from tag | |
| `--badge-r` | 2 | 4 | 9999 | badges, status | named outside the `--r-*` family |
| `--tab-r` | 0 | 40 | 9999 | segs, switches | named outside the `--r-*` family |
| literal `3px` | | | | `.v-tl-key i` | |

### 1.5 Borders, shadows, depth, motion, z

| Kind | Values in use | Finding |
|---|---|---|
| Border width | `--card-bw` (1, 0, 1), literal `1px` x14, literal `1.5px` x5 (marker, rail, stem, select chevron), dashed `1px` for aside items and the "none" marker | no token for the hairline or the rail |
| Focus | `--focus-w` 2px, `outline-offset: 2px` literal | fine |
| Card shadow | `--card-shadow: none` in all three layers | always none, so it is noise |
| Hover lift | `--card-hover-bg`, `--card-hover-line` | **unused**: no card has a hover rule |
| Ad hoc box-shadows | lit ring `0 0 0 3px lit-bg, 0 0 0 4px lit-line`; lane ring `0 0 0 1px lit-line`; held rule `inset 0 3px 0 st-heldback` (x3); tab underline `inset 0 -2px 0`; rail halo `0 0 0 4px var(--bg)` | five shapes, none tokenised |
| Mercury card line | `--card-line: var(--surface-2)` with `--card-bw: 0px` | a line that can never show |
| Motion | `--dur` 220ms, `--ease`; literals 120, 150, 200, 240, 260 (x2) and 900ms in CSS; 360, 220 and 150 plus the easing string `cubic-bezier(.22,1,.36,1)` x2 in variants.js 684 and 755 | the JS copies the easing instead of reading it |
| z | `--z-raise`, `--z-sticky` (**unused**), `--z-skip` | |
| Header | `--hdr-h` 48 / 56 / 56; `--ctl-h` 32; `--btn-h` 0 / 40 / 0 | `--btn-h: 0px` is used as "off", which is not a real size |

### 1.6 Hardcoded values in variants.js

| Line | Value | Problem |
|---|---|---|
| 35 to 38 | `SCHEMES[].sw`: `#1F4E5F`, `#982649`, `oklch(33% 0.095 262)`, `oklch(45% 0.11 152)`, `oklch(22.5% 0.018 252)`, `oklch(82% 0.13 165)`, `oklch(68% 0.13 72)`, `oklch(41% 0.07 195)` | Raw colours outside the scheme blocks. contrast.py's `raw_colours()` only scans tokens.css and index.html, so these pass unseen. They also copy different roles in each scheme: S1 accent and alarm, S2 accent and st-discuss, S3 surface and st-discuss, S4 avatar-bg and accent. A change to a scheme token silently leaves its swatch stale. |
| 598 | `style="background:' + s.sw[0] + '"` | inline style carrying the literal |
| 144 | glyph `held` uses `stroke="var(--surface)"` | a token, but the tick is drawn in the card colour, not an "on state" colour |
| 157 | `st-x` class for info, group, care and replay | a class with no rule; harmless but misleading |
| 180, 415, 460 | `style.display = "inline"`, `vertical-align: -2px / -1px`, `margin-right: 4px / 5px` | inline glyph styling done three ways, by string replacement on the class attribute |
| 296 | `style="stroke-width:1"` | inline style in the timeline |
| 474 | `style="margin-left:auto"` | inline layout |
| 280, 297, 418 | `6.9` px per character, dot radii `5.5` / `4.5`, chart `IW 12, IG 2, IH 28` | chart geometry; acceptable as chart constants, but the 6.9 guess is tuned to one face and every ds changes the face |
| 335 | `ws.w.length > 10 ? ' stack'` | layout chosen by string length, not by measured width |
| 684, 755 | `duration: 360`, `duration: 220`, `easing: "cubic-bezier(.22,1,.36,1)"` | copies of motion tokens |

## 2. Naming

| Issue | Where | Recommendation |
|---|---|---|
| `.sw` means three things | status word in `.v-stat`, status word in `.v-wrow`, swatch in `.v-switch` | `.v-word` for the status word, `.v-swatch` for the swatch |
| `.lbl` means two things | stat label, switch label | `.v-stat-label`, `.v-switch-label` |
| `.nm` in three components | wallet row, item, index.html `.grp` | keep it scoped (`.v-wrow-name`, `.v-item-name`), or accept it as a documented local name |
| `.st` vs `.v-st` vs `.st-*` | review status line, step status badge, state colour classes | `.v-review-status`; `.v-step-status`; keep `.st-*` for the five states only |
| "lane" names three things | page `.lane` (a step plus its part), component `.v-lane` (a sub list), model `lane()` (offer, ask, hold...) | page `.spine-col`; keep `.v-lane` for the list; the model keeps `lane` |
| state attributes | `data-s` (run state), `data-status` (result), `data-st` (wallet, review), `data-tone` (stat), `data-lane` (item) | `data-run` for run state, `data-result` for the step result, `data-state` for any of the five product states, drop `data-tone` |
| `--alarm*` vs `--st-heldback*` | same colour, two names | one family: `--st-heldback`, `--st-heldback-bg`, `--st-heldback-fill` |
| `--mark` vs marker | `--mark` is the meeting dot colour; `--r-marker` and `.v-step-n` are the step marker | rename to `--tl-meet` |
| `--w-title` vs `--w-head` | "title" and "head" are not clear apart | `--w-title` (part titles, stat values) and `--w-headline` |
| `--badge-r`, `--tab-r`, `--badge-pad` | outside their families | `--r-badge`, `--r-tab`, `--pad-badge` |
| class vs component | component `summary` makes `.v-sum`/`.v-stat`; `partHead` makes `.v-part-h`; `fromTag` makes `.v-from`; `bandChart` makes `.v-ilad` | class follows the component name: `.v-summary`, `.v-part-head`, `.v-step-tag`, `.v-band-chart` |
| `ds` | means design system in `C.ds`, `#ds`, `data-ds`, and `ds.set` | fine on its own, but the label "Design" in the switch should read "Design system" where there is room |
| `S` | the state object, and S1 to S4 | the code can keep it; the docs should say "scheme S1" |

## 3. Component inventory and findings

### 3.1 Registered components

| Component | Mounted by index.html | Own CSS | Note |
|---|---|---|---|
| identity, facts, summary, timeline, wallet (wrapped), headline, care, discuss, ask, held, aside, review, bar (wrapped as scoreBar), questions, followup, step, partHead, skeleton, picker, ds, scheme, footer | yes (22) | yes | |
| chips | **no** | **none** (`.v-chips`, `.v-chip` have no rules) | dead; it overlaps facts and summary |
| mismatch, groupNote | no | shared | groupNote is duplicated by index.html's own `groupCard` |
| meeting | no | none (`.v-meeting`) | dead |
| legend | no | yes | the states are explained only by the words next to them, which is enough |
| steps | no | none for `.v-agent-h`, `.v-agent-t`, `.v-agent-sub`, `.v-steps`, `.v-replay` | duplicated by index.html's `agentHead` |
| ranked | no | none (`.v-ranked`) | kept for the raw output comparison; must stay labelled raw if ever mounted |

### 3.2 State consistency

| State | What exists | Inconsistency |
|---|---|---|
| Hover | `.v-btn` surface-2; `.v-step-btn` surface-2; `.v-link` underline colour; `.v-from` lit border; segs and switches ink colour only; lane hover rings the part | `.v-stat` has `cursor: pointer` but no hover. `[data-from]` parts are clickable but give no hover cue of their own (only the lane ring). Seg hover changes only text colour, so on Mercury's tinted pills it is barely visible. |
| Focus | one global `:focus-visible` 2px outline in `--focus`, offset 2px | Consistent. But `.v-stat` and `[data-from]` click targets cannot take focus, so the summary card's step link is mouse only. |
| Pressed (selected) | answer `.v-btn`: accent fill; segs and switches: tab-on tokens; `.v-step-btn`: lit-bg + lit-line border; `.v-from`: lit-line fill with `--surface` text | Four looks. Answers and segs are both "one of a set", yet they look different. The step button and the from tag are both "this step is linked", yet they look different. |
| Active (mouse down) | `.v-btn` translateY(1px) | only `.v-btn` |
| Lit (linked step) | `[data-from][data-lit]`: lit-bg fill + 3px/4px double ring; `.lane[data-on] > .part`: 1px ring; `.lane[data-on] .v-step-n`: 3px/4px ring | A pinned link draws a 1px ring on the part *and* a tinted 4px ring on every element inside it, so rings nest inside rings. Hover draws only the outer one. Hover and pin should look the same, apart from the pin persisting. |
| Disabled | none | Nothing is disabled today (prev and next wrap round). There is still no spec for when a control cannot act, for example Replay with one step. |
| Empty | `.v-none` text (discuss, held); hidden mount (ask, aside, care, mismatch, followup); "No review date on file"; "No recorded changes in the last six months"; "Nothing held back"; "No products in this data" | Fine by rule 4 (held back always shows, even when empty), but two empty styles exist: `.v-none` (ink-3, t-s) and `.v-tl-key li.none` (ink-3, t-xs). |
| Loading | `.v-sk` lines in `--surface-2` | **Mercury bug:** `.part` is a `.v-card` with `--card-bg: var(--surface-2)`, so the skeleton bars are the same colour as the card behind them and cannot be seen. In IBM and Linear, S1 gives 99.8% against 96.6%, which is faint. |
| Waiting (replay) | `[data-from][data-ready="0"]` opacity 0; `.lane:not([data-done]) > .part > *` opacity 0.35; step badge "Waiting" in ink-3 | Two fade mechanisms on the same elements, at different opacities. |
| Held back | `.v-stat[data-tone=heldback]`: border colour + inset 3px top rule; `.part[data-hold]`: inset 3px top rule + red title; `.v-item[data-lane=hold]`: st-heldback-bg fill; step marker: `--alarm` fill | In Mercury `--card-bw` is 0, so the stat card loses its border and keeps only the top rule. On a 12px radius that rule draws as a curved smile (visible in after/desktop_mercury_S1_client10.png). In IBM the same card gets a full border. The emphasis should not depend on the ds layer. |
| Run (replay) | marker accent border + scale 1.08 | fine |

## 4. Proposed token set

Everything below keeps the four schemes, the three ds layers, the five states with their glyphs and words, and the 4.5:1 and 3:1 thresholds. New values are taken from the DESIGN.md files or marked "not specified, fallback".

### 4.1 Colour (scheme blocks keep literal values; aliases move to one shared block)

Per scheme, literal (26): `--bg`, `--surface`, `--surface-2`, `--line`, `--line-2`, `--ink`, `--ink-2`, `--ink-3`, `--accent`, `--on-accent`, `--accent-soft`, `--accent-text`, `--st-held`, `--st-discuss`, `--st-discuss-bg`, `--st-progress`, `--st-heldback`, `--st-heldback-bg`, `--st-heldback-fill` (was `--alarm`), `--st-none`, `--care-ink`, `--care-bg`, `--avatar-bg`, `--avatar-ink`, `--chart-bar`, `--tl-meet` (was `--mark`), `--lit-bg`, `--lit-line`.

Shared aliases, in one `:root` block after the schemes (6):

```css
:root, [data-scheme] {
  --focus: var(--accent);
  --chart-me: var(--st-discuss);
  --chart-rule: var(--ink-2);
  --on-heldback: var(--surface);   /* text on the held back step marker */
  --on-lit: var(--surface);        /* text on a pressed step tag */
  --sk: var(--line);               /* skeleton bars, visible on every card fill */
}
```

The selector includes `[data-scheme]` so that the aliases resolve again on any element that carries its own scheme. This is what the swatch fix in 5.1 relies on.

Removed: `--alarm-soft` (use `--st-heldback-bg`), `--alarm-text` (use `--st-heldback`; both pairs already pass as text in all four schemes), `--st-held-bg`, `--st-progress-bg`, `--st-none-bg` (unused), `--shadow` (unused). Net: 35 per scheme down to 28, plus 6 aliases.

Kept separate on purpose: `--accent-text` (differs from `--accent` in S2, S3 and S4), `--lit-line` (S4 uses amber), `--avatar-*` (S3 and S4 differ), `--tl-meet` (S4 uses amber), `--st-heldback-fill` (S3 needs a darker fill than the text colour to carry `--on-heldback`).

### 4.2 Type (role names, five desktop sizes)

| Role token | IBM | Mercury | Linear | Replaces |
|---|---|---|---|---|
| `--t-caption` / `--lh-caption` / `--ls-caption` | 12 / 1.33 / 0.32px | 12 / 1.4 / 0.24px | 12 / 1.4 / 0 | `--t-xs`, the 10px and 11px chart literals |
| `--t-body-sm` / `--lh-body-sm` / `--ls-body-sm` | 14 / 1.29 / 0.16px | 14 / 1.4 / 0.07px | 14 / 1.5 / 0 | `--t-s` |
| `--t-body` / `--lh-body` / `--ls-body` | 16 / 1.5 / 0.16px | 16 / 1.4 / 0 | 16 / 1.5 / -0.05px | `--t-m` |
| `--t-title` / `--lh-title` / `--ls-title` | 20 / 1.4 / 0 | 18 / 1.35 / 0 | 20 / 1.4 / -0.2px | `--t-l`, and `--t-xl` for the client name |
| `--t-headline` / `--lh-headline` / `--ls-headline` | 32 / 1.25 / 0 | 28 / 1.2 / 0.42px | 28 / 1.2 / -0.6px | `--t-2xl` |
| `--t-headline-sm` (phone only, at 760px and below) | 24 card-title / 1.33 | 24 lead / 1.2 | 22 card-title / 1.25 | new, so the headline wraps in two lines rather than four at 390px |
| `--lh-ui` | 1.29 (button) | 1 (ui), fallback 1.2 for wrapping labels, flagged | 1.2 (button) | the literal 1.2 and 1.25 |

Weights (5 roles):

| Role | IBM | Mercury | Linear | Change |
|---|---|---|---|---|
| `--w-body` | 400 | 400 | 400 | none |
| `--w-ui` | 400 | 420 | 500 | none |
| `--w-strong` | 600 | 500 | 500 | none |
| `--w-title` | 400 | **480** (heading-2) | **500** (card-title) | fixes two mismaps |
| `--w-headline` | 400 | 480 | 600 | rename of `--w-head` |

Fonts: collapse `--f-ui`, `--f-head` and `--f-read` into `--f-sans` per layer, since all three are identical everywhere. Keep `--f-code`.

Rule: any rule that sets a font size sets the matching line height and letter spacing from the same role. A one line shorthand token per role makes that the easy path, for example `--type-caption: var(--w-body) var(--t-caption)/var(--lh-caption) var(--f-sans);` used as `font: var(--type-caption); letter-spacing: var(--ls-caption);`.

### 4.3 Space and size

| Token | Value | Note |
|---|---|---|
| `--sp-0` | 2px | not specified in any file (IBM and Linear base 4, Mercury base 8); fallback for label and value stacks only |
| `--sp-1` to `--sp-6` | 4, 8, 12, 16, 24, 32 | unchanged |
| `--sp-7` | remove | unused |
| `--pad-card`, `--pad-row`, `--pad-badge` | as now | `--pad-badge` moves to the shared block |
| `--size-marker` | 28px | not specified; drives the rail offsets with `calc()` |
| `--size-tag` | 20px | not specified |
| `--size-avatar` | 40px | Linear avatar 32 to 40, Mercury control 40; was 44 |
| `--size-glyph`, `--size-glyph-sm` | 16px, 14px | the 13px glyphs move to 14 |
| `--size-brand` | 24px | was 26; on the 4px grid |

Snap rules: 3px becomes 4 (`--sp-1`); 5px and 6px become 4 for glyph to word gaps and 8 for block gaps; 1px padding becomes 0 or `--sp-0`.

### 4.4 Shape, line, depth, motion

| Token | IBM | Mercury | Linear | Replaces |
|---|---|---|---|---|
| `--r-badge` | 2 | 4 | 9999 | `--badge-r` |
| `--r-small` | 2 | 4 | 4 | `--r-s`: skeleton, skip link, brand mark, timeline key |
| `--r-control` | 0 | 40 | 8 | `--r-btn` |
| `--r-select` | 0 | 8 (sm: selects) | 8 | the picker's `--r-m` on the select |
| `--r-icon` | 0 | 9999 (button-icon-round) | 8 | the picker's prev and next |
| `--r-tab` | 0 | 40 | 9999 | `--tab-r` |
| `--r-item` | 0 | 8 | 8 | `--r-m` |
| `--r-card` | 0 | 12 | 12 | `--r-l` |
| `--r-marker` | 0 | 9999 | 9999 | unchanged |
| `--bw` | 1px | 1px | 1px | literal 1px hairlines |
| `--bw-rail` | 1.5px | 1.5px | 1.5px | not specified; the rail, stem and marker ring |
| `--bw-tab` | 2px | 2px | 2px | IBM selected tab underline; the `inset 0 -2px 0` |
| `--focus-w` | 2px | 2px | 2px | unchanged; move to the shared block |
| `--ring-lit` | `0 0 0 1px var(--lit-line)` | same | same | the lane ring and the `[data-lit]` double ring |
| `--rule-hold` | `inset 0 0 0 1px var(--st-heldback), inset 0 3px 0 var(--st-heldback)` | same | same | the three held back emphases; works whatever `--card-bw` is |
| `--halo` | `0 0 0 4px var(--bg)` | same | same | the rail status halo |
| `--dur-fast`, `--dur`, `--dur-slow`, `--dur-flash` | 120, 220, 360, 900ms | same | same | 120, 150, 200, 240, 260, 900 literals and the JS 360 and 220 |
| `--ease` | unchanged | | | read from CSS in JS |

Removed: `--card-shadow`, `--card-hover-bg`, `--card-hover-line`, `--r-pill`, `--z-sticky`, `--btn-h: 0px` (use `min-height: auto` in IBM and Linear, `--ctl-lg: 40px` in Mercury), Mercury's `--card-line` (keep only `--card-bw: 0`).

### 4.5 Breakpoints

CSS custom properties cannot be used in media queries, so these are named in a comment at the top of tokens.css and used literally:

| Name | Query | What changes | Source |
|---|---|---|---|
| wide | min 1600px | the brand subline shows | page |
| desktop | 1367 to 1599 | the brand subline hides | page |
| laptop | max 1399px **and** max 1366px | merge into one breakpoint at max 1399: switch labels hide, picker 240px, gaps tighten to `--sp-4` | page; the two are 33px apart and both fire at 1366 |
| tablet | max 1099px | two lanes a row, header wraps, summary stacks | IBM 1056, Linear 1024, Mercury 1024 |
| phone | max 760px | one column, step over part, summary 2 x 2, links hide, headline uses `--t-headline-sm` | IBM 672, Linear 768, Mercury 768 |
| touch | pointer: coarse | controls reach `--touch` | 48 IBM, 44 Mercury and Linear |

## 5. Component specs

Each table lists anatomy, variants, states, tokens and breakpoints. "Lit" is the linked step state, by hover, focus or pin. "Waiting" is the replay state.

### 5.1 Summary (`C.summary`, `.v-sum` and `.v-stat`)

| | Spec |
|---|---|
| Anatomy | list of 4 cards; each card: label (caption, ink-3), value (title, `--w-title`, ink, tabular), status line (glyph 14 + word, body-sm, `--w-strong`, state colour), step tag (`.v-step-tag`, top right, new) |
| Variants | segment (step 1), tenure (step 1), review (step 4), held back (step 3) |
| States | default; **held back with items**: `--rule-hold`, value and word in `--st-heldback` (the same in all three ds); held back empty: quiet word "Nothing held back" in ink-3, no rule; review overdue: held back glyph and word; review due: progress; no date: not in data; hover: `--card-bg` stays, step tag gets lit border; lit: `--ring-lit`; loading: 3 `--sk` bars; waiting: opacity per the single replay rule |
| Interaction | remove `cursor: pointer` from the card. The step tag is the focusable control (keyboard and screen reader route). The card click stays as a mouse shortcut. |
| Tokens | `--card-bg`, `--card-bw`, `--card-line`, `--r-card`, `--pad-card`, `--t-caption`, `--t-title`, `--t-body-sm`, `--w-title`, `--w-strong`, `--st-*`, `--rule-hold`, `--ring-lit` |
| Breakpoints | at least 1100: 4 across, beside the identity block (1.45fr : 4fr); 760 to 1099: 4 across under the identity block; at most 760: 2 x 2; value wraps with `overflow-wrap` |

### 5.2 Facts (`C.facts`, `.v-facts`)

| | Spec |
|---|---|
| Anatomy | one line of pairs: label (caption, ink-3) + value (caption, `--w-strong`, ink, tabular), gap `--sp-0` x `--sp-4` |
| Variants | age, income recorded, meeting; care pair (care-ink) only when the care check fires |
| States | default; value "not recorded" in the same style; lit (step 1 or 3): `--ring-lit` on the pair; waiting |
| Tokens | `--t-caption`, `--lh-caption`, `--ls-caption`, `--ink-3`, `--ink`, `--care-ink` |
| Breakpoints | wraps freely at every width; unchanged on phone |
| Fix | `margin-left: 4px` becomes `--sp-1` |

### 5.3 Step (`C.step` and `stepHTML`, `.v-step`)

| | Spec |
|---|---|
| Anatomy | marker (`--size-marker`, `--r-marker`, `--bw-rail` ring, number at body-sm `--w-strong`); status badge (5.9); rail to the next marker and stem to the part (`--bw-rail`); step button (body, `--w-strong`, `--lh-ui`); Read and Returned captions (caption; dt ink-3, dd ink-2 / ink); "and n more" link (5.10); expandable detail (tool calls in `--f-code` caption) |
| Variants | step 1 to 5; `ret` keeps or drops the Returned line (steps 1 and 4 drop it) |
| States (run) | waiting: marker line-2 ring, ink-3, text ink-3; running: accent ring, accent-text, scale 1.08; done |
| States (result, when done) | done: accent fill, on-accent; blocked: `--st-heldback-fill`, `--on-heldback` ("Held back n", "Holds products"); nothing found: dashed ring, ink-3 |
| States (interaction) | hover on the button: surface-2; focus: global ring; lit (pressed): button `--lit-bg` + `--lit-line` border, marker `--ring-lit` plus lit-bg halo, stem `--lit-line`; this is the single "linked" look, shared with 5.4 |
| Tokens | `--size-marker`, `--bw-rail`, `--line-2`, `--accent`, `--on-accent`, `--st-heldback-fill`, `--on-heldback`, `--lit-*`, `--halo`, `--dur`, `--ease` |
| Breakpoints | at least 1100: five across with rails; 760 to 1099: 2 per row, rails hidden on the right hand lane; at most 760: stacked, rails hidden, stem kept, `--sp-5` above each step |
| Fix | rail offsets `13.25px`, `34px`, `38px`, `top: 5px` become `calc()` on `--size-marker` and `--bw-rail`; `transition 150ms` and `200ms` become `--dur-fast` and `--dur`; `data-s` becomes `data-run`, `data-status` becomes `data-result` |

### 5.4 Part head and step tag (`C.partHead`, `.v-part-h`, `fromTag`, `.v-from`)

| | Spec |
|---|---|
| Anatomy | h2 title (title role, `--w-title`); optional glyph 16; step tag at the right (`--size-tag`, `--r-marker`, caption `--w-strong`, tabular) |
| Variants | parts 1 to 5; part 3 with held items turns the title `--st-heldback` |
| States (tag) | default: `--bw` line-2 ring, ink-2 on surface; hover: lit-line ring, ink; focus: global ring; pressed (lit): `--lit-bg` fill, `--lit-line` ring, ink text (the same as the step button; the full lit-line fill with surface text goes) |
| Tokens | `--t-title`, `--lh-title`, `--w-title`, `--size-tag`, `--lit-*`, `--bw` |
| Breakpoints | unchanged; touch: the hit area grows to `--touch` through padding, not size |
| Fix | `padding: 0 5px` becomes `0 var(--sp-1)`; `padding-right: 28px` becomes `calc(var(--size-tag) + var(--sp-2))` |

### 5.5 Cards: part, item, review, care, out

| | Part `.part.v-card` | Item `.v-item` | Review `.v-review` | Care `.v-care` | Outcome `.v-out` |
|---|---|---|---|---|---|
| Anatomy | part head, mounts, `.part-sub` with a `--bw` top rule | name (body, `--w-strong`, `--lh-title`) + evidence (body-sm, ink-2) + optional band chart | status (body, `--w-strong`) + detail (body-sm) + "Synthetic date." (caption, ink-3) | glyph + line (`--w-strong`) + why | outcome line + diff + clear link |
| Variants | hold (part 3 with items) | offer (st-discuss-bg), ask (st-discuss-bg), hold (st-heldback-bg), aside (dashed `--bw` line-2, transparent), below | overdue (st-heldback-bg, st-heldback text), due (progress word), not due, no date | n/a | n/a |
| States | default; hover on the lane: `--ring-lit`; lit: `--ring-lit` (one ring, no nested ring on children); held: `--rule-hold`; loading: `--sk`; waiting | moved: `v-moved` flash `--dur-flash`; lit: inherits the part ring; no own ring | lit; waiting | hidden when there is no care flag | empty: hidden (`:empty`) |
| Tokens | `--card-*`, `--r-card`, `--pad-card`, `--rule-hold`, `--ring-lit` | `--item-bg`, `--r-item`, `--st-*-bg`, `--sp-2`, `--sp-3` | `--item-bg`, `--r-item`, `--st-heldback-bg` | `--care-bg`, `--care-ink`, `--r-item` | `--accent-soft`, `--r-item` |
| Breakpoints | five across, then 2 per row, then 1; padding is `--pad-card` at every width | at most 300px container: the chart drops under the words | unchanged | unchanged | unchanged |

### 5.6 Skeleton (`C.skeleton`, `.v-sk`)

| | Spec |
|---|---|
| Anatomy | n bars (`opts.sk`, default 3); the first bar 1em tall at 46%, the rest 0.75em at 100%, 82% or 64% |
| States | pulsing (opacity 0.55 at `1.4s`, `--ease`); reduced motion: still; `aria-busy` on the mount |
| Tokens | `--sk` (new alias of `--line`; visible on surface, surface-2 and bg in all four schemes), `--r-small`, `--sp-2` |
| Fix | Mercury bug: `--surface-2` on `--card-bg: var(--surface-2)` is invisible. The `--sk` alias fixes it in every layer. |
| Breakpoints | follows the mount |

### 5.7 Wallet (`C.wallet`, `.v-wallet`)

| | Spec |
|---|---|
| Anatomy | category head (caption, `--w-strong`, ink-3, sentence case); rows: glyph 16, name (body-sm), state word (caption, `--w-strong`, state colour); quiet group behind a "Not raised for this client (n)" link |
| Variants | the five states (held, discuss or ask, progress, held back, not in data); "held" rows grouped per category (`groupHeld`); stacked row when the word is long |
| States | default; lit (from 1 to 5 by row): `--ring-lit`; quiet group collapsed or expanded (`aria-expanded`); moved: flash; empty category: one "No products in this data" row with the not in data glyph |
| Tokens | `--row-line`, `--pad-row`, `--bw`, `--size-glyph`, `--st-*`, `--t-body-sm`, `--t-caption` |
| Breakpoints | inside part 1 at every width |
| Fix | `.v-wrow` stops undoing `[data-from]`'s radius once that rule is removed; `stack` should come from a container query (`@container (max-width: 220px)`), not from `ws.w.length > 10`; `.sw` becomes `.v-word` |

### 5.8 Chips and badges (`.v-badge`, `.v-chip`)

| | Spec |
|---|---|
| Anatomy | inline pill: caption, `--w-strong`, `--pad-badge`, `--r-badge` |
| Variants | segment badge (accent-soft on accent-text) |
| States | static, not interactive |
| Tokens | `--accent-soft`, `--accent-text`, `--t-caption`, `--ls-caption`, `--r-badge`, `--pad-badge` |
| Fix | `C.chips` and `.v-chip` have no CSS and are not mounted: remove them, or style them with this spec if a layout needs them; `gap: 6px` becomes `--sp-1` |

### 5.9 Step status badge (`.v-st`)

| Variant | Colours |
|---|---|
| done | accent-text on accent-soft |
| blocked ("Held back n", "Holds products") | st-heldback on st-heldback-bg |
| nothing found | ink-2 on surface-2 |
| running, waiting | ink-3 on transparent, with `--halo` on the rail |

Tokens: `--t-caption`, `--w-strong`, `--pad-badge`, `--r-badge`. It is not interactive.

### 5.10 Buttons (`.v-btn`, `.v-link`, answer, replay, picker icon)

| | `.v-btn` (Replay, Copy) | Answer (`.v-ans .v-btn`) | `.v-link` | Picker icon |
|---|---|---|---|---|
| Anatomy | optional glyph 14 + label body-sm `--w-ui` `--lh-ui` | label | underlined text, `+` or `−` mark for `aria-expanded` | chevron 12 |
| Size | IBM 12px 16px padding; Mercury 40px high, 0 20px; Linear 8px 14px | `--ctl-h`, `0 calc(--ctl-px / 2)`, **body-sm** (was caption 12; every file sets buttons at 14) | inline | `--ctl-h` square |
| Radius | `--r-control` | `--r-control` | none | `--r-icon` |
| Hover | surface-2 | surface-2 | underline goes to currentColor | surface-2 |
| Focus | global ring | global ring | global ring | global ring |
| Active | translateY(1px), `--dur-fast` | same | none | same |
| Pressed | n/a | **selected option**: accent fill, on-accent text (the toggle look; documented as different from the tab look because it changes the brief) | n/a | n/a |
| Disabled (spec only) | ink-3 on surface, `--line` border, `cursor: default`, `aria-disabled` | same | ink-3, no underline | same |
| Touch | `--touch` minimum height | `--touch` | `--sp-2` vertical padding | `--touch` |

### 5.11 Tabs: bar, ds switch, scheme switch (`.v-segs`, `.v-switch`)

| | Spec |
|---|---|
| Anatomy | optional label (caption, ink-3); group of buttons, `--ctl-h`, `0 calc(--ctl-px / 2)`, caption `--w-ui`; the scheme option adds a swatch |
| Variants | bar (10%, 20%, 30%, 50%); ds (IBM, Mercury, Linear); scheme (S1 to S4) |
| States | off: `--tab-off-bg`, `--tab-off-ink`; hover: off-bg plus **surface-2 in IBM and Linear, accent-soft at full strength in Mercury**, ink (today only the text colour changes); focus: global ring; selected: `--tab-on-bg`, `--tab-on-ink`, `--tab-on-w`, underline `--bw-tab` in `--tab-on-line` |
| Swatch | three 6px stripes. The span carries `data-scheme="S2"` (and so on) and paints `--surface`, `--accent` and `--st-heldback` from the custom properties that resolve on that element. No literal colour, and a swatch can never go stale. |
| Tokens | `--tab-*`, `--r-tab`, `--ctl-h`, `--ctl-px`, `--bw-tab`, `--t-caption` |
| Breakpoints | at most 1399: labels hide; 760 to 1099: the header wraps; at most 760: the picker takes a full row and the switches sit on the next; touch: `--touch` |

### 5.12 Identity, headline, questions, follow up (short)

| Component | Tokens | Change |
|---|---|---|
| Identity | avatar `--size-avatar`, `--r-card`, `--avatar-*`; name `--t-title` at `--w-headline` (was `--t-xl`); group body-sm | the inline glyph style moves to a `.v-g-inline` class |
| Headline | `--t-headline`, `--w-headline`, `--ls-headline`; sub at body, ink-2 | phone: `--t-headline-sm` |
| Questions | question body `--f-sans`; why body-sm; answers 5.10; outcome 5.5 | `.v-out` gap `3px` becomes `--sp-1` |
| Follow up | draft box `--item-bg`, `--bw` line, `--r-item`, body-sm with `--lh-body-sm` (was literal 1.5) | `gap: 6px` becomes `--sp-2` |
| Band chart | bars `--chart-bar` / `--chart-me`, rule `--chart-rule`, text at caption (was 11 and 10px) | check that "low" and "high" still fit; widen the chart by one bar gap if not |

## 6. Migration list

All edits are in docs/brief. Line numbers refer to the files as audited. Run `contrast.py` after each group (it must exit 0), then vfit.py for each ds in S1 at 1440x900, 1280x800 and 390.

### Group A: bugs and rule gaps (do first)

1. tokens.css: add `--sk: var(--line)` to the shared alias block, and change line 474 `.v-sk i { background: var(--surface-2) }` to `var(--sk)`. This fixes the invisible skeleton in Mercury.
2. tokens.css 548 and 549, index.html 90 and 91: replace the three `inset 0 3px 0 var(--st-heldback)` box-shadows and the `border-color` on `.v-stat[data-tone=heldback]` with `box-shadow: var(--rule-hold)`. Define `--rule-hold` in the shared block. Held back emphasis then looks the same in IBM, Mercury and Linear.
3. tokens.css 512: change `[data-from][data-lit="1"]` to a tint only (`background: var(--lit-bg)`) with no ring, so the part ring (`--ring-lit`, index.html 86) is the single ring.
4. tokens.css 541: remove `cursor: pointer` from `.v-stat`. variants.js 216: add `fromTag(n)` inside each card, so the link is focusable.
5. tokens.css 379: Linear `--w-title: 400` becomes `500` (card-title). tokens.css 296: Mercury `--w-title: 360` becomes `480` (heading-2). Check the summary values still fit at 1280.
6. variants.js 34 to 39 and 598: delete the `sw` arrays. Render `<span class="v-swatch" data-scheme="' + s.id + '"><i></i><i></i><i></i></span>` and style `.v-swatch i:nth-child(1..3)` with `var(--surface)`, `var(--accent)` and `var(--st-heldback)`. Note: `[data-scheme="S1"]` is joined with `:root`, so check that the S1 block applies to the span (it does, through the attribute selector).
7. contrast.py 123 to 135: extend `raw_colours()` to scan variants.js, ignoring comments. Add `accent` on `bg` as a `ui` pair for the focus alias. Teach `blocks()` to read the shared alias block and resolve `var()` there, as it already does for ds blocks.

### Group B: colour tidy (values unchanged, so contrast is unchanged)

8. Scheme blocks: delete `--alarm-soft`. Replace its uses (tokens.css 628, 686) with `--st-heldback-bg`.
9. Scheme blocks: delete `--alarm-text`. Replace its uses (tokens.css 567, 628, 663, 687) with `--st-heldback`. Remove contrast.py lines 36 to 38 (they become duplicates of lines 43 and 79).
10. Scheme blocks: rename `--alarm` to `--st-heldback-fill` (uses: 559, 613). Add `--on-heldback: var(--surface)` and use it at 613. Rename contrast.py line 39, "surface on alarm", to "on-heldback on st-heldback-fill".
11. Scheme blocks: rename `--mark` to `--tl-meet` (use: tokens.css 557; contrast.py line 71).
12. Scheme blocks: delete `--focus`, `--chart-me` and `--chart-rule`; define them as aliases in the shared block.
13. Scheme blocks: delete `--st-held-bg`, `--st-progress-bg`, `--st-none-bg` and `--shadow`. Delete contrast.py lines 40, 42, 44, 49, 50 and 51 (they check tokens nothing uses).
14. tokens.css 508: `.v-from[aria-pressed="true"]` becomes `background: var(--lit-bg); border-color: var(--lit-line); color: var(--ink)`. Drop contrast.py line 59; `ink` on `lit-bg` is already checked at line 52.

### Group C: type

15. ds blocks: rename `--t-xs/s/m/l/2xl` (with their `--lh-*` and `--ls-*`) to `--t-caption/body-sm/body/title/headline`. Delete `--t-xl`, `--lh-xl` and `--ls-xl`. Find and replace in tokens.css and index.html.
16. tokens.css 523: `.v-name` moves to `--t-title` at `--w-headline`.
17. tokens.css 677 and 678: `11px` and `10px` become `var(--t-caption)`.
18. Add `--lh-ui` per ds (1.29, 1.2 flagged, 1.2). Replace the literals at 485 (`1.2`) and 621 (`1.25`). Replace 660 (`1.3`) with `--lh-title`, 639 (`1.4`) with `--lh-caption`, and 727 (`1.5`) with `--lh-body-sm`.
19. Add the missing `letter-spacing: var(--ls-caption)` to the 12 caption rules listed in 1.2.
20. ds blocks: collapse `--f-ui`, `--f-head` and `--f-read` into `--f-sans`.
21. ds blocks: rename `--w-head` to `--w-headline`.
22. index.html 120 to 133: add `.v-head { font-size: var(--t-headline-sm); line-height: var(--lh-headline-sm) }` under max 760px, and define `--t-headline-sm` per ds (24, 24, 22).
23. tokens.css 716: answer buttons move from `--t-xs` to `--t-body-sm`.
24. tokens.css 465 and 466: delete the unused `.t-xs` and `.t-s` utilities, or start using them through the role shorthand tokens.

### Group D: space, size, shape, motion

25. Shared block: add `--sp-0: 2px` (flagged "not specified"). Replace the 19 `2px` gaps with `--sp-0`. Snap `3px` to `--sp-1`; `5px` and `6px` to `--sp-1` for glyph to word gaps and `--sp-2` for block gaps (tokens.css 525, 544, 570, 572, 602, 626, 696, 718, 725). Delete `--sp-7`.
26. Shared block: add `--size-marker: 28px`, `--size-tag: 20px`, `--size-avatar: 40px`, `--size-brand: 24px`, `--bw: 1px` and `--bw-rail: 1.5px`. Replace the literals at tokens.css 502, 518, 605, 607, 608, 617 and 650, and at index.html 26, 62, 65, 68 and 73. The rail offsets become `calc(var(--size-marker) / 2 - var(--bw-rail) / 2)` and similar.
27. Rename `--badge-r` to `--r-badge`, `--r-m` to `--r-item`, `--r-l` to `--r-card`, `--r-btn` to `--r-control` and `--tab-r` to `--r-tab`. Keep `--r-s` (renamed `--r-small`) for the skeleton, skip link and brand mark, because in Linear `--r-badge` is a pill and those shapes should not become pills. Add `--r-select` and `--r-icon` for the picker (tokens.css 733 and 738). Delete `--r-pill`. Replace the literal `3px` at 572 with `--r-small`.
28. tokens.css 511: drop `border-radius` from `[data-from]`, and drop `border-radius: 0` from `.v-wrow` (592).
29. ds blocks: delete `--card-shadow`, `--card-hover-bg` and `--card-hover-line`, and Mercury's `--card-line`. Replace `--btn-h: 0px` with an explicit `min-height` in the Mercury block only.
30. Shared block: add `--dur-fast: 120ms`, `--dur-slow: 360ms` and `--dur-flash: 900ms`. Replace 120ms (486), 150ms (index.html 69), 200ms (609), 240ms (index.html 97), 260ms (511) and 900ms (668). In variants.js 684 and 755, read `getComputedStyle(document.documentElement).getPropertyValue("--ease")` and the durations once at boot.
31. Delete `--z-sticky`, or make the header sticky with it.
32. index.html 96 and tokens.css 513: keep one replay fade. Use `[data-ready="0"] { opacity: 0.35 }` and drop the lane level opacity rule, or the reverse, but not both.

### Group E: naming and dead code

33. Rename the classes: `.v-stat .sw` and `.v-wrow .sw` to `.v-word`; `.v-switch .sw` to `.v-swatch`; `.v-stat .lbl` to `.v-stat-label`; `.v-switch .lbl` to `.v-switch-label`; `.v-review .st` to `.v-review-status`; `.v-st` to `.v-step-status`; `.v-from` to `.v-step-tag`; `.v-ilad` to `.v-band-chart`; `.v-sum` to `.v-summary`; `.v-part-h` to `.v-part-head`. Page `.lane` becomes `.spine-col`.
34. Rename the attributes: `data-s` to `data-run`, `data-status` to `data-result` (step only), `data-st` and `data-tone` to `data-state`. Check vinteract.py and vfit.py selectors before renaming.
35. variants.js: delete `C.chips`, `C.meeting` and `C.steps`, plus their DEPS entries, or move them to a clearly marked "unused" section. Keep `C.ranked`, since its label rule is documented. Remove `groupNote` or make index.html's `groupCard` use it.
36. variants.js 157: drop the `st-x` class. Add a `glyph(name, size, label, {inline: true})` option that outputs `class="v-g v-g-inline"`, and delete the string replacements at 180, 415 and 460. Add `.v-g-inline { display: inline; vertical-align: -0.125em; margin-right: var(--sp-1) }`.
37. variants.js 296 and 474: move the inline styles into rules (`.v-tl .lead`, `.v-lane-h .v-bar { margin-left: auto }`).
38. index.html 29 and 30: merge the 1399px and 1366px breakpoints into one at 1399px, and write the breakpoint table (4.5) as a comment at the top of tokens.css.

### Expected result

| Measure | Now | After |
|---|---|---|
| Colour tokens per scheme | 35 + `--shadow` | 28 + 6 shared aliases |
| Raw colours outside scheme blocks | 8 (variants.js, unchecked) | 0, and checked |
| Desktop type sizes | 8 | 5 (plus 1 phone headline size) |
| Line height literals (excluding `/1`) | 5 | 0 |
| Off-scale spacing literals | about 40 | 0 (`--sp-0` covers the 2px stacks) |
| Unused tokens | 9 | 0 |
| Pressed looks | 4 | 3, each documented: toggle (answers), tab (bar, ds, scheme), linked (step button and step tag) |
| Lit looks | 3 | 1 ring plus 1 tint |
| Held back emphasis | differs per ds | one `--rule-hold` |
| contrast.py pairs | 468 | about 430 (dead and duplicate pairs removed), all passing |

None of these changes touch data.json, the five state glyphs or words, the synthetic labels, the raw output label rule or the step to part links.
