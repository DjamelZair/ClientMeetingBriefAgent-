/* shared by field_v1 to field_v5 and model.html: reads data.json, builds one view per showcase client,
   and renders the parts every version has in common (the novelty strip, the client panel on the left,
   the footer). each version only draws its own centre and right side in onClient.
   no number is typed in here; everything comes from data.json, which python main.py writes. */
(function(){
"use strict";

var RULE_LABELS = {deceased:"Recorded as deceased", under_18_basic_only:"Under 18: basic accounts only",
  credit_under_18:"Under 18: no credit", credit_activity_drop:"Activity dropped: no credit",
  credit_vulnerable:"Possibly vulnerable: no credit", credit_income_missing:"No income on file: no credit",
  investment_no_risk_profile:"No risk profile: no investments", investment_account_cautious:"Cautious profile: no investment account",
  investment_vulnerable:"Possibly vulnerable: no investments", review_overdue:"Review overdue: nothing new",
  declined_recently:"Declined recently: not raised again yet"};
var CHANGE_LABELS = {flag_new_products:"Added products", flag_dropped_products:"Closed products",
  flag_activity_drop:"Became inactive", flag_moved:"Moved province", flag_new_client:"New client", flag_segment_change:"Segment changed"};

function fmt(v, f){
  if (v == null || (typeof v === "number" && isNaN(v))) return "n/a";
  if (f === "int") return Math.round(v).toLocaleString("en-GB");
  if (f === "pct") return Math.round(v * 100) + "%";
  if (f === "pct1") return (v * 100).toFixed(1) + "%";
  if (f === "dec2") return Number(v).toFixed(2);
  if (f === "dec3") return Number(v).toFixed(3);
  return String(v);
}
function esc(s){ return String(s == null ? "" : s).replace(/[&<>"]/g, function(c){ return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
function cap1(s){ return s ? s.charAt(0).toUpperCase() + s.slice(1) : s; }
function plural(n, w){ return n + " " + w + (n === 1 ? "" : "s"); }
function nice(iso){ return new Date(iso + "T00:00:00").toLocaleDateString("en-GB", {day:"numeric", month:"long", year:"numeric"}); }
function rlabel(r){ return RULE_LABELS[r] || String(r).replace(/_/g, " "); }

/* the profile wording comes from the pipeline's own markdown, so no page rephrases it */
function profileFacts(md){
  var lines = String(md || "").split("\n"), i = lines.findIndex(function(l){ return l.indexOf("## 1.") === 0; });
  if (i < 0) return [];
  var line = "";
  for (var j = i + 1; j < lines.length; j++){ var l = lines[j].trim(); if (!l || l.charAt(0) === "*") continue; line = l; break; }
  var cut = line.indexOf(": ");
  return (cut >= 0 ? line.slice(0, cut) : line).replace(/\.$/, "").split(", ").map(cap1);
}

function make(D){
  var labels = D.meta.product_labels || {}, specs = D.meta.agent_steps || [];
  function plabel(c){ return labels[c] || String(c).replace(/_/g, " "); }

  function tagOf(s){
    var p = (s.picked_for || [])[0] || "", m = /^cluster (\d+) example$/.exec(p);
    if (m){ var c = D.segmentation.clusters.find(function(x){ return x.cluster === +m[1]; }); return c ? c.name : p; }
    m = /^shows rule (.+)$/.exec(p); if (m) return rlabel(m[1]);
    m = /^recent change (.+)$/.exec(p); if (m) return CHANGE_LABELS["flag_" + m[1]] || m[1];
    return p === "random fill" ? "random client" : cap1(p);
  }

  /* the logged calls grouped into the five steps, next to what each step reads, runs and returns */
  function steps(b){
    var log = b.tool_log, by = function(t){ return log.filter(function(e){ return e.tool === t; }); };
    var seg = by("get_segment")[0], prop = by("get_propensities")[0], q = by("draft_questions")[0];
    var suit = by("check_suitability"), lk = by("check_linked").filter(function(e){ return / in progress$/.test(e.summary); });
    var held = suit.filter(function(e){ return / blocked by /.test(e.summary); });
    var r = b.due_anyway;
    var results = [
      seg ? seg.summary.replace(/^cluster \d+, /, "") : "",
      prop ? prop.summary : "",
      (!suit.length ? "nothing above " + fmt(b.threshold, "pct") + " to check" :
        plural(suit.length, "product") + " checked, " + (suit.length - held.length) + " allowed, " + held.length + " held back" +
        (lk.length ? ", " + lk.length + " in progress" : "")) +
        /* the care check runs for every client; it only shows in the result when it found something */
        (b.care && b.care.flag ? "; signs to check for care" : ""),
      r.next_review == null ? "no review date on file" : r.days_until < 0 ? "overdue by " + plural(-r.days_until, "day") :
        r.due ? "due in " + plural(r.days_until, "day") : "not due for " + plural(r.days_until, "day"),
      q ? q.summary : ""
    ];
    var keys = ["who", "help", "not", "due", "qs"];
    return specs.map(function(sp, i){
      return {n: sp.n, key: keys[i], name: sp.name, result: results[i], reads: sp.reads, returns: sp.returns, rule: sp.rule_or_model,
              tools: sp.tools.map(function(t){ var c = by(t).length; return {tool: t, calls: c}; }).filter(function(t){ return t.calls; }),
              calls: log.filter(function(e){ return sp.tools.indexOf(e.tool) >= 0; })};
    });
  }

  function view(i){
    var s = D.showcase[i], b = s.brief, w = b.who, r = b.due_anyway, due;
    if (r.next_review == null) due = {state: "none", headline: "No review date on file", sub: ""};
    else if (r.days_until < 0) due = {state: "overdue", headline: "Overdue by " + plural(-r.days_until, "day"), sub: "Was due " + nice(r.next_review)};
    else if (r.due) due = {state: "due", headline: "Due in " + plural(r.days_until, "day"), sub: "Next review " + nice(r.next_review)};
    else due = {state: "not_due", headline: "Not due", sub: "Next review " + nice(r.next_review)};
    due.days = r.days_until; due.riskClass = r.risk_class; due.sentence = r.sentence; due.windowDays = D.reviews.window_days;
    return {
      index: i, ref: s.client_ref, tag: tagOf(s),
      meeting: nice(b.meeting_date), threshold: b.threshold, thresholdText: fmt(b.threshold, "pct"),
      nextStep: b.next_step,
      who: {cluster: w.cluster, name: w.cluster_name, description: w.cluster_description, facts: profileFacts(s.markdown),
            changes: w.change_flags.map(function(f, k){ return {flag: f, label: CHANGE_LABELS[f] || f, sentence: w.changes[k]}; })},
      /* never a raw probability: score is the capped display text, observed is the take up rate in its band */
      help: b.might_help.map(function(x){ var bd = x.band || {};
        return {product: x.product, label: x.label, score: x.score_display, bandLo: bd.lo, bandHi: bd.hi,
                observed: bd.enough ? bd.observed : null, n: bd.n, bandSentence: x.band_sentence,
                line: bd.enough ? Math.round(bd.observed * 100) + "% of " + fmt(bd.n, "int") + " similar clients took it up" : "too few similar clients to compare",
                reasons: x.reasons || [],
                /* product: something the bank sells. flow: where the client's money goes, asked about, not sold */
                kind: x.kind || "product", also: x.also || "", notHeld: (D.meta.not_held || {})[x.product] || ""}; }),
      inProgress: b.in_progress.map(function(x){ return {product: x.product, label: x.label, score: x.score_display, sentence: x.sentence}; }),
      blocked: b.not_to_offer.map(function(x){
        var keep = x.rules.map(function(r, k){ return [r, x.reasons[k]]; }).filter(function(p){ return !(b.next_step && p[0] === "review_overdue"); });
        return {product: x.product, label: x.label, score: x.score_display, rules: keep.map(function(p){ return rlabel(p[0]); }),
                reasons: keep.map(function(p){ return p[1]; })}; }),
      waiting: b.waiting_for_review,
      waitingText: b.waiting_for_review ? (b.waiting_for_review === 1 ? "1 product waits" : b.waiting_for_review + " products wait") + " for the review" : "",
      due: due,
      /* each question: text, kind, why (the signal from the data) and answers with what the brief then does */
      questions: b.question_cards || b.questions.map(function(q){ return {text: q, kind: "", why: "", answers: []}; }),
      holdings: b.holdings || [],
      /* every scored product with its raw score, only for the "typical recommender" comparison */
      ranked: b.ranked || [],
      steps: steps(b), nCalls: b.tool_log.length, toolLog: b.tool_log,
      /* care comes before anything else when the data shows signs of difficulty; the follow up is a draft, never sent */
      care: b.care && b.care.flag ? {line: b.care.line, signals: b.care.signals || [], note: b.care.synthetic_note || ""} : null,
      followUp: b.follow_up || null
    };
  }

  /* the page opens on a client with something the bank actually sells and something worth asking about,
     so the first screen shows both kinds; failing that, any client with a product to offer */
  function has(s, kind){ return s.brief.might_help.some(function(x){ return (x.kind || "product") === kind; }); }
  var start = D.showcase.findIndex(function(s){ return has(s, "product") && has(s, "flow"); });
  if (start < 0) start = D.showcase.findIndex(function(s){ return has(s, "product"); });
  var mc = D.model_card || {};
  return {
    data: D, view: view, fmt: fmt, esc: esc, plural: plural, plabel: plabel, rlabel: rlabel, nice: nice,
    count: D.showcase.length, start: start < 0 ? 0 : start,
    clients: D.showcase.map(function(s, i){ return {index: i, ref: s.client_ref, tag: tagOf(s)}; }),
    novelty: D.meta.novelty || [], stateWords: D.meta.state_words || {}, stepSpecs: specs, modelCard: mc,
    pitch: {
      goal: "Give a client advisor a one page brief before every meeting.",
      data: fmt(D.data_facts.sample_clients, "int") + " real anonymised bank clients (Santander, public) plus a labelled synthetic KYC layer.",
      result: "Suggestions with reasons, products held back for the client's sake, and reviews that can be covered in the same meeting."
    },
    /* each label says exactly what was counted, so a reader can check it against the code */
    kpis: [
      {key: "clients", value: fmt(D.reviews.n_clients, "int"),
       label: "clients briefed (" + fmt(D.data_facts.sample_clients - D.reviews.n_clients, "int") + " recorded as deceased are left out)"},
      {key: "products", value: fmt(D.data_facts.n_products_modelled, "int"), of: fmt(D.data_facts.n_products_raw, "int"),
       label: "products modelled (the rest have too few take ups to train and test on)"},
      {key: "held", value: fmt(D.guardrail.at_default.n_blocked, "int"),
       label: "high scoring suggestions held back by the suitability check, for " + fmt(D.guardrail.at_default.n_clients_with_blocked, "int") + " clients"},
      {key: "reviews", value: fmt(D.reviews.n_meetings_covering_review, "int"),
       label: "clients with a suggestion whose periodic review is also due within " + D.reviews.window_days + " days"}
    ],
    links: {model: "model.html", notebook: "notebook.html", code: D.meta.code_url, home: "index.html", readme: D.meta.code_url + "#readme"}
  };
}

/* plays the five steps one after another. onStep(k, "run" | "done"). returns a cancel function. */
function play(n, onStep, gap){
  gap = gap || 420;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches, timers = [];
  if (reduce){ for (var k = 0; k < n; k++) onStep(k, "done"); return function(){}; }
  for (var j = 0; j < n; j++) (function(k){
    timers.push(setTimeout(function(){ onStep(k, "run"); }, 120 + k * gap));
    timers.push(setTimeout(function(){ onStep(k, "done"); }, 120 + k * gap + gap * 0.8));
  })(j);
  return function(){ timers.forEach(clearTimeout); };
}

/* the tool log speaks in rule codes and iso dates; this turns them into plain words for the screen only */
function clean(s){
  s = String(s == null ? "" : s);
  s = s.replace(/next review (\d{4}-\d{2}-\d{2}) \((-?\d+) days\)/, function(m, d, n){
    n = +n; return "next review " + nice(d) + " (" + (n < 0 ? plural(-n, "day") + " ago" : plural(n, "day")) + ")"; });
  s = s.replace(/\b(\d{4}-\d{2}-\d{2})\b/g, function(m, d){ return nice(d); });
  return s.replace(/blocked by ([a-z0-9_]+(?:,\s*[a-z0-9_]+)*)/g, function(m, codes){
    return "held back (" + codes.split(/,\s*/).map(rlabel).join("; ") + ")"; });
}

/* ---------- shared markup ---------- */

/* the care line opens the brief when the data shows signs of difficulty. it is guidance, not an error,
   so it speaks in petrol and ink, never in the vermilion kept for held back and overdue */
function careHTML(v){
  if (!v.care) return "";
  return '<div class="care" role="note"><p class="care-l">' + esc(v.care.line) + '</p><p class="care-w"><b>Why:</b> ' +
    esc(v.care.signals.join(" ")) + (v.care.note ? ' <span>' + esc(v.care.note) + '</span>' : '') + '</p></div>';
}

/* the follow up draft: closed by default, plain text in a serif block, a copy button and nothing that sends */
function followHTML(v){
  if (!v.followUp) return "";
  return '<section class="fu" aria-labelledby="fu-tog"><button type="button" class="fu-tog" id="fu-tog" aria-expanded="false" aria-controls="fu-body">Follow up draft</button>' +
    '<p class="fu-l">' + esc(v.followUp.label) + '</p><div class="fu-body" id="fu-body" hidden>' +
    '<p class="fu-after" id="fu-after" aria-live="polite">As drafted before the meeting.</p><div class="fu-t" id="fu-t">' + esc(v.followUp.text) + '</div>' +
    '<p class="fu-acts"><button type="button" class="fu-copy" id="fu-copy">Copy text</button><span class="fu-st" id="fu-st" aria-live="polite"></span></p></div></section>';
}
/* shows the draft as it reads after the chosen answer, or the original when no answer is chosen */
function setFollow(v, answer){
  var t = document.getElementById("fu-t"), a = document.getElementById("fu-after"); if (!t || !v.followUp) return;
  t.textContent = answer && answer.follow_up ? answer.follow_up : v.followUp.text;
  a.textContent = answer ? "As it reads if the client says \u201c" + answer.answer + "\u201d." : "As drafted before the meeting.";
}
/* one listener for the toggle and the copy button, on whatever element holds the draft */
function wireFollow(root){
  root.addEventListener("click", function(e){
    var tog = e.target.closest(".fu-tog");
    if (tog){ var open = tog.getAttribute("aria-expanded") !== "true"; tog.setAttribute("aria-expanded", String(open)); document.getElementById("fu-body").hidden = !open; return; }
    if (!e.target.closest(".fu-copy")) return;
    var text = document.getElementById("fu-t").textContent, st = document.getElementById("fu-st");
    var done = function(ok){ st.textContent = ok ? "Copied." : "Select the text to copy it."; setTimeout(function(){ st.textContent = ""; }, 2500); };
    if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(function(){ done(true); }, function(){ done(false); });
    else done(false);
  });
}

function noveltyHTML(F){
  return '<div class="strip-in"><h2 class="strip-h">What this brief does that a recommender does not</h2><ol class="strip-list">' +
    F.novelty.map(function(n){ return '<li><b>' + esc(n.point) + '</b><span>' + esc(n.contrast) + '</span></li>'; }).join("") +
    '</ol><a class="to-model" href="' + F.links.model + '">How the models perform</a></div>';
}

var STATE_ORDER = ["held", "suggested", "in_progress", "held_back", "lower_ranked", "below_threshold", "not_modelled", "not_in_data"];
function holdingsHTML(v){
  var used = {};
  var cats = v.holdings.map(function(c){
    return '<div class="hcat"><span class="hcat-name">' + esc(c.category) + '</span><span class="hchips">' +
      c.products.map(function(p){ used[p.state] = 1;
        var tip = p.state_words + (p.why ? ". " + p.why : "");
        return '<span class="hchip s-' + p.state + '" title="' + esc(tip) + '">' + esc(p.product ? p.label : "Not in this data") + '</span>';
      }).join("") + '</span></div>';
  }).join("");
  var key = STATE_ORDER.filter(function(s){ return used[s]; }).map(function(s){
    return '<span class="hkey"><i class="hchip s-' + s + '"></i>' + esc(window.Field.F.stateWords[s] || s) + '</span>'; }).join("");
  return '<div class="holdings"><h3 class="fh">Products</h3>' + cats + '<div class="hkeys">' + key + '</div></div>';
}

function clientHTML(F, v){
  return '<p class="ref">' + esc(v.ref) + '<span>, meeting on ' + esc(v.meeting) + '</span></p>' +
    /* the segment is the group the client falls in, not a fact about the client, so it says so */
    '<p class="group-l">In the group</p><h1 class="group">' + esc(v.who.name) + '</h1>' +
    '<p class="desc">' + esc(v.who.description) + '.</p>' +
    '<ul class="facts">' + v.who.facts.map(function(f){ return '<li>' + esc(f) + '</li>'; }).join("") + '</ul>' +
    (v.who.changes.length ? '<ul class="changes">' + v.who.changes.map(function(c){ return '<li>' + esc(c.sentence) + '</li>'; }).join("") + '</ul>'
      : '<ul class="changes"><li class="none">No notable changes in the last six months.</li></ul>') +
    holdingsHTML(v);
}

function footerHTML(F){
  var k = F.kpis;
  return '<div class="foot-in"><p class="foot-pitch"><b>' + esc(F.pitch.goal) + '</b> ' + esc(F.pitch.data) + ' ' + esc(F.pitch.result) + '</p>' +
    '<p class="foot-kpi">Across the sample: <b>' + k[0].value + '</b> ' + k[0].label + ', <b>' + k[1].value + '</b> of ' + k[1].of + ' ' + k[1].label +
    ', <b>' + k[2].value + '</b> ' + k[2].label + ', and <b>' + k[3].value + '</b> ' + k[3].label + '.</p>' +
    '<p class="foot-small">Independent prototype for a job application. Not affiliated with or endorsed by Rabobank. Review dates are synthetic. ' +
    '<a href="' + F.links.model + '">How the models perform</a> <a href="' + F.links.notebook + '">Notebook</a> <a href="' + F.links.code + '">Code</a> <a href="' + F.links.home + '">Home</a></p></div>';
}

/* boot: renders the shared parts into #strip, #client and #foot, wires the picker, and calls opts.onClient(view, animate)
   whenever the client changes. sets window.__brief for the screenshot check. */
function boot(opts){
  return fetch(opts.url || "data.json").then(function(r){ if (!r.ok) throw new Error("data.json " + r.status); return r.json(); }).then(function(D){
    var F = make(D); window.Field.F = F;
    var strip = document.getElementById("strip"), client = document.getElementById("client"), foot = document.getElementById("foot");
    if (strip){
      strip.innerHTML = noveltyHTML(F);
      /* the first screen is the strip plus the two fields, so the fields take exactly what the strip leaves */
      var fit = function(){ document.documentElement.style.setProperty("--strip-h", Math.ceil(strip.getBoundingClientRect().height) + "px"); };
      fit(); window.addEventListener("resize", fit);
      if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);
    }
    if (foot) foot.innerHTML = footerHTML(F);
    var cur = F.start;
    function show(i, animate){
      cur = i; var v = F.view(i);
      var sel = document.getElementById("pick"); if (sel) sel.value = String(i);
      var body = document.getElementById("client-body"); if (body) body.innerHTML = clientHTML(F, v);
      if (opts.onClient) opts.onClient(v, animate !== false, F);
    }
    if (client){
      client.insertAdjacentHTML("afterbegin",
        '<p class="lock"><b>Djamel Zair</b>, application for Junior Data Scientist, CLUE</p>' +
        '<div class="pick"><label for="pick">Client</label><select id="pick">' +
        F.clients.map(function(c){ return '<option value="' + c.index + '">' + esc(c.ref + ": " + c.tag) + '</option>'; }).join("") +
        '</select><button type="button" id="another">Show another client</button></div><div id="client-body"></div>');
      document.getElementById("pick").addEventListener("change", function(e){ show(+e.target.value, true); });
      document.getElementById("another").addEventListener("click", function(){ show((cur + 1) % F.count, true); });
    }
    window.__brief = {count: F.count, start: F.start, show: show};
    if (opts.onReady) opts.onReady(F);
    show(F.start, true);
    return F;
  }).catch(function(e){
    console.error(e);
    document.body.insertAdjacentHTML("afterbegin", '<p class="loaderr">This page reads data.json next to it and could not load it. ' +
      'Run python -m http.server 8000 inside docs and open http://localhost:8000/ instead.</p>');
  });
}

window.Field = {boot: boot, make: make, play: play, esc: esc, fmt: fmt, plural: plural, nice: nice, rlabel: rlabel,
                clean: clean, careHTML: careHTML, followHTML: followHTML, setFollow: setFollow, wireFollow: wireFollow,
                load: function(url){ return fetch(url || "data.json").then(function(r){ return r.json(); }).then(make); }};
})();
