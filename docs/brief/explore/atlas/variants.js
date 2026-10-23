/* atlas copy of docs/brief/variants.js. i changed only four things here: the data path (this page sits three folders
   down), the footer links, a few helpers exported for the page, and the questions, which draw as a small decision tree.
   the shared layer for the brief page. it loads ../data.json once through ../field.js, keeps one state
   (client, bar, chosen answer, linked step), and renders components into whatever containers a layout hands it.
   a layout only says where each component goes: V.boot({mounts: {"#wallet": "wallet", ...}}).
   every mount shows a skeleton until the data is in, and says what it depends on, so a change only
   rerenders the mounts it touches: a new client redraws the brief, the bar or an answer only the parts that move.
   no number is typed in here; everything comes from data.json. no raw probability is ever printed, except
   by V.components.ranked, which a layout must label as the raw model output. */
(function(){
"use strict";

var Field = window.Field, esc = Field.esc;
var reduce = !!(window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches);

/* ---------- small words ---------- */
/* motion comes from tokens.css, so the js never keeps its own copy of an easing or a duration */
function motion(name, fallback){
  var v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return fallback == null ? (v || "ease") : (parseFloat(v) || fallback);
}
function pct(x){ return Math.round(x * 100) + "%"; }
function list(a){ return a.length < 2 ? a.join("") : a.slice(0, -1).join(", ") + " and " + a[a.length - 1]; }
function cap(s){ return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
function low1(s){ return s ? s.charAt(0).toLowerCase() + s.slice(1) : s; }
function bandWords(lo, hi){ return lo == null ? "unknown" : pct(lo) + " to " + pct(hi); }
function plural(n, w){ return Field.plural(n, w); }
var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
function iso(d){ return new Date(d + "T00:00:00"); }
function addMonths(d, m){ var x = new Date(d.getTime()); x.setMonth(x.getMonth() + m); return x; }
function monYear(d){ return MONTHS[d.getMonth()] + " " + d.getFullYear(); }
function dayMon(d){ return d.getDate() + " " + MONTHS[d.getMonth()] + " " + d.getFullYear(); }
function tenureWords(m){
  if (m == null) return "not recorded";
  m = Math.round(m); if (m < 1) return "under a month";
  if (m < 24) return plural(m, "month");
  var y = Math.floor(m / 12), r = m % 12; return plural(y, "year") + (r ? " " + plural(r, "month") : "");
}
/* how a money flow reads: asked about, never sold */
var FLOW_ASK = {salary_deposit: "where the salary is paid", pension_deposit: "where the pension is paid", direct_debit: "how the bills are paid"};
/* no colour lives here: each swatch carries its scheme id and tokens.css paints it from that scheme's tokens */
var SCHEMES = [
  {id: "S1", name: "Teal and cherry"},
  {id: "S2", name: "Calm banking light"},
  {id: "S3", name: "Dark slate"},
  {id: "S4", name: "Warm paper"}
];
/* the design system layer: type, space, depth and shape from each DESIGN.md; the colours stay the scheme's */
var DSS = [
  {id: "ibm", name: "IBM Carbon"},
  {id: "mercury", name: "Mercury"},
  {id: "linear", name: "Linear"}
];
/* which agent step produced which part of the brief */
var STEP_OF = {who: 1, help: 2, not: 3, due: 4, qs: 5};
var BARS = [0.1, 0.2, 0.3, 0.5];
/* the question kinds come from data.json; "top suggestion" read like a sales opener, so the page says what it means */
var KIND_WORDS = {"Top suggestion": "Highest after the checks"};

/* ---------- state ---------- */
var S = {F: null, v: null, m: null, thr: 0.1, q: -1, a: -1, open: {}, fu: false, link: 0, replaying: false, stepState: [], cancel: function(){}};
var mounts = [], handlers = {render: [], link: [], step: [], client: [], ready: [], resize: []};
function emit(evt){ var a = [].slice.call(arguments, 1); handlers[evt].forEach(function(fn){ fn.apply(null, a); }); }

/* ---------- the model: every product the agent looked at, and the lane it sits in now (ported from brief.html) ---------- */
function briefOf(view){ return S.F.data.showcase[view.index].brief; }
function bandsOf(product){
  return S.F.data.propensity.calibration.bands.filter(function(b){ return b.product === product; }).sort(function(a, b){ return a.lo - b.lo; });
}
function model(view, st){
  var b = briefOf(view), t = st.thr, items = [], seen = {};
  var ans = st.q >= 0 ? view.questions[st.q].answers[st.a] : null, o = ans ? (ans.outcome || {}) : null;
  /* the raw scores only decide what falls under the bar; no component prints them, except ranked */
  var prob = {}; view.ranked.forEach(function(r){ prob[r.product] = r.probability; });
  var answered = {};
  if (o && o.changes_brief){
    (o.held_back || []).forEach(function(h){ answered[h.label] = {how: "held", reason: h.reason}; });
    view.help.forEach(function(x){ if ((o.suggest || []).indexOf(x.label) < 0 && !answered[x.label]) answered[x.label] = {how: "dropped"}; });
  }
  function add(it){ seen[it.p] = 1; it.prob = prob[it.p]; items.push(it); }
  view.help.forEach(function(x){ add({p: x.product, label: x.label, kind: x.kind === "flow" ? "flow" : "offer", x: x, lo: x.bandLo, hi: x.bandHi}); });
  view.blocked.forEach(function(x){ var bb = (b.not_to_offer.find(function(n){ return n.product === x.product; }) || {}).band || {}; add({p: x.product, label: x.label, kind: "blocked", x: x, lo: bb.lo, hi: bb.hi}); });
  view.inProgress.forEach(function(x){ var bb = (b.in_progress.find(function(n){ return n.product === x.product; }) || {}).band || {}; add({p: x.product, label: x.label, kind: "prog", x: x, lo: bb.lo, hi: bb.hi}); });
  var also = {};
  b.might_help.forEach(function(m){ if (m.also_product) also[m.also_product] = m.product; });
  view.ranked.forEach(function(r){
    if (seen[r.product]) return;
    if (also[r.product]){ seen[r.product] = 1; items.push({p: r.product, label: r.label, kind: "also", with: also[r.product], prob: r.probability}); return; }
    var bd = bandsOf(r.product).find(function(x){ return r.probability >= x.lo && (r.probability < x.hi || x.hi >= 1); }) || {};
    add({p: r.product, label: r.label, kind: r.probability < b.threshold ? "low" : view.nextStep ? "wait" : "other", lo: bd.lo, hi: bd.hi});
  });
  items.forEach(function(it){
    var k = it.kind;
    it.lane = k === "offer" ? "offer" : k === "flow" ? "ask" : k === "blocked" || k === "wait" ? "hold" : k === "low" ? "below" : k === "also" ? "also" : "aside";
    /* a rule holds whatever the bar; only what could be raised can fall under it */
    if ((k === "offer" || k === "flow" || k === "prog" || k === "other") && it.prob != null && it.prob < t - 1e-9){ it.fell = true; it.lane = "aside"; }
    if (!it.fell && (it.lane === "offer" || it.lane === "ask") && answered[it.label]){
      it.ans = answered[it.label]; it.lane = it.ans.how === "held" ? "hold" : "aside";
    }
  });
  items.forEach(function(it){ if (it.kind === "also"){ var w = items.find(function(x){ return x.p === it.with; }); it.fell = !!(w && w.fell); it.ans = w && w.ans; } });
  return {items: items, t: t, ans: ans, view: view};
}
function lane(m, l){ return m.items.filter(function(it){ return it.lane === l; }); }
function itemOf(m, p){ return m.items.find(function(x){ return x.p === p; }); }

/* the headline names what is worth discussing; it never reads as an order */
function headline(m){
  var view = m.view, offers = lane(m, "offer"), asks = lane(m, "ask"), hold = lane(m, "hold"), aside = lane(m, "aside");
  var rule = hold.filter(function(it){ return it.kind === "blocked"; }), byAns = hold.concat(aside).filter(function(it){ return it.ans; });
  var prog = aside.filter(function(it){ return it.kind === "prog" && !it.fell; });
  var h = {lead: "", main: "", sub: "", kicker: view.care && (offers.length || asks.length) ? "If the care check is fine" : ""};
  if (offers.length){
    h.lead = "Worth discussing: "; h.main = list(offers.map(function(it){ return low1(it.label); }));
    if (asks.length) h.sub = "Worth asking about " + list(asks.map(function(it){ return FLOW_ASK[it.p] || "the " + low1(it.label); })) + ".";
  } else if (asks.length){
    h.lead = "Worth asking about: "; h.main = list(asks.map(function(it){ return FLOW_ASK[it.p] || "the " + low1(it.label); }));
  } else if (view.nextStep){
    h.lead = "Worth discussing: "; h.main = "the overdue periodic review"; h.sub = "New products wait until the review is complete.";
  } else if (byAns.length){ h.main = "Nothing new worth discussing after that answer";
  } else if (rule.length){ h.main = "Nothing worth discussing after the checks"; h.sub = "Held back: " + list(rule.map(function(it){ return low1(it.label); })) + ".";
  } else if (prog.length){ h.main = "Nothing new worth discussing"; h.sub = cap(list(prog.map(function(it){ return "the " + low1(it.label); }))) + (prog.length > 1 ? " are" : " is") + " likely already in progress.";
  } else if (aside.some(function(it){ return it.fell; })){ h.main = "Nothing worth discussing above the " + pct(m.t) + " bar";
  } else h.main = "Nothing worth discussing at this meeting";
  if (offers.length && rule.length) h.sub = (h.sub ? h.sub + " " : "") + "Held back: " + list(rule.map(function(it){ return low1(it.label); })) + ".";
  h.text = h.lead + h.main;
  return h;
}

/* where a product in the wallet stands now, after the bar and any chosen answer */
/* "has it" is the word for a product the client owns, so it never reads like "held back". data.json still says "Held";
   i map it here and leave the data alone */
var STATE_WORDS = {held: "Has it", discuss: "Worth discussing", ask: "Worth asking about", progress: "Likely in progress", heldback: "Held back", none: "Not in data"};
function dataWord(w){ return w === "Held" ? STATE_WORDS.held : w; }
function walletState(p){
  if (!p.product) return {s: "none", w: STATE_WORDS.none, from: 1};
  var it = itemOf(S.m, p.product);
  if (p.state === "held") return {s: "held", w: STATE_WORDS.held, from: 1};
  if (!it){
    if (p.state === "not_in_data") return {s: "none", w: STATE_WORDS.none, from: 1};
    return {s: "quiet", w: dataWord(p.state_words), from: 2};
  }
  if (it.lane === "offer") return {s: "discuss", w: STATE_WORDS.discuss, from: 2};
  if (it.lane === "ask") return {s: "discuss", w: STATE_WORDS.ask, from: 2};
  if (it.lane === "hold") return {s: "heldback", w: it.ans ? "Held back by the answer" : it.kind === "wait" ? "Waits for the review" : STATE_WORDS.heldback, from: it.ans ? 5 : it.kind === "wait" ? 4 : 3};
  if (it.lane === "also"){ var w = itemOf(S.m, it.with) || {}, live = !it.fell && !it.ans && (w.lane === "ask" || w.lane === "offer");
    return {s: live ? "discuss" : "quiet", w: live ? (w.lane === "ask" ? STATE_WORDS.ask : STATE_WORDS.discuss) : "Not raised", t: "Counted with " + w.label, from: 2}; }
  if (it.kind === "prog" && !it.fell) return {s: "progress", w: STATE_WORDS.progress, from: 3};
  if (it.fell) return {s: "quiet", w: "Under the " + pct(S.m.t) + " bar", from: 2};
  if (it.ans) return {s: "quiet", w: "Not raised after the answer", from: 5};
  if (it.lane === "below") return {s: "quiet", w: dataWord(p.state_words), from: 2};
  return {s: "quiet", w: dataWord(p.state_words), from: 2};
}

/* ---------- glyphs: one simple shape per state, drawn here, never from an icon pack ---------- */
var G = {
  held: '<circle cx="8" cy="8" r="7" fill="currentColor"/><path d="M4.8 8.2l2.2 2.2 4.2-4.6" fill="none" stroke="var(--surface)" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>',
  discuss: '<path d="M2.5 3.5h11a1 1 0 0 1 1 1v6a1 1 0 0 1-1 1H7.2L4.4 14v-2.5H2.5a1 1 0 0 1-1-1v-6a1 1 0 0 1 1-1z" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round"/><path d="M4.8 6.6h6.4M4.8 8.9h4" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>',
  progress: '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M8 1.8a6.2 6.2 0 0 1 0 12.4z" fill="currentColor"/>',
  heldback: '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.6"/><path d="M4.6 8h6.8" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>',
  none: '<circle cx="8" cy="8" r="6.2" fill="none" stroke="currentColor" stroke-width="1.4" stroke-dasharray="2.2 2"/>',
  quiet: '<circle cx="8" cy="8" r="2.6" fill="none" stroke="currentColor" stroke-width="1.3"/>',
  info: '<circle cx="8" cy="8" r="6.4" fill="none" stroke="currentColor" stroke-width="1.4"/><path d="M8 7.2v4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><circle cx="8" cy="4.9" r="1" fill="currentColor"/>',
  group: '<circle cx="5.6" cy="6" r="2.3" fill="none" stroke="currentColor" stroke-width="1.4"/><circle cx="11" cy="6.6" r="1.9" fill="none" stroke="currentColor" stroke-width="1.3"/><path d="M1.8 13.2c.5-2.3 2-3.5 3.8-3.5s3.3 1.2 3.8 3.5M9.8 10.1c1.9-.2 3.6.8 4.2 3.1" fill="none" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>',
  care: '<path d="M8 13.6S2.2 10.2 2.2 6.2A2.9 2.9 0 0 1 8 4.9a2.9 2.9 0 0 1 5.8 1.3c0 4-5.8 7.4-5.8 7.4z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/>',
  replay: '<path d="M3 8a5 5 0 1 0 1.6-3.7" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"/><path d="M4.4 1.8v2.8h2.8" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
};
function glyph(name, size, label){
  size = size || 16;
  return '<svg class="v-g st-' + (G[name] && name !== "info" && name !== "group" && name !== "care" && name !== "replay" ? name : "x") + '" width="' + size + '" height="' + size + '" viewBox="0 0 16 16"' +
    (label ? ' role="img" aria-label="' + esc(label) + '"' : ' aria-hidden="true"') + '>' + G[name] + '</svg>';
}
/* the reverse link: a small numbered marker on every part, which selects the step that made it */
function fromTag(n){
  var sp = S.F.stepSpecs[n - 1] || {};
  return '<button type="button" class="v-from" data-act="link" data-step="' + n + '" aria-pressed="' + (S.link === n) + '" aria-label="Made by step ' + n + ', ' + esc(sp.name || "") + '. Show the step" title="Made by step ' + n + ', ' + esc(sp.name || "") + '">' + n + '</button>';
}
function fromAttr(n, extra){ return ' data-from="' + n + '"' + (S.replaying && !stepDone(n) ? ' data-ready="0"' : '') + (extra || ""); }
function stepDone(n){ return !S.replaying || S.stepState[n - 1] === "done"; }

/* ---------- components. each takes (el, ctx, opts) and fills el ---------- */
var C = {};

C.identity = function(el, ctx, opts){
  opts = opts || {};
  var v = ctx.v, p = briefOf(v).who.profile || {}, num = v.ref.replace(/\D/g, "");
  var seg = p.segment ? cap(p.segment) : "Segment not recorded";
  el.innerHTML = '<div class="v-id"' + fromAttr(1) + '><span class="v-avatar" aria-hidden="true">C' + esc(num) + '</span><div class="v-id-t">' +
    '<div class="v-name-row"><h1 class="v-name">' + esc(v.ref) + '</h1><span class="v-badge" title="Bank segment recorded in the data">' + esc(seg) + '</span></div>' +
    '<p class="v-group">' + glyph("group", 13) + ' In the group <b>' + esc(v.who.name) + '</b></p>' +
    /* opts.mismatch "inline": the mismatch sits right under the group it qualifies */
    (opts.mismatch === "inline" && briefOf(v).who.mismatch ? '<p class="v-mismatch">' + glyph("info", 14) + '<span>' + esc(briefOf(v).who.mismatch) + '</span></p>' : '') + '</div></div>';
  var g = el.querySelector(".v-group svg"); if (g){ g.style.display = "inline"; g.style.verticalAlign = "-2px"; }
};
C.mismatch = function(el, ctx){
  var mm = briefOf(ctx.v).who.mismatch;
  el.innerHTML = mm ? '<p class="v-mismatch"' + fromAttr(1) + '>' + glyph("info", 14) + '<span>' + esc(mm) + '</span></p>' : '';
  el.hidden = !mm;
};
C.groupNote = function(el, ctx){
  el.innerHTML = '<p class="v-meta"' + fromAttr(1) + '>' + esc(cap(ctx.v.who.description)) + '.</p>';
};
C.chips = function(el, ctx, opts){
  var v = ctx.v, p = briefOf(v).who.profile || {}, d = v.due, chips = [];
  function chip(k, val, tone, from, title){ chips.push('<li class="v-chip"' + (tone ? ' data-tone="' + tone + '"' : '') + fromAttr(from) + (title ? ' title="' + esc(title) + '"' : '') + '><span class="k">' + esc(k) + '</span><span class="val">' + esc(val) + '</span></li>'); }
  chip("Age", p.age == null ? "not recorded" : String(Math.round(p.age)), "", 1);
  chip("Tenure", tenureWords(p.tenure_months), "", 1);
  chip("Income recorded", p.income == null ? "No" : "Yes", "", 1);
  if (opts && opts.products) chip("Products", String(p.n_products != null ? p.n_products : (p.held || []).length), "", 1);
  var rv = d.state === "overdue" ? "Overdue" : d.state === "due" ? "Due in " + plural(d.days, "day") : d.state === "not_due" ? "Not due" : "No date";
  chip("Review", rv, d.state === "overdue" ? "alarm" : d.state === "due" ? "due" : "", 4, "Synthetic review date. " + (d.sub || ""));
  if (v.care) chip("Care", "Check first", "care", 3, v.care.signals.join(" "));
  el.innerHTML = '<ul class="v-chips" aria-label="Key facts">' + chips.join("") + '</ul>';
};
/* the quiet facts under the name: age, income, the meeting date, and the care check when there is one */
C.facts = function(el, ctx){
  var v = ctx.v, p = briefOf(v).who.profile || {};
  el.innerHTML = '<p class="v-facts" aria-label="Key facts"><span' + fromAttr(1) + '>Age<b>' + esc(p.age == null ? "not recorded" : String(Math.round(p.age))) + '</b></span>' +
    '<span' + fromAttr(1) + '>Income recorded<b>' + (p.income == null ? "No" : "Yes") + '</b></span>' +
    '<span>Meeting<b>' + esc(v.meeting) + '</b></span>' +
    (v.care ? '<span class="care"' + fromAttr(3) + ' title="' + esc(v.care.signals.join(" ")) + '">Care<b>Check first</b></span>' : '') + '</p>';
};
/* the summary strip: what changed, tenure, review and held back. the segment is already the badge next to the name,
   so it is not repeated here. each card has a value, a label, a status word with its glyph, coloured only by the state
   tokens, and the tag of the step that produced it, which is the keyboard route to that step */
var CHANGE_SHORT = {flag_new_products: "Took up products", flag_dropped_products: "Closed products", flag_activity_drop: "Became inactive",
  flag_moved: "Moved province", flag_new_client: "New client", flag_segment_change: "Segment changed"};
C.summary = function(el, ctx){
  var v = ctx.v, b = briefOf(v), p = b.who.profile || {}, d = v.due, flags = b.who.change_flags, cards = [];
  var hold = lane(ctx.m, "hold");
  function card(n, key, val, lbl, st, word, tone){
    cards.push('<li class="v-stat" data-key="' + key + '"' + fromAttr(n) + (tone ? ' data-tone="' + tone + '"' : '') + '><span class="lbl">' + esc(lbl) + '</span>' + fromTag(n) +
      '<span class="val">' + esc(val) + '</span><span class="sw st-' + st + '">' + glyph(st === "info" ? "info" : st, 14) + '<span>' + esc(word) + '</span></span></li>');
  }
  var ch = flags.map(function(f, k){ return {short: CHANGE_SHORT[f], sentence: b.who.changes[k]}; }).filter(function(c){ return c.short; });
  /* the first change is the value; any others are counted in the status line and drawn on the timeline */
  card(1, "changed", ch.length ? ch[0].short : "Nothing recorded", "What changed", ch.length ? "info" : "quiet",
    ch.length ? ch[0].sentence.replace(/\.$/, "") + (ch.length > 1 ? ", and " + (ch.length - 1) + " more on the timeline" : "") + "." : "No changes in the last six months");
  var meet = iso(b.meeting_date), joined = p.tenure_months != null ? addMonths(meet, -Math.round(p.tenure_months)) : null;
  card(1, "tenure", tenureWords(p.tenure_months), "Tenure", "quiet", joined ? "Joined " + monYear(joined) : "Start date not recorded");
  var rv = b.due_anyway.next_review ? dayMon(iso(b.due_anyway.next_review)) : "No date on file";
  var rs = d.state === "overdue" ? ["heldback", "Overdue by " + plural(-d.days, "day")] : d.state === "due" ? ["progress", "Due in " + plural(d.days, "day")] : d.state === "not_due" ? ["quiet", "Not due"] : ["none", "No review date"];
  card(4, "review", rv, "Periodic review, synthetic date", rs[0], rs[1]);
  var nChecked = v.toolLog.filter(function(e){ return e.tool === "check_suitability"; }).length;
  card(3, "held", hold.length ? list(hold.map(function(it){ return it.label; })) : "Nothing", "Held back", hold.length ? "heldback" : "quiet",
    hold.length ? (hold.length === 1 ? "The reason is in part 3" : "The reasons are in part 3") : nChecked ? plural(nChecked, "product") + " checked against the rules" : "Nothing to check", hold.length ? "heldback" : "");
  el.innerHTML = '<ul class="v-sum" aria-label="Client summary">' + cards.join("") + '</ul>';
};
/* one quiet line under the header that says what the page is. the data source comes from data.json */
C.context = function(el){
  var src = (S.F.data.meta || {}).source;
  el.innerHTML = '<p>Prototype for a job application' + (src ? ', built on the ' + esc(src) : '') + '. Review dates and vulnerability flags are synthetic. The agent prepares the brief; the advisor decides.</p>';
};
C.meeting = function(el, ctx){ el.innerHTML = '<p class="v-meeting">Meeting on <b>' + esc(ctx.v.meeting) + '</b></p>'; };

/* the relationship timeline. the data gives windows, not dates, for changes, so those are drawn as spans over the window */
C.timeline = function(el, ctx, opts){
  opts = opts || {};
  var v = ctx.v, b = briefOf(v), p = b.who.profile || {}, W = Math.max(240, Math.round(opts.width || el.clientWidth || 520));
  var meet = iso(b.meeting_date), m6 = addMonths(meet, -6), m3 = addMonths(meet, -3);
  var joined = p.tenure_months != null ? addMonths(meet, -Math.round(p.tenure_months)) : null;
  var rv = b.due_anyway.next_review ? iso(b.due_anyway.next_review) : null, overdue = v.due.state === "overdue";
  var end = rv && rv > meet ? rv : addMonths(meet, 3);
  /* piecewise scale: long history squeezed on the left, the last six months in detail, the future squeezed on the right */
  var L = 6, R = W - 6, early = joined && joined < m6, far = end > addMonths(meet, 6);
  var knots = early ? [[joined, L], [m6, L + (R - L) * 0.24], [meet, L + (R - L) * 0.68], [end, R]] : [[m6, L], [meet, L + (R - L) * 0.62], [end, R]];
  function X(d){
    for (var k = 1; k < knots.length; k++){ var a = knots[k - 1], c = knots[k];
      if (d <= c[0] || k === knots.length - 1){ var f = (d - a[0]) / Math.max(1, c[0] - a[0]); return a[1] + Math.max(0, Math.min(1, f)) * (c[1] - a[1]); } }
    return R;
  }
  var flags0 = b.who.change_flags.filter(function(f){ return /new_products|dropped_products|activity_drop|segment_change|moved/.test(f); }).length;
  var y = 8 + flags0 * 7 + 4, out = [], labs = [];
  out.push('<line class="axis" x1="' + L + '" x2="' + R + '" y1="' + y + '" y2="' + y + '"/>');
  /* a break mark where the scale changes, so a squeezed stretch never looks like real distance */
  function brk(x){ out.push('<line class="brk" x1="' + (x - 3) + '" x2="' + (x + 3) + '" y1="' + y + '" y2="' + y + '"/><line class="brk-l" x1="' + (x - 4) + '" x2="' + (x - 1) + '" y1="' + (y + 4) + '" y2="' + (y - 4) + '"/><line class="brk-l" x1="' + (x + 1) + '" x2="' + (x + 4) + '" y1="' + (y + 4) + '" y2="' + (y - 4) + '"/>'); }
  if (early) brk((knots[0][1] + knots[1][1]) / 2);
  if (far) brk((X(meet) + R) / 2);
  /* spans above the line, one lane each */
  var spans = [], flags = b.who.change_flags;
  if (flags.indexOf("flag_new_products") >= 0) spans.push({c: "add", a: m3, t: "Took up products, last 3 months", from: 1});
  if (flags.indexOf("flag_dropped_products") >= 0) spans.push({c: "drop", a: m3, t: "Closed products, last 3 months", from: 1});
  if (flags.indexOf("flag_activity_drop") >= 0) spans.push({c: "act", a: m3, t: "Became inactive, last 3 months", from: 1});
  if (flags.indexOf("flag_segment_change") >= 0) spans.push({c: "seg", a: m6, t: "Segment changed, last 6 months", from: 1});
  if (flags.indexOf("flag_moved") >= 0) spans.push({c: "seg", a: m6, t: "Moved province, last 6 months", from: 1});
  var sentence = {}; b.who.change_flags.forEach(function(f, k){ sentence[f] = b.who.changes[k]; });
  /* a window never starts before the client joined */
  spans.forEach(function(s){ s.x1 = X(joined && joined > s.a ? joined : s.a); s.x2 = X(meet); });
  /* spans stack upwards from the line; each gets a label at its left end */
  var top = 0;
  spans.forEach(function(s, k){
    var yy = y - 10 - k * 7;
    out.push('<g' + fromAttr(1) + '><title>' + esc(s.t) + '</title><line class="span ' + s.c + '" x1="' + (s.x1 + 3) + '" x2="' + (s.x2 - 3) + '" y1="' + yy + '" y2="' + yy + '"/></g>');
    top = Math.min(top, yy - 6);
  });
  /* point events below the line */
  function pt(x, cls, lab, sub, from, anchor){ labs.push({x: x, cls: cls, lab: lab, sub: sub, from: from}); }
  if (joined) pt(X(joined), "", "Joined", monYear(joined), 1);
  pt(X(meet), "meet", "Meeting", dayMon(meet), 0);
  if (rv) pt(X(rv), "rev" + (overdue ? " overdue" : ""), overdue ? "Review overdue" : "Next review", dayMon(rv) + ", synthetic", 4);
  /* labels: place left to right, drop to a second row when two would touch */
  labs.sort(function(a, c){ return a.x - c.x; });
  var rows = [[], []], LW = function(l){ return Math.max(l.lab.length, l.sub.length) * 6.9 + 8; };
  function setA(l, anchor){ var w = LW(l); l.anchor = anchor; l.a0 = anchor === "start" ? l.x - 4 : anchor === "end" ? l.x - w + 4 : l.x - w / 2; l.a1 = l.a0 + w; }
  function hit(l, set){ return set.some(function(o){ return o !== l && !(l.a1 < o.a0 || l.a0 > o.a1); }); }
  labs.forEach(function(l, i){
    var w = LW(l); setA(l, l.x - w / 2 < 0 ? "start" : l.x + w / 2 > W ? "end" : "middle"); l.row = 0;
    var prev = rows[0][rows[0].length - 1];
    /* two labels that touch first turn away from each other; only if that fails does the right one drop a row */
    if (prev && hit(l, rows[0])){
      var pa = prev.anchor; setA(prev, prev.x - LW(prev) < 0 ? pa : "end"); setA(l, l.x + w > W ? l.anchor : "start");
      if (hit(prev, rows[0]) || hit(l, rows[0]) || prev.a0 < 0){ setA(prev, pa); setA(l, l.x - w / 2 < 0 ? "start" : l.x + w / 2 > W ? "end" : "middle"); l.row = 1; }
    }
    rows[l.row].push(l);
  });
  labs.forEach(function(l){
    var ly = y + 22 + l.row * 28, tx = l.anchor === "start" ? Math.max(0, l.x - 4) : l.anchor === "end" ? Math.min(W, l.x + 4) : l.x;
    var g = '<g' + (l.from ? fromAttr(l.from) : '') + '>';
    if (l.row) g += '<line class="axis" x1="' + l.x + '" x2="' + l.x + '" y1="' + (y + 6) + '" y2="' + (ly - 11) + '" style="stroke-width:1"/>';
    g += '<circle class="dot ' + l.cls + '" cx="' + l.x + '" cy="' + y + '" r="' + (l.cls === "meet" ? 5.5 : 4.5) + '"/>' +
      '<text class="lab' + (l.cls.indexOf("overdue") >= 0 ? " alarm" : "") + '" x="' + tx + '" y="' + ly + '" text-anchor="' + l.anchor + '"><tspan class="s">' + esc(l.lab) + '</tspan></text>' +
      '<text class="lab q" x="' + tx + '" y="' + (ly + 13) + '" text-anchor="' + l.anchor + '">' + esc(l.sub) + '</text></g>';
    out.push(g);
  });
  var maxRow = Math.max.apply(null, labs.map(function(l){ return l.row; }).concat([0]));
  var H = y + 22 + maxRow * 28 + 17, T = 0;
  /* the span key sits under the svg as text, so it wraps instead of colliding */
  var ttl = opts.title ? '<li class="ttl">' + esc(opts.title) + '</li>' : '';
  var key = spans.length ? '<ul class="v-tl-key">' + ttl + spans.map(function(s){ return '<li' + fromAttr(1) + ' title="' + esc(sentence[{add: "flag_new_products", drop: "flag_dropped_products", act: "flag_activity_drop"}[s.c]] || s.t) + '"><i class="' + s.c + '"></i>' + esc(s.t) + '</li>'; }).join("") + '</ul>' : '<ul class="v-tl-key">' + ttl + '<li class="none">No recorded changes in the last six months.</li></ul>';
  el.innerHTML = '<svg class="v-tl" width="' + W + '" height="' + (H - T) + '" viewBox="0 ' + T + ' ' + W + ' ' + (H - T) + '" role="img" aria-label="Relationship timeline. ' +
    esc(labs.map(function(l){ return l.lab + " " + l.sub; }).join(". ") + ". " + spans.map(function(s){ return s.t; }).join(". ")) + '">' + out.join("") + '</svg>' + key;
};

/* the wallet: every product by category; the five states carry a glyph, a colour and a word, the quiet ones are one muted line */
C.wallet = function(el, ctx, opts){
  opts = opts || {};
  if (opts.split) return walletSplit(el, ctx, opts);
  /* quiet: "inline" lists the quiet products under their own category; "bottom" gathers them by state under the wallet */
  var v = ctx.v, bottom = opts.quiet === "bottom", allQuiet = {};
  function quietHTML(q){ return Object.keys(q).map(function(w){ return '<p class="v-wquiet"' + fromAttr(2) + '><b>' + esc(w) + ':</b> ' + esc(q[w].join(", ")) + '</p>'; }).join(""); }
  var html = v.holdings.map(function(c){
    var rows = [], quiet = {};
    if (!c.products.length) rows.push(row({product: null, label: "No products in this data"}, {s: "none", w: STATE_WORDS.none, from: 1}));
    var held = [];
    c.products.forEach(function(p){
      var ws = walletState(p);
      if (ws.s === "quiet"){ var bag = bottom ? allQuiet : quiet; (bag[ws.w] = bag[ws.w] || []).push(p.label); return; }
      /* opts.groupHeld: products the client holds share one row per category, so a full wallet still fits */
      if (opts.groupHeld && ws.s === "held"){ held.push(p); return; }
      rows.push(row(p, ws));
    });
    if (held.length) rows.unshift(held.length === 1 ? row(held[0], {s: "held", w: STATE_WORDS.held, from: 1}) :
      '<div class="v-wrow" data-st="held"' + fromAttr(1) + '>' + glyph("held", 16) + '<span class="nm">' + esc(held.map(function(p){ return p.label; }).join(", ")) + '</span><span class="sw st-held">' + STATE_WORDS.held + '</span></div>');
    if (bottom && !rows.length) return "";
    return '<div class="v-wcat"><p class="v-wcat-h">' + esc(c.category) + '</p>' + rows.join("") + (bottom ? "" : quietHTML(quiet)) + '</div>';
  }).join("");
  if (bottom && Object.keys(allQuiet).length) html += '<div class="v-wcat v-wcat-quiet"><p class="v-wcat-h">' + esc(opts.quietTitle || "Not raised for this client") + '</p>' + quietHTML(allQuiet) + '</div>';
  function row(p, ws){
    return '<div class="v-wrow' + (ws.w.length > 10 ? ' stack' : '') + '" data-st="' + ws.s + '"' + (p.product ? ' data-item="w-' + esc(p.product) + '" data-p="' + esc(p.product) + '"' : '') + fromAttr(ws.from) + (ws.t ? ' title="' + esc(ws.t) + '"' : '') + '>' +
      glyph(ws.s, 16) + '<span class="nm">' + esc(p.label) + '</span><span class="sw st-' + ws.s + '">' + esc(ws.w) + '</span></div>';
  }
  el.innerHTML = '<div class="v-wallet">' + html + '</div>';
};
/* the split wallet: what the client has sits in one quiet group, what the brief raised or held back sits apart as rows,
   so "has it" and "held back" never share a column. empty categories fold into one "not in data" line */
function walletCounts(v){
  var c = {held: 0, discuss: 0, progress: 0, heldback: 0};
  v.holdings.forEach(function(cat){ cat.products.forEach(function(p){ var ws = walletState(p); if (ws.s in c) c[ws.s]++; }); });
  return c;
}
function walletSplit(el, ctx, opts){
  var v = ctx.v, has = [], rows = [], none = [], quiet = {}, nHas = 0;
  v.holdings.forEach(function(c){
    if (!c.products.length){ none.push(c.category); return; }
    var mine = [];
    c.products.forEach(function(p){
      var ws = walletState(p);
      if (ws.s === "quiet"){ (quiet[ws.w] = quiet[ws.w] || []).push(p.label); return; }
      if (ws.s === "held"){ mine.push(p); return; }
      if (ws.s === "none"){ none.push(p.product ? p.label : c.category); return; }
      rows.push('<li class="v-wrow" data-st="' + ws.s + '" data-item="w-' + esc(p.product) + '" data-p="' + esc(p.product) + '"' + fromAttr(ws.from) + (ws.t ? ' title="' + esc(ws.t) + '"' : '') + '>' +
        glyph(ws.s, 16) + '<span class="nm">' + esc(p.label) + '<span class="cat">' + esc(c.category) + '</span></span><span class="sw st-' + ws.s + '">' + esc(ws.w) + '</span></li>');
    });
    if (mine.length){ nHas += mine.length; has.push('<li><span class="cat">' + esc(c.category) + '</span> ' + mine.map(function(p){ return '<span data-item="w-' + esc(p.product) + '" data-st="held">' + esc(p.label) + '</span>'; }).join(", ") + '</li>'); }
  });
  var html = '<div class="v-wsplit">' +
    '<section class="v-wgrp v-whas" aria-label="' + esc(STATE_WORDS.held) + '"' + fromAttr(1) + '><h4 class="v-wgrp-h">' + glyph("held", 16) + '<span class="st-held">' + esc(STATE_WORDS.held) + '</span> <span class="v-count">' + nHas + '</span></h4>' +
      (has.length ? '<ul class="v-whas-l">' + has.join("") + '</ul>' : '<p class="v-none">No products with this bank in this data.</p>') + '</section>' +
    (rows.length ? '<section class="v-wgrp" aria-label="In this brief"><h4 class="v-wgrp-h">In this brief</h4><ul class="v-wrows">' + rows.join("") + '</ul></section>' : '') +
    '</div>' +
    (none.length ? '<p class="v-wnone"' + fromAttr(1) + '>' + glyph("none", 14) + '<span><b>' + esc(STATE_WORDS.none) + ':</b> ' + esc(list(none)) + '</span></p>' : '');
  if (Object.keys(quiet).length) html += '<div class="v-wcat v-wcat-quiet"><p class="v-wcat-h">' + esc(opts.quietTitle || "Not raised for this client") + '</p>' +
    Object.keys(quiet).map(function(w){ return '<p class="v-wquiet"' + fromAttr(2) + '><b>' + esc(w) + ':</b> ' + esc(quiet[w].join(", ")) + '</p>'; }).join("") + '</div>';
  el.innerHTML = '<div class="v-wallet v-wallet-split">' + html + '</div>';
}
C.legend = function(el){
  el.innerHTML = '<p class="v-legend" aria-label="Product states">' + ["held", "discuss", "progress", "heldback", "none"].map(function(s){
    return '<span>' + glyph(s, 14) + esc(STATE_WORDS[s]) + '</span>'; }).join("") + '</p>';
};

/* ---------- agent steps ---------- */
function stepStatus(v, k){
  var b = briefOf(v), s = v.steps[k];
  if (k === 1) return v.help.length || v.blocked.length || v.inProgress.length || v.ranked.some(function(r){ return r.probability >= b.threshold; }) ? "done" : "none";
  if (k === 2){
    var held = s.calls.filter(function(e){ return / blocked by /.test(e.summary); }).length;
    if (held) return "blocked";
    return s.calls.filter(function(e){ return e.tool === "check_suitability"; }).length || (v.care) ? "done" : "none";
  }
  if (k === 3) return v.due.state === "overdue" && (v.waiting || v.nextStep) ? "blocked" : v.due.state === "none" ? "none" : "done";
  if (k === 4) return v.questions.length ? "done" : "none";
  return "done";
}
function statusWords(v, k, st){
  if (st === "blocked") return k === 2 ? "Held back " + v.steps[2].calls.filter(function(e){ return / blocked by /.test(e.summary); }).length : "Holds back products";
  if (st === "none") return "Nothing found";
  return "Done";
}
/* what a step returned, in plain words. step 2 gives the count only: naming the highest scored product here
   would put a product, maybe a held back one, above the brief as if it were the pick */
function retWords(v, k){
  if (k === 1){ var m = /^\d+ products? scored/.exec(v.steps[1].result || ""); return m ? m[0] : plural(v.ranked.length, "product") + " scored"; }
  return cap(Field.clean(v.steps[k].result)) || "Nothing";
}
/* what the step read for this client, in plain words: the specs list the inputs, the calls say what came back */
function readWords(s){ return s.reads; }
function stepHTML(v, k, opts){
  var s = v.steps[k], n = k + 1, st = S.replaying ? (S.stepState[k] || "wait") : "done", status = stepStatus(v, k);
  var stw = st === "done" ? statusWords(v, k, status) : st === "run" ? "Running" : "Waiting";
  var reads = readWords(s), budget = opts.readChars || 30, shown = [], open = !!S.open["step" + k];
  /* opts.ret: the steps that keep their returned line. a step whose part sits right under it and says the same words drops it */
  var ret = !opts.ret || opts.ret.indexOf(n) >= 0;
  /* the read line shows what fits in about one line; the rest sits behind "and n more" */
  for (var r = 0; r < reads.length; r++){ if (shown.length && shown.concat([reads[r]]).join(", ").length > budget) break; shown.push(reads[r]); }
  var tools = s.calls.map(function(e){ return '<li><span class="v-tool">' + esc(e.tool) + '</span> ' + esc(Field.clean(e.summary)) + '</li>'; }).join("");
  var Tag = opts.tag || "li";
  return '<' + Tag + ' class="v-step" id="v-step-' + n + '" data-step-n="' + n + '" data-s="' + st + '" data-status="' + status + '">' +
    '<span class="v-step-n" aria-hidden="true">' + n + '</span><div class="v-step-body">' +
    '<div class="v-step-top"><button type="button" class="v-step-btn" data-act="link" data-step="' + n + '" aria-pressed="' + (S.link === n) + '" aria-label="Step ' + n + ', ' + esc(s.name) + '. Show what this step produced" title="Show what this step produced">' +
      '<span>' + esc(s.name) + '</span></button>' +
      '<span class="v-st" data-status="' + (st === "done" ? status : st) + '">' + esc(stw) + '</span></div>' +
    '<dl class="v-step-io"><dt>Read</dt><dd>' + esc(cap(shown.join(", "))) + (reads.length > shown.length ? ' <button type="button" class="v-link" data-act="toggle" data-key="step' + k + '" aria-expanded="' + open + '" aria-controls="v-sm-' + n + '">and ' + (reads.length - shown.length) + ' more</button>' : '') + '</dd>' +
    (ret ? '<dt>Returned</dt><dd class="ret">' + (st === "done" ? esc(retWords(v, k)) : '<span class="v-meta">' + (st === "run" ? "Working" : "Not run yet") + '</span>') + '</dd>' : '') + '</dl>' +
    '<div class="v-step-more" id="v-sm-' + n + '"' + (open ? '' : ' hidden') + '><p>Also read: ' + esc(reads.slice(shown.length).join(", ")) + '.</p><ul>' + tools + '</ul><p>' + esc(s.rule) + '</p></div>' +
    '</div></' + Tag + '>';
}
C.steps = function(el, ctx, opts){
  opts = opts || {};
  var v = ctx.v;
  var head = opts.head === false ? '' :
    '<div class="v-agent-h"><h2 class="v-agent-t">' + esc(opts.title || "The agent") + '</h2>' +
    (S.replaying ? '<button type="button" class="v-btn v-replay" data-act="skip">Skip</button>' : '<button type="button" class="v-btn v-replay" data-act="replay">' + glyph("replay", 14) + 'Replay</button>') +
    '<p class="v-agent-sub">' + esc(opts.sub || ("One agent, five tool steps, " + plural(v.nCalls, "logged call") + ".")) + '</p></div>';
  el.innerHTML = head + '<ol class="v-steps" aria-label="Agent steps">' + v.steps.map(function(s, k){ return stepHTML(v, k, opts); }).join("") + '</ol>';
};
/* one step on its own, so a layout can put each step at the head of the part it produced. opts.n is the step number */
C.step = function(el, ctx, opts){
  opts = opts || {};
  el.innerHTML = stepHTML(ctx.v, opts.n - 1, {readChars: opts.readChars, ret: opts.ret, tag: "div"});
};
/* the heading of a brief part: the question it answers and the marker of the step that made it */
C.partHead = function(el, ctx, opts){
  opts = opts || {};
  el.innerHTML = '<h2 class="v-part-h" id="ph-' + opts.n + '">' + (opts.glyph ? glyph(opts.glyph, 16) : '') + '<span>' + esc(opts.title) + '</span>' + fromTag(opts.n) + '</h2>';
};

/* ---------- brief parts ---------- */
C.headline = function(el, ctx, opts){
  var h = headline(ctx.m);
  el.innerHTML = (h.kicker && !(opts && opts.kicker === false) ? '<p class="v-kicker">' + esc(h.kicker) + '</p>' : '') +
    '<h2 class="v-head" aria-live="polite"' + fromAttr(2) + '>' + (h.lead ? '<span class="lead">' + esc(h.lead) + '</span>' : '') + esc(h.main) + '</h2>' +
    (h.sub ? '<p class="v-head-sub">' + esc(h.sub) + '</p>' : '');
};
C.care = function(el, ctx, opts){
  var v = ctx.v;
  el.hidden = !v.care;
  el.innerHTML = v.care ? '<div class="v-care" role="note"' + fromAttr(3) + '><b>' + glyph("care", 13).replace('class="v-g st-x"', 'class="v-g" style="display:inline;vertical-align:-2px;margin-right:4px"') + esc(v.care.line) + '</b><span class="why">Why: ' + esc(v.care.signals.join(" ")) + ' ' + esc(v.care.note) + '</span>' + (opts && opts.then ? '<span class="then">' + esc(opts.then) + '</span>' : '') + '</div>' : '';
};

var IW = 12, IG = 2, IH = 28;
function bandChart(it, m){
  var bs = bandsOf(it.p); if (!bs.length || it.lo == null) return '';
  var w = bs.length * (IW + IG) - IG, top = 14, H = top + IH + 12, me = null;
  var bars = bs.map(function(b, k){
    var h = Math.max(1, Math.round(b.observed * IH)), on = b.lo === it.lo, x = k * (IW + IG);
    if (on) me = {x: x, h: h, b: b};
    return '<rect class="' + (on ? 'me' : '') + '" x="' + x + '" y="' + (top + IH - h) + '" width="' + IW + '" height="' + h + '"><title>Scoring ' + bandWords(b.lo, b.hi) + ': ' + pct(b.observed) + ' of ' + Field.fmt(b.n, "int") + ' took it up</title></rect>';
  }).join("");
  var tx = me ? me.x + IW / 2 : 0, anchor = "middle";
  if (me && me.x + IW / 2 > w - 10){ anchor = "end"; tx = w; } else if (me && me.x < 6){ anchor = "start"; tx = 0; }
  var k0 = bs.findIndex(function(b){ return Math.abs(b.lo - m.t) < 1e-6; }), x0 = k0 < 0 ? w + 1 : k0 * (IW + IG) - IG / 2;
  return '<svg class="v-ilad" width="' + w + '" height="' + H + '" viewBox="0 0 ' + w + ' ' + H + '" role="img" aria-label="Take up by score band for ' + esc(it.label) +
    (me ? ': ' + pct(me.b.observed) + ' in this client’s band, ' + bandWords(me.b.lo, me.b.hi) : '') + '">' + bars +
    '<line class="base" x1="0" x2="' + w + '" y1="' + (top + IH + .5) + '" y2="' + (top + IH + .5) + '"/>' +
    (me ? '<text class="me-t" x="' + tx + '" y="' + (top + IH - me.h - 3) + '" text-anchor="' + anchor + '">' + pct(me.b.observed) + '</text>' : '') +
    (m.t > 0.1 + 1e-9 ? '<line class="thl" x1="' + x0 + '" x2="' + x0 + '" y1="' + (top - 2) + '" y2="' + (top + IH + 3) + '"/>' : '') +
    '<text class="ax-t" x="0" y="' + (H - 1) + '">low</text><text class="ax-t" x="' + w + '" y="' + (H - 1) + '" text-anchor="end">high</text></svg>';
}
function ansWords(){ return S.q >= 0 ? "“" + S.v.questions[S.q].answers[S.a].answer + "”" : ""; }
function underBar(it, m){ return m.t > 0.1 + 1e-9 && it.prob != null && it.prob < m.t - 1e-9; }
function itemHTML(it, m, opts){
  /* the band chart is evidence one level down: it opens with why, next to the score band it explains */
  var x = it.x || {}, chart = (it.lane === "offer" || it.lane === "ask") && opts.charts !== false ? bandChart(it, m) : "";
  var cap = chart ? '<p class="v-band-cap">Bars: share of similar clients who took it up, by score band. The coloured bar is this client\u2019s band.</p>' : '';
  var from = it.lane === "offer" || it.lane === "ask" ? 2 : it.ans ? 5 : it.lane === "hold" ? (it.kind === "wait" ? 4 : 3) : it.kind === "prog" ? 3 : 2;
  var h = '<li class="v-item" data-item="i-' + esc(it.p) + '" data-p="' + esc(it.p) + '" data-lane="' + it.lane + '"' + fromAttr(from) + '><div class="txt">';
  var also = m.items.find(function(a){ return a.kind === "also" && a.with === it.p; });
  if (it.lane === "offer"){
    var open = !!S.open["why-" + it.p];
    h += '<p class="nm">' + esc(it.label) + '</p><p class="ev">' + esc(x.line) + '. <button type="button" class="v-link" data-act="toggle" data-key="why-' + esc(it.p) + '" aria-expanded="' + open + '" aria-controls="v-why-' + esc(it.p) + '">Why</button></p>' +
      '<div class="v-why" id="v-why-' + esc(it.p) + '"' + (open ? '' : ' hidden') + '><p>Scores ' + bandWords(it.lo, it.hi) + '. ' + esc(x.bandSentence) + '</p>' +
      (x.reasons.length ? '<p>The score leans on: ' + esc(x.reasons.join("; ")) + '.</p>' : '') + chart + cap + '</div>';
  } else if (it.lane === "ask"){
    var ao = !!S.open["why-" + it.p];
    h += '<p class="nm">' + esc(it.label) + '</p><p class="ev">Not with this bank yet. ' + esc(x.line) + '.' + (also ? ' ' + esc(also.label) + ' is counted with it.' : '') +
      (chart ? ' <button type="button" class="v-link" data-act="toggle" data-key="why-' + esc(it.p) + '" aria-expanded="' + ao + '" aria-controls="v-why-' + esc(it.p) + '">Why</button>' : '') + '</p>' +
      (chart ? '<div class="v-why" id="v-why-' + esc(it.p) + '"' + (ao ? '' : ' hidden') + '>' + chart + cap + '</div>' : '');
  } else if (it.lane === "hold"){
    if (it.ans) h += '<p class="nm">' + esc(it.label) + '</p><p class="ev"><span class="rl">Held back by the answer ' + esc(ansWords()) + '.</span> ' + esc(it.ans.reason || "") + '</p>';
    else if (it.kind === "blocked") h += '<p class="nm">' + esc(it.label) + '</p>' + x.rules.map(function(r, j){ return '<p class="ev"><span class="rl">' + esc(r) + '.</span> ' + esc(x.reasons[j] || "") + '</p>'; }).join("") + (underBar(it, m) ? '<p class="ev">Held back by this rule whatever the bar.</p>' : '');
    else { var hk = "hw-" + it.p, ho = !!S.open[hk];
      /* a held back item shows no score on its face; the band sits one click away, said to be the model's */
      h += '<p class="nm">' + esc(it.label) + '</p><p class="ev"><span class="rl">Waits for the overdue review.</span>' + (it.lo != null ? ' <button type="button" class="v-link" data-act="toggle" data-key="' + hk + '" aria-expanded="' + ho + '" aria-controls="v-hw-' + esc(it.p) + '">Why</button>' : '') + '</p>' +
        (it.lo != null ? '<p class="ev" id="v-hw-' + esc(it.p) + '"' + (ho ? '' : ' hidden') + '>Score band from the model: ' + bandWords(it.lo, it.hi) + '. It does not count while the review is overdue.</p>' : ''); }
  } else {
    var why = it.fell ? "Under the " + pct(m.t) + " bar. It scores " + bandWords(it.lo, it.hi) + "." :
      it.ans ? "Not raised after the answer " + ansWords() + "." :
      it.kind === "prog" ? (x.sentence || "Likely already in progress.") : "Ranked below the top suggestions.";
    var short = opts.asideWhy === "toggle" && it.kind === "prog" && !it.fell && !it.ans && x.sentence, wk = "aw-" + it.p, wo = !!S.open[wk];
    h += '<p class="nm">' + glyph(it.kind === "prog" && !it.fell ? "progress" : "quiet", 13).replace('class="v-g', 'style="display:inline;vertical-align:-1px;margin-right:5px" class="v-g') + esc(it.label) + '</p>' +
      (short ? '<p class="ev">Likely already in progress. <button type="button" class="v-link" data-act="toggle" data-key="' + wk + '" aria-expanded="' + wo + '" aria-controls="v-aw-' + esc(it.p) + '">Why</button></p><p class="ev" id="v-aw-' + esc(it.p) + '"' + (wo ? '' : ' hidden') + '>' + esc(why) + '</p>'
        : '<p class="ev">' + esc(why) + '</p>');
  }
  return h + '</div></li>';
}
function laneBlock(key, title, gl, its, empty, from, opts){
  return '<section class="v-lane" data-lane-key="' + key + '" aria-label="' + esc(title) + '"' + fromAttr(from, ' data-part="' + key + '"') + '>' +
    '<h3 class="v-lane-h">' + (gl ? glyph(gl, 14) : '') + esc(title) + (its.length ? ' <span class="v-count">' + its.length + '</span>' : '') + (opts.tags === false ? '' : ' ' + fromTag(from)) + (opts.extra || '') + '</h3>' +
    '<ul class="v-items">' + (its.length ? its.map(function(it){ return itemHTML(it, S.m, opts); }).join("") : '<li class="v-none">' + esc(empty) + '</li>') + '</ul></section>';
}
C.discuss = function(el, ctx, opts){
  opts = opts || {};
  /* opts.bar: "head" puts the bar control in the lane heading, "below" under the lane */
  el.innerHTML = laneBlock("offer", "Worth discussing", "discuss", lane(ctx.m, "offer"), "Nothing to discuss after the checks.", 2, {charts: opts.charts, tags: opts.tags, extra: opts.bar === "head" ? '<span style="margin-left:auto">' + barHTML() + '</span>' : ''}) +
    (opts.bar === "below" ? '<div class="v-bar-row">' + barHTML(true) + '</div>' : '');
};
C.ask = function(el, ctx, opts){
  opts = opts || {};
  var its = lane(ctx.m, "ask");
  el.hidden = !its.length && opts.hideEmpty !== false;
  el.innerHTML = laneBlock("ask", "Worth asking about", "discuss", its, "Nothing to ask about.", 2, {charts: opts.charts, tags: opts.tags});
};
C.held = function(el, ctx, opts){
  opts = opts || {};
  var n = S.v.toolLog.filter(function(e){ return e.tool === "check_suitability"; }).length;
  var hl = lane(ctx.m, "hold");
  el.innerHTML = laneBlock("hold", "Held back", hl.length ? "heldback" : "quiet", hl, n ? "Nothing. " + plural(n, "product") + " checked against the rules." : "Nothing to check.", 3, opts);
};
C.aside = function(el, ctx, opts){
  opts = opts || {};
  var its = lane(ctx.m, "aside");
  el.hidden = !its.length;
  var prog = its.length && its.every(function(it){ return it.kind === "prog" && !it.fell; });
  el.innerHTML = its.length ? laneBlock("aside", prog ? "Likely in progress" : "Not raised", prog ? "progress" : "quiet", its, "", prog ? 3 : 2, opts) : '';
};
C.review = function(el, ctx, opts){
  opts = opts || {};
  var d = ctx.v.due, st, sub;
  if (d.state === "overdue"){ st = "Overdue by " + plural(-d.days, "day"); sub = d.sub + "." + (ctx.v.waitingText ? " " + ctx.v.waitingText + "." : ""); }
  else if (d.state === "due"){ st = "Due in " + plural(d.days, "day"); sub = "Can be covered in this meeting. " + d.sub + "."; }
  else if (d.state === "not_due"){ st = "Not due"; sub = d.sub + "."; }
  else { st = "No review date on file"; sub = ""; }
  el.innerHTML = '<section class="v-lane" aria-label="Periodic review"' + fromAttr(4, ' data-part="due"') + '><h3 class="v-lane-h">Periodic review' + (opts.tags === false ? '' : ' ' + fromTag(4)) + '</h3>' +
    '<p class="v-review" data-st="' + d.state + '"><span class="st">' + esc(st) + '</span><span class="sub">' + esc(sub) + '</span><span class="syn">Synthetic date.</span></p></section>';
};
function barHTML(long){
  return '<span class="v-bar"><span id="v-bar-l">' + (long ? 'Only include scores above' : 'Bar') + '</span><span class="v-segs" role="group" aria-labelledby="v-bar-l">' + BARS.map(function(t){
    return '<button type="button" data-act="bar" data-t="' + t + '" aria-pressed="' + (Math.abs(t - S.thr) < 1e-9) + '" aria-label="Only include scores above ' + pct(t) + '">' + pct(t) + '</button>'; }).join("") + '</span></span>';
}
C.bar = function(el){ el.innerHTML = barHTML(); };

function outcomeHTML(a){
  var held = [], dropped = [];
  S.m.items.forEach(function(it){ if (it.ans && it.kind !== "also" && !it.fell) (it.ans.how === "held" ? held : dropped).push(it.label); });
  var diff = [held.length ? '<b>' + esc(list(held)) + '</b> moved to Held back.' : '', dropped.length ? '<b>' + esc(list(dropped)) + '</b> moved to Not raised.' : ''].filter(Boolean).join(" ");
  if (!diff && a.outcome && !a.outcome.changes_brief) diff = "Nothing in the brief moves.";
  var o = a.outcome || {}, extra = (o.review || []).concat(o.notes || []).filter(function(s){ return a.outcome_line.indexOf(s) < 0; });
  return '<p>' + esc(a.outcome_line) + '</p>' + (diff ? '<p class="diff">' + diff + '</p>' : '') + (extra.length ? '<p>' + esc(extra.join(" ")) + '</p>' : '') +
    '<button type="button" class="v-link" data-act="clear">Clear the answer</button>';
}
/* atlas: each question is a small decision tree. the question sits at the root, the answers branch under it,
   and the chosen branch leads down to what the brief does then. same buttons and state as before */
C.questions = function(el, ctx, opts){
  opts = opts || {};
  var v = ctx.v;
  el.innerHTML = '<section class="v-lane at-qs-l" aria-label="Questions"' + fromAttr(5, ' data-part="qs"') + '>' +
    '<ol class="at-trees" data-nq="' + v.questions.length + '">' + v.questions.map(function(q, j){
      var review = q.kind === "Periodic review", care = q.key === "care", kind = review ? "Part of the periodic review" : q.kind ? (KIND_WORDS[q.kind] || q.kind) : "";
      var wk = "qwhy" + j, wopen = !!S.open[wk], on = S.q === j, n = q.answers.length;
      return '<li class="at-tree' + (on ? ' is-on' : '') + '" style="--n:' + Math.max(1, n) + (on ? ';--k:' + S.a : '') + '">' +
        '<div class="at-q"><p class="at-qk' + (care ? ' care-k' : '') + '">' + esc(kind) + '</p><p class="qt" id="v-qt' + j + '">“' + esc(q.text) + '”</p>' +
        (q.why ? '<p class="qw"><button type="button" class="v-link" data-act="toggle" data-key="' + wk + '" aria-expanded="' + wopen + '" aria-controls="v-qw' + j + '">Why asked</button></p>' +
          '<p class="qw" id="v-qw' + j + '"' + (wopen ? '' : ' hidden') + '>Asked because: ' + esc(low1(q.why)) + '</p>' : '') + '</div>' +
        (n ? '<div class="at-fork" role="group" aria-labelledby="v-al' + j + ' v-qt' + j + '"><p class="at-fork-l" id="v-al' + j + '">If the client says</p><ul class="at-br">' +
          q.answers.map(function(a, k){ var pr = on && S.a === k;
            return '<li' + (pr ? ' class="is-on"' : '') + '><button type="button" class="at-ans" data-act="answer" data-q="' + j + '" data-a="' + k + '" aria-pressed="' + pr + '" aria-controls="v-out' + j + '">' + esc(a.answer) + '</button></li>'; }).join("") +
          '</ul></div>' : '') +
        '<div class="v-out at-then" id="v-out' + j + '" aria-live="polite"' + (on ? '' : ' hidden') + '>' + (on ? '<p class="at-then-l">Then</p>' + outcomeHTML(q.answers[S.a]) : '') + '</div></li>';
    }).join("") + '</ol></section>';
};
C.followup = function(el, ctx, opts){
  var v = ctx.v; opts = opts || {};
  if (!v.followUp){ el.innerHTML = ''; el.hidden = true; return; }
  el.hidden = false;
  var a = S.q >= 0 ? v.questions[S.q].answers[S.a] : null, text = a && a.follow_up ? a.follow_up : v.followUp.text;
  el.innerHTML = '<section class="v-fu" aria-label="Follow up draft"' + fromAttr(5) + '><div class="v-fu-h"><h3 class="v-lane-h">Follow up draft' + (opts.tags === false ? '' : ' ' + fromTag(5)) + '</h3>' +
    '<button type="button" class="v-link" data-act="fu" aria-expanded="' + S.fu + '" aria-controls="v-fu-body">' + (S.fu ? 'Hide the draft' : 'Show the draft') + '</button></div>' +
    '<p class="v-fu-l">' + esc(v.followUp.label) + '</p>' +
    '<div class="v-fu-body" id="v-fu-body"' + (S.fu ? '' : ' hidden') + '><p class="v-fu-a" aria-live="polite">' + (a ? 'As it reads if the client says ' + esc(ansWords()) + '.' : 'As drafted before the meeting.') + '</p>' +
    '<div class="v-fu-t">' + esc(text) + '</div><p class="v-fu-acts"><button type="button" class="v-btn" data-act="copy">Copy the text</button><span class="v-fu-st" aria-live="polite"></span></p></div></section>';
};
/* the raw model output, for the before and after comparison only. the caller must label it as raw */
C.ranked = function(el, ctx){
  el.innerHTML = '<ol class="v-ranked">' + ctx.v.ranked.map(function(r, k){
    return '<li data-item="r-' + esc(r.product) + '" data-p="' + esc(r.product) + '"><span class="k v-num">' + (k + 1) + '</span><span class="nm">' + esc(r.label) + '</span><span class="raw v-num">' + Field.fmt(r.probability, "dec3") + '</span></li>'; }).join("") + '</ol>';
};
C.footer = function(el){
  var F = S.F;
  el.innerHTML = '<p><b>Djamel Zair, application for Junior Data Scientist, CLUE.</b> Independent prototype for a job application. Not affiliated with or endorsed by Rabobank. Review dates and vulnerability flags are synthetic.</p>' +
    '<p class="v-foot-l"><a href="../../../' + F.links.model + '">How the models perform</a> <a href="' + esc(F.links.code) + '">Code</a></p>';
};

/* a skeleton: grey lines where a part will be, shown until data.json is in */
C.skeleton = function(el, ctx, opts){
  var n = (opts && opts.lines) || 3, h = '<div class="v-sk" aria-hidden="true">';
  for (var k = 0; k < n; k++) h += '<i></i>';
  el.innerHTML = h + '</div>'; el.setAttribute("aria-busy", "true");
};

/* ---------- app chrome ---------- */
C.picker = function(el){
  var F = S.F;
  el.innerHTML = '<div class="v-picker"><button type="button" class="v-btn" data-act="prev" aria-label="Previous client" title="Previous client">' +
    '<svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M7.5 2.5L4 6l3.5 3.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button>' +
    '<label class="v-sr" for="v-pick">Client</label><span class="v-sel"><select id="v-pick">' + F.clients.map(function(c){ return '<option value="' + c.index + '">' + esc(c.ref + ": " + c.tag) + '</option>'; }).join("") + '</select></span>' +
    '<button type="button" class="v-btn" data-act="next" aria-label="Next client" title="Next client"><svg width="12" height="12" viewBox="0 0 12 12" aria-hidden="true"><path d="M4.5 2.5L8 6 4.5 9.5" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg></button></div>';
  var sel = el.querySelector("select"); sel.value = String(S.v ? S.v.index : F.start);
  sel.addEventListener("change", function(){ show(+sel.value, true); });
};
var scheme = {
  list: SCHEMES,
  get: function(){ return document.documentElement.getAttribute("data-scheme") || "S1"; },
  set: function(id, push){
    if (!SCHEMES.some(function(s){ return s.id === id; })) id = "S1";
    document.documentElement.setAttribute("data-scheme", id);
    document.querySelectorAll("[data-act=scheme]").forEach(function(b){ b.setAttribute("aria-pressed", String(b.getAttribute("data-id") === id)); });
    if (push !== false){ try { var u = new URL(location.href); u.searchParams.set("scheme", id); history.replaceState(null, "", u); } catch (e) {} }
    if (S.v) emit("render", ctxNow());
  },
  fromURL: function(){ var m = /[?&]scheme=(S[1-4])\b/i.exec(location.search); return m ? m[1].toUpperCase() : null; }
};
C.scheme = function(el){
  var cur = scheme.get();
  el.innerHTML = '<div class="v-switch v-scheme" role="group" aria-label="Colour scheme"><span class="lbl">Scheme</span><span class="opts">' + SCHEMES.map(function(s){
    return '<button type="button" data-act="scheme" data-id="' + s.id + '" aria-pressed="' + (s.id === cur) + '" title="' + esc(s.name) + '" aria-label="' + esc(s.id + ", " + s.name) + '">' +
      '<span class="sw" data-scheme="' + s.id + '" aria-hidden="true"><i></i><i></i><i></i></span>' + s.id + '</button>'; }).join("") + '</span></div>';
};
/* the design system switch sits next to the scheme switch and works the same way: ?ds=ibm|mercury|linear */
var ds = {
  list: DSS,
  get: function(){ return document.documentElement.getAttribute("data-ds") || "ibm"; },
  set: function(id, push){
    if (!DSS.some(function(d){ return d.id === id; })) id = "ibm";
    document.documentElement.setAttribute("data-ds", id);
    /* the head script owns the font links, so the face for a layer is only fetched when that layer is picked */
    if (window.__dsFont) window.__dsFont(id);
    document.querySelectorAll("[data-act=ds]").forEach(function(b){ b.setAttribute("aria-pressed", String(b.getAttribute("data-id") === id)); });
    if (push !== false){ try { var u = new URL(location.href); u.searchParams.set("ds", id); history.replaceState(null, "", u); } catch (e) {} }
    /* type metrics change, so whatever is drawn to its box redraws once the face is in */
    if (S.v){ emit("render", ctxNow()); if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ emit("render", ctxNow()); emit("resize"); }); }
  },
  fromURL: function(){ var m = /[?&]ds=(ibm|mercury|linear)\b/i.exec(location.search); return m ? m[1].toLowerCase() : null; }
};
C.ds = function(el){
  var cur = ds.get();
  el.innerHTML = '<div class="v-switch v-ds" role="group" aria-label="Design system"><span class="lbl">Design</span><span class="opts">' + DSS.map(function(d){
    return '<button type="button" data-act="ds" data-id="' + d.id + '" aria-pressed="' + (d.id === cur) + '" title="' + esc(d.name) + ' type, space, depth and shape">' + esc(d.name.split(" ")[0]) + '</button>'; }).join("") + '</span></div>';
};

/* ---------- linking registry ---------- */
var extra = []; /* [step, element or selector] that a layout registers on top of data-from */
var links = {
  register: function(step, target){ extra.push([step, target]); links.apply(); },
  select: function(n){ S.link = S.link === n ? 0 : n; links.apply(); emit("link", S.link); },
  set: function(n){ S.link = n; links.apply(); emit("link", S.link); },
  clear: function(){ S.link = 0; links.apply(); emit("link", 0); },
  current: function(){ return S.link; },
  /* every element a step produced, for layouts that draw connectors */
  targets: function(n){
    var a = [].slice.call(document.querySelectorAll('[data-from~="' + n + '"]'));
    extra.forEach(function(e){ if (e[0] === n) a = a.concat(typeof e[1] === "string" ? [].slice.call(document.querySelectorAll(e[1])) : [e[1]]); });
    return a;
  },
  apply: function(){
    document.querySelectorAll("[data-from]").forEach(function(el){ var on = S.link && (" " + el.getAttribute("data-from") + " ").indexOf(" " + S.link + " ") >= 0; if (on) el.setAttribute("data-lit", "1"); else el.removeAttribute("data-lit"); });
    extra.forEach(function(e){ var els = typeof e[1] === "string" ? document.querySelectorAll(e[1]) : [e[1]]; [].forEach.call(els, function(el){ if (el) el.toggleAttribute("data-lit", S.link === e[0]); }); });
    document.querySelectorAll('[data-act="link"]').forEach(function(b){ b.setAttribute("aria-pressed", String(+b.getAttribute("data-step") === S.link)); });
    document.querySelectorAll(".v-step").forEach(function(li){ li.toggleAttribute("data-linked", +li.getAttribute("data-step-n") === S.link); });
  }
};

/* ---------- rendering ---------- */
function ctxNow(){ return {F: S.F, v: S.v, m: S.m, state: S, V: V}; }
/* what each component reads. "client" is the picked client, "model" the lanes after the bar and the answer,
   "answer" the chosen answer, "replay" whether the agent is replaying. a change only rerenders what reads it */
var DEPS = {identity: ["client"], mismatch: ["client"], groupNote: ["client"], chips: ["client"], facts: ["client"], meeting: ["client"],
  timeline: ["client"], wallet: ["client", "model"], legend: ["client"], steps: ["client", "replay"], step: ["client", "replay"], partHead: ["client"],
  headline: ["client", "model"], care: ["client"], discuss: ["client", "model"], ask: ["client", "model"], held: ["client", "model"],
  aside: ["client", "model"], review: ["client"], bar: ["client", "model"], questions: ["client", "answer"], followup: ["client", "answer"],
  ranked: ["client"], summary: ["client", "model"], context: ["client"]};
function depsOf(mt){ return (mt.opts && mt.opts.deps) || (typeof mt.fn === "string" ? DEPS[mt.fn] : mt.fn.deps) || ["client"]; }
/* why: "client", "bar", "answer" or "replay" */
function touches(mt, why){
  var d = depsOf(mt);
  if (why === "client") return true;
  if (why === "bar") return d.indexOf("model") >= 0 || (S.q >= 0 && d.indexOf("answer") >= 0);
  if (why === "answer") return d.indexOf("model") >= 0 || d.indexOf("answer") >= 0;
  return d.indexOf(why) >= 0;
}
function draw(mt, ctx){
  [].forEach.call(document.querySelectorAll(mt.sel), function(el){
    (typeof mt.fn === "string" ? C[mt.fn] : mt.fn)(el, ctx, mt.opts);
    el.removeAttribute("aria-busy");
    /* a render count per mount, so a check can see that a change left the other parts alone */
    el.setAttribute("data-renders", String(+(el.getAttribute("data-renders") || 0) + 1));
  });
}
function renderAll(flip, why){
  why = why || "client";
  var before = {}, oldLane = {};
  if (flip && !reduce) document.querySelectorAll("[data-item]").forEach(function(el){ before[el.getAttribute("data-item")] = el.getBoundingClientRect(); oldLane[el.getAttribute("data-item")] = el.getAttribute("data-lane") || el.getAttribute("data-st"); });
  if (why !== "replay") S.m = model(S.v, S);
  var ctx = ctxNow();
  mounts.forEach(function(mt){ if (touches(mt, why)) draw(mt, ctx); });
  links.apply();
  if (flip) document.querySelectorAll("[data-item]").forEach(function(el){
    var k = el.getAttribute("data-item"), now = el.getAttribute("data-lane") || el.getAttribute("data-st");
    if (!(k in oldLane) || oldLane[k] === now) return;
    el.classList.add("is-moved");
    var r0 = before[k]; if (!r0 || reduce) return;
    var r1 = el.getBoundingClientRect();
    el.animate([{transform: "translate(" + (r0.left - r1.left) + "px," + (r0.top - r1.top) + "px)", opacity: .6}, {transform: "none", opacity: 1}], {duration: motion("--dur-slow", 360), easing: motion("--ease")});
  });
  emit("render", ctx);
}
/* during a replay a part waits, faded, until every step it came from is done. this marks what is already on the page,
   so a replay never has to redraw the brief */
function readyMarks(){
  document.querySelectorAll("[data-from]").forEach(function(el){
    var need = el.getAttribute("data-from").split(/\s+/).map(Number);
    if (S.replaying && !need.every(function(n){ return S.stepState[n - 1] === "done"; })) el.setAttribute("data-ready", "0"); else el.removeAttribute("data-ready");
  });
}
/* the five steps replay one after another, 150ms apart; what each step produced appears when it finishes */
function setStep(k, st){
  S.stepState[k] = st;
  var li = document.getElementById("v-step-" + (k + 1));
  if (li){
    li.setAttribute("data-s", st);
    var badge = li.querySelector(".v-st"), status = li.getAttribute("data-status");
    if (badge){ badge.setAttribute("data-status", st === "done" ? status : st); badge.textContent = st === "done" ? statusWords(S.v, k, status) : st === "run" ? "Running" : "Waiting"; }
    var ret = li.querySelector("dd.ret"); if (ret && st === "done") ret.textContent = retWords(S.v, k);
    else if (ret && st === "run") ret.innerHTML = '<span class="v-meta">Working</span>';
  }
  if (st === "done"){
    readyMarks();
    emit("step", k + 1, "done");
    if (k === S.v.steps.length - 1) endReplay();
  } else emit("step", k + 1, st);
}
function startReplay(){
  if (!S.v) return;
  S.cancel(); S.replaying = true; S.stepState = S.v.steps.map(function(){ return "wait"; });
  renderAll(false, "replay"); readyMarks();
  S.cancel = Field.play(S.v.steps.length, setStep, 150);
}
function endReplay(){
  if (!S.replaying) return;
  S.cancel(); S.cancel = function(){}; S.replaying = false; S.stepState = [];
  var hadSkip = document.activeElement && document.activeElement.getAttribute && document.activeElement.getAttribute("data-act") === "skip";
  renderAll(false, "replay"); readyMarks();
  if (hadSkip){ var r = document.querySelector('[data-act="replay"]'); if (r) r.focus(); }
}
function show(i, animate){
  S.cancel(); S.replaying = false; S.stepState = [];
  S.v = S.F.view(i); S.q = -1; S.a = -1; S.open = {}; S.fu = false;
  var sel = document.getElementById("v-pick"); if (sel) sel.value = String(i);
  try { var u = new URL(location.href); u.hash = S.v.ref.replace(/\s+/g, "-").toLowerCase(); history.replaceState(null, "", u); } catch (e) {}
  emit("client", S.v);
  /* a new client is the one change that redraws the whole brief; a replay then only fades and shows what is there */
  if (animate && !reduce){ S.replaying = true; S.stepState = S.v.steps.map(function(){ return "wait"; }); }
  renderAll(false, "client");
  if (S.replaying){ readyMarks(); S.cancel = Field.play(S.v.steps.length, setStep, 150); }
}
/* a chosen answer only moves the lanes and the questions; the bar only moves the lanes */
function setAnswer(q, a){ S.q = q; S.a = a; renderAll(true, "answer"); }
function setBar(t){ if (Math.abs(t - S.thr) < 1e-9) return; S.thr = t; renderAll(true, "bar"); }

/* ---------- one delegated listener for every component ---------- */
document.addEventListener("click", function(e){
  if (!S.F) return;
  var b = e.target.closest("[data-act]");
  if (b){
    var act = b.getAttribute("data-act");
    if (act === "link"){ links.select(+b.getAttribute("data-step")); return; }
    if (act === "answer"){ var q = +b.getAttribute("data-q"), a = +b.getAttribute("data-a"); if (S.q === q && S.a === a) setAnswer(-1, -1); else setAnswer(q, a);
      var nb = document.querySelector('[data-act="answer"][data-q="' + q + '"][data-a="' + a + '"]'); if (nb) nb.focus({preventScroll: true}); return; }
    if (act === "clear"){ var q0 = S.q; setAnswer(-1, -1); var f0 = document.querySelector('[data-act="answer"][data-q="' + q0 + '"]'); if (f0) f0.focus({preventScroll: true}); return; }
    if (act === "bar"){ setBar(+b.getAttribute("data-t")); var bb = document.querySelector('[data-act="bar"][data-t="' + b.getAttribute("data-t") + '"]'); if (bb) bb.focus({preventScroll: true}); return; }
    if (act === "toggle"){ var key = b.getAttribute("data-key"), open = !S.open[key]; S.open[key] = open; b.setAttribute("aria-expanded", String(open));
      var t = document.getElementById(b.getAttribute("aria-controls")); if (t) t.hidden = !open; emit("render", ctxNow()); return; }
    if (act === "fu"){ S.fu = !S.fu; b.setAttribute("aria-expanded", String(S.fu)); b.textContent = S.fu ? "Hide the draft" : "Show the draft";
      var body = document.getElementById("v-fu-body"); if (body){ body.hidden = !S.fu; if (S.fu && !reduce) body.animate([{opacity: 0, transform: "translateY(4px)"}, {opacity: 1, transform: "none"}], {duration: motion("--dur", 220), easing: motion("--ease")}); }
      emit("render", ctxNow()); return; }
    if (act === "copy"){
      var txt = (b.closest(".v-fu").querySelector(".v-fu-t") || {}).textContent || "", st = b.parentNode.querySelector(".v-fu-st");
      var done = function(ok){ if (st){ st.textContent = ok ? "Copied. Nothing was sent." : "Select the text to copy it."; setTimeout(function(){ st.textContent = ""; }, 2600); } };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(txt).then(function(){ done(true); }, function(){ done(false); }); else done(false);
      return;
    }
    if (act === "replay"){ startReplay(); var sk = document.querySelector('[data-act="skip"]'); if (sk) sk.focus(); return; }
    if (act === "skip"){ endReplay(); return; }
    if (act === "scheme"){ scheme.set(b.getAttribute("data-id")); return; }
    if (act === "ds"){ ds.set(b.getAttribute("data-id")); return; }
    if (act === "prev"){ show((S.v.index - 1 + S.F.count) % S.F.count, true); return; }
    if (act === "next"){ show((S.v.index + 1) % S.F.count, true); return; }
    return;
  }
  /* a click on any part of the brief (outside a control) selects the step that made it */
  if (e.target.closest("a, button, select, input, label")) return;
  var part = e.target.closest("[data-from]");
  if (part){ var n = +part.getAttribute("data-from").split(/\s+/)[0]; if (n) links.set(S.link === n ? 0 : n); }
});
document.addEventListener("keydown", function(e){
  if (!S.F) return;
  if (e.key === "Escape"){ if (S.replaying){ endReplay(); return; } if (S.q >= 0){ setAnswer(-1, -1); return; } if (S.link){ links.clear(); } }
});

/* ---------- boot ---------- */
/* opts.mounts: {selector: componentName | function(el, ctx, opts) | [componentName, opts]} */
function boot(opts){
  opts = opts || {};
  scheme.set(scheme.fromURL() || opts.scheme || "S1", false);
  ds.set(ds.fromURL() || opts.ds || "ibm", false);
  Object.keys(opts.mounts || {}).forEach(function(sel){ var m = opts.mounts[sel]; mount(sel, Array.isArray(m) ? m[0] : m, Array.isArray(m) ? m[1] : undefined); });
  return Field.load(opts.url || "../../../data.json").then(function(F){
    S.F = F;
    var start = F.start;
    if (location.hash){ var h = F.clients.findIndex(function(c){ return "#" + c.ref.replace(/\s+/g, "-").toLowerCase() === location.hash.toLowerCase(); }); if (h >= 0) start = h; }
    (opts.chrome || []).forEach(function(c){ var el = document.querySelector(c[0]); if (el) C[c[1]](el, ctxNow(), c[2]); });
    window.__brief = {count: F.count, start: start, show: function(i, animate){ show(i, animate); }};
    emit("ready", F);
    show(start, opts.animateFirst !== false);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function(){ emit("render", ctxNow()); });
    return F;
  }).catch(function(e){
    console.error(e);
    document.body.insertAdjacentHTML("afterbegin", '<p class="v-loaderr">This page reads docs/data.json and could not load it. Serve the docs folder (python -m http.server inside docs) and open brief/explore/atlas/ from there.</p>');
  });
}
/* a mount draws a skeleton straight away and its real part once the data is in. opts.sk sets how many skeleton lines */
function mount(sel, fn, o){
  var mt = {sel: sel, fn: fn, opts: o}; mounts.push(mt);
  if (S.v) draw(mt, ctxNow());
  else [].forEach.call(document.querySelectorAll(sel), function(el){ C.skeleton(el, null, {lines: (o && o.sk) || 3}); });
}

var V = {
  briefOf: function(v){ return briefOf(v); }, monYear: monYear, addMonths: addMonths, iso: iso,
  boot: boot, mount: mount, components: C, links: links, scheme: scheme, ds: ds, glyph: glyph, fromTag: fromTag,
  show: show, setAnswer: setAnswer, setBar: setBar, replay: startReplay, skip: endReplay, render: function(why){ renderAll(false, why); },
  on: function(evt, fn){ handlers[evt].push(fn); },
  state: S, model: model, lane: lane, headline: headline, walletState: walletState, stepStatus: stepStatus, bandChart: bandChart,
  STATE_WORDS: STATE_WORDS, walletCounts: walletCounts, retWords: retWords, statusWords: statusWords, readWords: readWords, stepDone: stepDone, STEP_OF: STEP_OF, BARS: BARS, util: {pct: pct, list: list, cap: cap, low1: low1, bandWords: bandWords, tenureWords: tenureWords}
};
window.V = V;
})();
