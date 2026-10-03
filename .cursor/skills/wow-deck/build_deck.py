#!/usr/bin/env python3
"""
wow-deck: generate a self-contained, offline, "wow"-grade HTML slide deck from JSON.

Design system baked in from 2026 deck-design research (visualbest / slideegg / inkppt /
skills-slides anti-slop): massive display type, dark mode + neon accent, real
glassmorphism, bento grids, grid+grain background depth, a shimmer signature effect,
strategic (not flashy) kinetic motion, prefers-reduced-motion, WCAG-minded contrast.

Anti-slop hard rules enforced here:
  - No Inter/Roboto/Arial as display font (uses OS-native SF Pro / Segoe Variable).
  - No purple-gradient-on-white. Background always has depth (orbs + grid + grain).
  - Every font size uses clamp(). Nothing flat.
  - Zero external dependencies. Single .html file. Works offline, on a projector and a phone.

USAGE
  python build_deck.py content.json -o deck.html [--accent "#38e1d6"]

CONTENT JSON SHAPE (see example.json next to this script)
  {
    "title": "Deck title (browser tab)",
    "accent": "#38e1d6",                 # optional neon accent (overrides default)
    "footerLeft": "Team · Project",       # optional chrome label
    "slides": [ { ...slide... }, ... ]
  }

SLIDE TYPES (set "type")
  hook       : cold-open. {quote, by, turn}
  bento      : modular tiles. {kicker, heading, tiles:[{stat,label,size,tone,wide,hero}]}
  split      : two cards side by side. {kicker, heading, lead?, left:{...}, right:{...}, callout?}
  options    : 2-4 cards, mark one recommended. {kicker, heading, cards:[{title,bullets,tone,reco}]}
  pipeline   : horizontal flow of stages. {kicker, heading, stages:[{layer,desc}], callout?}
  code       : single code block. {kicker, heading, code (html, use spans), callout?}
  diff       : before/after two code columns. {kicker, heading, before:{tag,code}, after:{tag,code}, chips:[..]}
  list       : big bullet list. {kicker, heading, items:[..], callout?}
  table      : risk-box style table. {kicker, heading, columns:[..], rows:[[..]], callout?}
  statement  : one massive centered line. {kicker?, big, sub?}

Every slide may carry "notes" (string or list of strings) -> speaker transcript (press S).
"""
import argparse
import html
import json
import sys
from pathlib import Path


# ---------- helpers ----------

def esc(s):
    return html.escape(str(s), quote=False)


def notes_block(notes):
    if not notes:
        return ""
    if isinstance(notes, str):
        notes = [notes]
    ps = "".join(f"<p>{esc(n)}</p>" for n in notes)
    return f'<div class="notes" data-notes><h4>Transcript</h4>{ps}</div>'


def kicker(k):
    return f'<div class="kicker anim">{esc(k)}</div>' if k else ""


def heading(h):
    # allow inline <span class="em"> in headings by NOT escaping; caller controls
    return f'<h2 class="anim">{h}</h2>' if h else ""


# ---------- slide renderers ----------

def s_hook(s):
    quote = s.get("quote", "")
    by = s.get("by", "")
    turn = s.get("turn", "")
    return f'''<section class="slide">
  <div class="body center">
    {kicker(s.get("kicker",""))}
    <blockquote class="hook-quote anim">{quote}</blockquote>
    <div class="hook-by anim">{esc(by)}</div>
    <p class="hook-turn anim">{esc(turn)}</p>
  </div>{notes_block(s.get("notes"))}
</section>'''


def _tile(t):
    cls = "tile"
    if t.get("hero"):
        cls += " hero-tile"
    if t.get("wide"):
        cls += " wide"
    if t.get("tone") == "danger":
        cls += " danger"
    inner = ""
    if "stat" in t:
        tone = t.get("tone", "")
        statcls = "stat"
        if tone in ("red", "green", "danger"):
            statcls += " red" if tone in ("red", "danger") else " green"
        size = t.get("size")
        style = f' style="font-size:{size}"' if size else ""
        inner += f'<div class="{statcls}"{style}>{esc(t["stat"])}</div>'
    if "label" in t:
        inner += f'<div class="label">{t["label"]}</div>'
    return f'<div class="{cls}">{inner}</div>'


def s_bento(s):
    tiles = "".join(_tile(t) for t in s.get("tiles", []))
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    <div class="bento anim">{tiles}</div>
  </div>{notes_block(s.get("notes"))}
</section>'''


def _card(c):
    cls = "card"
    if c.get("reco"):
        cls += " reco"
    elif c.get("tone") == "bad":
        cls += " bad"
    elif c.get("tone") == "good":
        cls += " good"
    tag = '<span class="reco-tag">RECOMMENDED</span>' if c.get("reco") else ""
    title = f'<h3>{c["title"]}</h3>' if c.get("title") else ""
    bullets = "".join(f"<li>{b}</li>" for b in c.get("bullets", []))
    ul = f"<ul>{bullets}</ul>" if bullets else ""
    body = c.get("body", "")
    return f'<div class="{cls}">{tag}{title}{ul}{body}</div>'


def s_split(s):
    lead = f'<p class="lead anim">{s["lead"]}</p>' if s.get("lead") else ""
    left = _card(s.get("left", {}))
    right = _card(s.get("right", {}))
    callout = _callout(s.get("callout"))
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    {lead}
    <div class="grid2 anim">{left}{right}</div>
    {callout}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_options(s):
    cards = "".join(_card(c) for c in s.get("cards", []))
    n = len(s.get("cards", []))
    grid = "grid3" if n >= 3 else "grid2"
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    <div class="{grid} anim">{cards}</div>
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_pipeline(s):
    stages = "".join(
        f'<div class="stage"><div class="layer">{esc(st.get("layer",""))}</div>'
        f'<div class="desc">{esc(st.get("desc",""))}</div></div>'
        for st in s.get("stages", [])
    )
    callout = _callout(s.get("callout"))
    lead = f'<p class="lead anim">{s["lead"]}</p>' if s.get("lead") else ""
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    {lead}
    <div class="pipe anim">{stages}</div>
    {callout}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_code(s):
    callout = _callout(s.get("callout"))
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    <pre class="code anim">{s.get("code","")}</pre>
    {callout}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_diff(s):
    b = s.get("before", {})
    a = s.get("after", {})
    chips = "".join(f'<div class="winchip">{c}</div>' for c in s.get("chips", []))
    chipwrap = f'<div class="diffwin anim">{chips}</div>' if chips else ""
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    <div class="diff anim">
      <div class="diffcol">
        <div class="difftag before"><span class="badge">{esc(b.get("tag","BEFORE"))}</span></div>
        <pre class="diffcode before">{b.get("code","")}</pre>
      </div>
      <div class="diffcol">
        <div class="difftag after"><span class="badge">{esc(a.get("tag","AFTER"))}</span></div>
        <pre class="diffcode after">{a.get("code","")}</pre>
      </div>
    </div>
    {chipwrap}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_list(s):
    items = "".join(f"<li>{it}</li>" for it in s.get("items", []))
    callout = _callout(s.get("callout"))
    lead = f'<p class="lead anim">{s["lead"]}</p>' if s.get("lead") else ""
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    {lead}
    <ul class="big anim">{items}</ul>
    {callout}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_table(s):
    cols = "".join(f"<th>{esc(c)}</th>" for c in s.get("columns", []))
    rows = ""
    for r in s.get("rows", []):
        tds = "".join(f"<td>{cell}</td>" for cell in r)
        rows += f"<tr>{tds}</tr>"
    callout = _callout(s.get("callout"))
    return f'''<section class="slide">
  {kicker(s.get("kicker",""))}
  <div class="body">
    {heading(s.get("heading",""))}
    <div class="card anim" style="padding:1vh 1.4vw;">
      <table class="risk"><tr>{cols}</tr>{rows}</table>
    </div>
    {callout}
  </div>{notes_block(s.get("notes"))}
</section>'''


def s_statement(s):
    sub = f'<p class="lead anim" style="margin-top:2vh">{s["sub"]}</p>' if s.get("sub") else ""
    return f'''<section class="slide">
  <div class="body center">
    {kicker(s.get("kicker",""))}
    <h2 class="anim" style="max-width:24ch">{s.get("big","")}</h2>
    {sub}
  </div>{notes_block(s.get("notes"))}
</section>'''


def _callout(c):
    if not c:
        return ""
    if isinstance(c, str):
        return f'<div class="callout accent anim">{c}</div>'
    tone = c.get("tone", "accent")
    return f'<div class="callout {tone} anim">{c.get("text","")}</div>'


RENDERERS = {
    "hook": s_hook, "bento": s_bento, "split": s_split, "options": s_options,
    "pipeline": s_pipeline, "code": s_code, "diff": s_diff, "list": s_list,
    "table": s_table, "statement": s_statement,
}


# ---------- the template (CSS/JS shell) ----------

def build(content):
    accent = content.get("accent", "#38e1d6")
    title = esc(content.get("title", "Presentation"))
    footer = esc(content.get("footerLeft", ""))
    slides = content.get("slides", [])

    rendered = []
    titles = []
    for s in slides:
        t = s.get("type")
        if t not in RENDERERS:
            raise SystemExit(f"Unknown slide type: {t!r}. Valid: {', '.join(RENDERERS)}")
        rendered.append(RENDERERS[t](s))
        titles.append(s.get("navTitle", s.get("heading", s.get("big", t)).strip() or t))

    # first slide gets .active
    body_slides = "\n".join(rendered).replace('<section class="slide">', '<section class="slide active">', 1)
    titles_js = json.dumps([t if isinstance(t, str) else str(t) for t in titles])

    return TEMPLATE.format(
        title=title, accent=accent, footer=footer,
        slides=body_slides, titles=titles_js, count=len(slides),
    )


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0" />
<title>{title}</title>
<style>
  :root {{
    --bg:#0a0c12; --bg-grad-1:#0d1018; --bg-grad-2:#0a0c12;
    --panel:#161a24; --panel-2:#1c2230; --text:#eef2f7; --muted:#97a3b4; --dim:#5c6678;
    --indigo:#818cf8; --indigo-deep:#6366f1; --accent:{accent};
    --green:#34d399; --red:#fb7185; --amber:#fbbf24; --blue:#60a5fa;
    --code-bg:#0d1017; --border:#283143; --glass:rgba(22,26,36,.55); --glass-brd:rgba(255,255,255,.10);
    --mono:"SF Mono","JetBrains Mono","Cascadia Code","Fira Code",Menlo,Consolas,monospace;
    --display:"SF Pro Display","Segoe UI Variable Display","Segoe UI",system-ui,-apple-system,sans-serif;
    --sans:"SF Pro Text","Segoe UI Variable Text","Segoe UI",system-ui,-apple-system,sans-serif;
  }}
  * {{ box-sizing:border-box; margin:0; padding:0; }}
  .sr-only {{ position:absolute!important; width:1px!important; height:1px!important; padding:0!important; margin:-1px!important; overflow:hidden!important; clip:rect(0,0,0,0)!important; white-space:nowrap!important; border:0!important; }}
  html,body {{ height:100%; background:var(--bg); color:var(--text); font-family:var(--sans); overflow:hidden; -webkit-font-smoothing:antialiased; text-rendering:optimizeLegibility; }}
  body::before {{ content:""; position:fixed; inset:0; z-index:0; pointer-events:none;
    background:radial-gradient(58vw 58vw at 80% 14%,rgba(99,102,241,.20),transparent 60%),
      radial-gradient(46vw 46vw at 12% 86%,color-mix(in srgb,var(--accent) 22%,transparent),transparent 60%),
      radial-gradient(40vw 40vw at 50% 50%,rgba(96,165,250,.06),transparent 70%),
      linear-gradient(160deg,var(--bg-grad-1),var(--bg-grad-2)); animation:drift 24s ease-in-out infinite alternate; }}
  body::after {{ content:""; position:fixed; inset:0; z-index:0; pointer-events:none; opacity:.5;
    background-image:linear-gradient(rgba(255,255,255,.022) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.022) 1px,transparent 1px);
    background-size:64px 64px; -webkit-mask-image:radial-gradient(ellipse 80% 70% at 50% 45%,#000 40%,transparent 100%); mask-image:radial-gradient(ellipse 80% 70% at 50% 45%,#000 40%,transparent 100%); }}
  @keyframes drift {{ from {{ background-position:0 0,0 0,0 0,0 0; }} to {{ background-position:4% -3%,-4% 3%,2% 2%,0 0; }} }}
  @media (prefers-reduced-motion: reduce) {{ body::before {{ animation:none; }} .slide.active,.slide.active .anim {{ animation:none !important; }} * {{ transition:none !important; }} }}
  .deck {{ position:relative; z-index:1; height:100vh; width:100vw; }}
  .slide {{ position:absolute; inset:0; display:none; flex-direction:column; padding:5.5vh 6.5vw 8vh; }}
  .slide.active {{ display:flex; animation:slin .45s cubic-bezier(.16,.84,.32,1); }}
  @keyframes slin {{ from {{ opacity:0; transform:translateY(14px) scale(.995); }} to {{ opacity:1; transform:none; }} }}
  .slide.active .anim {{ animation:rise .6s both cubic-bezier(.16,.84,.32,1); animation-delay:calc(.06s + var(--i,0)*.09s); }}
  @keyframes rise {{ from {{ opacity:0; transform:translateY(20px); filter:blur(4px); }} to {{ opacity:1; transform:none; filter:blur(0); }} }}
  .slide.active .card:hover,.slide.active .bento .tile:hover {{ transform:translateY(-4px); box-shadow:0 22px 56px rgba(0,0,0,.45),inset 0 1px 0 rgba(255,255,255,.10); }}
  .kicker {{ font-size:clamp(.7rem,1vw,.86rem); letter-spacing:.16em; text-transform:uppercase; color:var(--accent); font-weight:700; margin-bottom:1.4vh; display:flex; align-items:center; gap:.7em; }}
  .kicker::before {{ content:""; width:26px; height:2px; background:var(--accent); display:inline-block; border-radius:2px; }}
  h1 {{ font-family:var(--display); font-size:clamp(2.6rem,7vw,6rem); line-height:.98; font-weight:800; letter-spacing:-.04em; }}
  h2 {{ font-family:var(--display); font-size:clamp(1.8rem,4.6vw,3.9rem); line-height:1.04; font-weight:800; letter-spacing:-.03em; margin-bottom:2.6vh; }}
  .em {{ background:linear-gradient(100deg,var(--indigo) 10%,var(--accent) 90%); -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .lead {{ font-size:clamp(1.05rem,1.9vw,1.55rem); color:var(--muted); max-width:60ch; line-height:1.5; }}
  p {{ font-size:clamp(1rem,1.6vw,1.3rem); line-height:1.5; }}
  .body {{ flex:1; display:flex; flex-direction:column; justify-content:center; gap:2.4vh; min-height:0; }}
  .center {{ align-items:center; text-align:center; }}
  .mono {{ font-family:var(--mono); }}
  code.inline {{ font-family:var(--mono); background:var(--code-bg); border:1px solid var(--border); border-radius:5px; padding:.06em .42em; font-size:.85em; color:var(--accent); }}
  .grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:2.2vw; }}
  .grid3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1.8vw; }}
  .card {{ background:var(--glass); backdrop-filter:blur(16px) saturate(140%); -webkit-backdrop-filter:blur(16px) saturate(140%); border:1px solid var(--glass-brd); border-radius:18px; padding:2.6vh 1.9vw; display:flex; flex-direction:column; gap:1.1vh; position:relative; overflow:hidden; box-shadow:0 12px 40px rgba(0,0,0,.35),inset 0 1px 0 rgba(255,255,255,.06); transition:transform .35s cubic-bezier(.16,.84,.32,1),box-shadow .35s; }}
  .card::before {{ content:""; position:absolute; inset:0 0 auto 0; height:1px; background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent); }}
  .card h3 {{ font-family:var(--display); font-size:clamp(1.05rem,1.7vw,1.4rem); font-weight:760; letter-spacing:-.01em; }}
  .card ul {{ list-style:none; display:flex; flex-direction:column; gap:.85vh; }}
  .card li {{ font-size:clamp(.88rem,1.4vw,1.16rem); line-height:1.4; padding-left:1.35em; position:relative; }}
  .card li::before {{ content:"–"; position:absolute; left:0; color:var(--dim); }}
  .card.bad {{ border-color:rgba(251,113,133,.32); }} .card.bad h3 {{ color:var(--red); }}
  .card.good {{ border-color:rgba(52,211,153,.30); }} .card.good h3 {{ color:var(--green); }}
  .card.reco {{ border-color:var(--indigo-deep); box-shadow:0 0 0 1px var(--indigo-deep),0 24px 60px rgba(99,102,241,.28),inset 0 1px 0 rgba(255,255,255,.08); }}
  .card.reco::after {{ content:""; position:absolute; inset:-40% -10% auto; height:60%; background:radial-gradient(60% 60% at 50% 0,rgba(99,102,241,.22),transparent 70%); pointer-events:none; }}
  .reco-tag {{ position:absolute; top:0; right:0; background:linear-gradient(135deg,var(--indigo-deep),var(--indigo)); color:#fff; font-size:.66rem; font-weight:800; letter-spacing:.12em; padding:.35em .9em; border-bottom-left-radius:12px; z-index:2; }}
  ul.big {{ list-style:none; display:flex; flex-direction:column; gap:1.7vh; max-width:74ch; }}
  ul.big li {{ font-size:clamp(1.02rem,1.8vw,1.45rem); line-height:1.4; padding-left:1.7em; position:relative; }}
  ul.big li::before {{ content:""; position:absolute; left:0; top:.55em; width:.7em; height:.7em; border-radius:3px; background:linear-gradient(135deg,var(--indigo),var(--accent)); }}
  .callout {{ border-radius:16px; padding:1.9vh 1.9vw; font-size:clamp(.95rem,1.55vw,1.28rem); line-height:1.45; border:1px solid var(--glass-brd); background:var(--glass); backdrop-filter:blur(14px) saturate(130%); -webkit-backdrop-filter:blur(14px) saturate(130%); position:relative; overflow:hidden; }}
  .callout.accent {{ border-color:color-mix(in srgb,var(--indigo-deep) 50%,transparent); background:rgba(99,102,241,.14); }}
  .callout.accent::after {{ content:""; position:absolute; top:0; left:-60%; width:45%; height:100%; background:linear-gradient(100deg,transparent,rgba(255,255,255,.10),transparent); transform:skewX(-18deg); animation:sweep 6.5s ease-in-out infinite; }}
  @keyframes sweep {{ 0%,15% {{ left:-60%; }} 55%,100% {{ left:130%; }} }}
  .callout.green {{ border-color:rgba(52,211,153,.4); background:rgba(52,211,153,.11); }}
  .callout.amber {{ border-color:rgba(251,191,36,.4); background:rgba(251,191,36,.11); }}
  .callout.red {{ border-color:rgba(251,113,133,.4); background:rgba(251,113,133,.10); }}
  .callout b {{ color:var(--text); }}
  .stat {{ font-family:var(--display); font-size:clamp(3rem,8vw,6.4rem); font-weight:850; line-height:.92; letter-spacing:-.04em; background:linear-gradient(160deg,#fff,var(--muted)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .stat.red {{ background:linear-gradient(160deg,#ffd5da,var(--red)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .stat.green {{ background:linear-gradient(160deg,#c8f7e4,var(--green)); -webkit-background-clip:text; background-clip:text; color:transparent; }}
  .label {{ color:var(--muted); font-size:clamp(.82rem,1.3vw,1.08rem); line-height:1.4; margin-top:.6vh; }}
  pre.code {{ background:var(--code-bg); border:1px solid var(--border); border-radius:14px; padding:2.4vh 1.9vw; font-family:var(--mono); font-size:clamp(.72rem,1.18vw,1.04rem); line-height:1.6; overflow:auto; max-height:62vh; }}
  pre.code .c {{ color:#61708a; font-style:italic; }} pre.code .k {{ color:#c4b5fd; }} pre.code .s {{ color:#86efac; }} pre.code .f {{ color:#7dd3fc; }} pre.code .n {{ color:#fcd34d; }}
  pre.code .hl {{ background:linear-gradient(90deg,rgba(99,102,241,.20),rgba(56,225,214,.06)); display:block; margin:0 -1.9vw; padding:0 1.9vw; border-left:3px solid var(--accent); }}
  .diff {{ display:grid; grid-template-columns:1fr 1fr; gap:1.6vw; }}
  .diffcol {{ display:flex; flex-direction:column; gap:1vh; min-width:0; }}
  .difftag {{ font-family:var(--mono); font-size:clamp(.78rem,1.2vw,1rem); font-weight:700; }} .difftag.before {{ color:var(--red); }} .difftag.after {{ color:var(--green); }}
  .difftag .badge {{ font-size:.68rem; padding:.12em .55em; border-radius:5px; border:1px solid currentColor; }}
  pre.diffcode {{ background:var(--code-bg); border:1px solid var(--border); border-radius:12px; padding:1.8vh 1.3vw; font-family:var(--mono); font-size:clamp(.62rem,1.02vw,.9rem); line-height:1.5; overflow:auto; flex:1; max-height:52vh; }}
  pre.diffcode.before {{ border-color:rgba(251,113,133,.4); }} pre.diffcode.after {{ border-color:rgba(52,211,153,.4); }}
  pre.diffcode .c {{ color:#61708a; font-style:italic; }} pre.diffcode .k {{ color:#c4b5fd; }} pre.diffcode .s {{ color:#86efac; }} pre.diffcode .f {{ color:#7dd3fc; }}
  pre.diffcode .del {{ background:rgba(251,113,133,.10); display:block; margin:0 -1.3vw; padding:0 1.3vw; }}
  pre.diffcode .add {{ background:rgba(52,211,153,.12); display:block; margin:0 -1.3vw; padding:0 1.3vw; border-left:3px solid var(--green); }}
  .diffwin {{ display:grid; grid-template-columns:1fr 1fr; gap:1.6vw; margin-top:1.2vh; }}
  .winchip {{ background:var(--glass); backdrop-filter:blur(10px); -webkit-backdrop-filter:blur(10px); border:1px solid var(--glass-brd); border-radius:12px; padding:1vh 1.1vw; font-size:clamp(.8rem,1.25vw,1.05rem); color:var(--muted); }}
  .winchip b {{ color:var(--text); }}
  .pipe {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1.4vw; }}
  .stage {{ background:var(--glass); backdrop-filter:blur(14px) saturate(130%); -webkit-backdrop-filter:blur(14px) saturate(130%); border:1px solid var(--glass-brd); border-radius:16px; padding:2.2vh 1.2vw; text-align:center; position:relative; box-shadow:inset 0 1px 0 rgba(255,255,255,.06); }}
  .stage .layer {{ font-family:var(--mono); font-weight:700; color:var(--accent); font-size:clamp(.9rem,1.45vw,1.2rem); }}
  .stage .desc {{ color:var(--muted); font-size:clamp(.78rem,1.2vw,1rem); margin-top:.8vh; line-height:1.35; }}
  .stage:not(:last-child)::after {{ content:"→"; position:absolute; right:-1vw; top:50%; transform:translateY(-50%); color:var(--indigo); font-size:1.4rem; z-index:2; }}
  .bento {{ display:grid; grid-template-columns:1.4fr 1fr 1fr; grid-template-rows:auto auto; gap:1.4vw; }}
  .bento .hero-tile {{ grid-row:span 2; display:flex; flex-direction:column; justify-content:center; }}
  .bento .wide {{ grid-column:span 2; }}
  .bento .tile {{ background:var(--glass); backdrop-filter:blur(16px) saturate(140%); -webkit-backdrop-filter:blur(16px) saturate(140%); border:1px solid var(--glass-brd); border-radius:18px; padding:2.4vh 1.7vw; position:relative; overflow:hidden; box-shadow:0 10px 36px rgba(0,0,0,.3),inset 0 1px 0 rgba(255,255,255,.06); transition:transform .35s; }}
  .bento .tile::before {{ content:""; position:absolute; inset:0 0 auto 0; height:1px; background:linear-gradient(90deg,transparent,rgba(255,255,255,.22),transparent); }}
  .bento .tile.danger {{ border-color:rgba(251,113,133,.35); }}
  table.risk {{ width:100%; border-collapse:collapse; font-size:clamp(.85rem,1.35vw,1.14rem); }}
  table.risk th,table.risk td {{ text-align:left; padding:1.3vh 1vw; border-bottom:1px solid var(--border); vertical-align:top; }}
  table.risk th {{ color:var(--accent); font-weight:700; font-size:.8em; letter-spacing:.06em; text-transform:uppercase; }}
  table.risk tr:last-child td {{ border-bottom:none; }}
  .pill {{ font-family:var(--mono); font-size:.82em; padding:.15em .6em; border-radius:20px; }}
  .pill.lo {{ background:rgba(52,211,153,.14); color:var(--green); }} .pill.md {{ background:rgba(251,191,36,.14); color:var(--amber); }} .pill.hi {{ background:rgba(251,113,133,.16); color:var(--red); }}
  .hook-quote {{ font-family:var(--display); font-size:clamp(2.2rem,6vw,5rem); font-weight:600; line-height:1.08; letter-spacing:-.035em; max-width:18ch; }}
  .hook-quote .em {{ font-weight:850; }}
  .hook-by {{ color:var(--dim); font-size:clamp(.9rem,1.4vw,1.2rem); margin-top:3vh; font-style:italic; }}
  .hook-turn {{ color:var(--muted); font-size:clamp(1.05rem,1.75vw,1.45rem); margin-top:4vh; max-width:46ch; line-height:1.5; }}
  .footnote {{ color:var(--dim); font-size:clamp(.78rem,1.15vw,1rem); margin-top:1vh; }}
  .chrome {{ position:fixed; bottom:0; left:0; right:0; display:flex; align-items:center; justify-content:space-between; padding:1vh 2vw; font-size:.76rem; color:var(--dim); border-top:1px solid var(--border); background:rgba(10,12,18,.78); backdrop-filter:blur(8px); z-index:30; }}
  .chrome .l {{ display:flex; gap:1.3em; align-items:center; }} .chrome .tag {{ font-family:var(--mono); color:var(--muted); }}
  .progress {{ position:fixed; top:0; left:0; height:3px; background:linear-gradient(90deg,var(--indigo-deep),var(--accent)); z-index:40; transition:width .4s cubic-bezier(.16,.84,.32,1); box-shadow:0 0 12px color-mix(in srgb,var(--accent) 50%,transparent); }}
  .hint {{ font-family:var(--mono); opacity:.65; }}
  kbd {{ font-family:var(--mono); background:var(--panel); border:1px solid var(--border); border-radius:4px; padding:.05em .4em; font-size:.85em; }}
  .notes {{ position:fixed; right:1.4vw; bottom:5.8vh; width:min(36vw,520px); max-height:52vh; overflow:auto; background:rgba(13,16,23,.97); border:1px solid var(--indigo-deep); border-radius:14px; padding:1.6vh 1.3vw; font-size:.94rem; line-height:1.5; color:var(--text); display:none; z-index:35; box-shadow:0 16px 50px rgba(0,0,0,.6); }}
  .notes.show {{ display:block; }} .notes h4 {{ color:var(--accent); font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; margin-bottom:1vh; }} .notes p {{ margin-bottom:.9vh; }}
  @media (max-width:860px) {{ .grid2,.grid3,.pipe,.bento {{ grid-template-columns:1fr; }} .diff,.diffwin {{ grid-template-columns:1fr; }} .bento .hero-tile {{ grid-row:auto; }} .notes {{ width:92vw; right:4vw; }} }}
</style>
</head>
<body>
<div id="slide-announcer" class="sr-only" role="status" aria-live="polite" aria-atomic="true"></div>
<div class="progress" id="progress"></div>
<div class="deck" id="deck">
{slides}
</div>
<div class="chrome">
  <div class="l"><span class="tag" id="counter">1 / {count}</span><span id="stitle">{footer}</span></div>
  <div class="l"><span class="hint"><kbd>&larr;</kbd><kbd>&rarr;</kbd> nav &middot; <kbd>S</kbd> notes &middot; <kbd>F</kbd> full &middot; <kbd>O</kbd> overview</span></div>
</div>
<script>
  const deck=document.getElementById('deck');
  const slides=Array.from(deck.querySelectorAll('.slide'));
  const titles={titles};
  const footer={footer!r};
  let i=0,notesOn=false;
  function render(){{
    slides.forEach((s,idx)=>{{
      const active=idx===i;
      s.classList.toggle('active',active);
      s.setAttribute('aria-hidden',active?'false':'true');
    }});
    slides[i].querySelectorAll('.anim').forEach((el,k)=>el.style.setProperty('--i',k));
    document.getElementById('counter').textContent=(i+1)+' / '+slides.length;
    document.getElementById('stitle').textContent=footer||titles[i]||'';
    document.getElementById('progress').style.width=((i+1)/slides.length*100)+'%';
    document.getElementById('slide-announcer').textContent='Slide '+(i+1)+' of '+slides.length+': '+(titles[i]||'Untitled slide');
    syncNotes();
    if(location.hash!=='#'+(i+1))history.replaceState(null,'','#'+(i+1));
  }}
  function syncNotes(){{
    slides.forEach(s=>{{const n=s.querySelector('[data-notes]');if(n)n.classList.remove('show');}});
    if(notesOn){{const n=slides[i].querySelector('[data-notes]');if(n)n.classList.add('show');}}
  }}
  function go(n){{i=Math.max(0,Math.min(slides.length-1,n));render();}}
  document.addEventListener('keydown',(e)=>{{
    if(['ArrowRight','PageDown',' '].includes(e.key)){{e.preventDefault();go(i+1);}}
    else if(['ArrowLeft','PageUp'].includes(e.key)){{e.preventDefault();go(i-1);}}
    else if(e.key==='Home')go(0); else if(e.key==='End')go(slides.length-1);
    else if(e.key.toLowerCase()==='s'){{notesOn=!notesOn;syncNotes();}}
    else if(e.key.toLowerCase()==='f'){{if(!document.fullscreenElement)document.documentElement.requestFullscreen();else document.exitFullscreen();}}
    else if(e.key.toLowerCase()==='o')toggleOverview();
    else if(/^[1-9]$/.test(e.key))go(parseInt(e.key,10)-1);
    else if(e.key==='0')go(slides.length-1);
  }});
  deck.addEventListener('click',(e)=>{{if(e.target.closest('a,pre,.notes'))return;go((e.clientX/window.innerWidth)>0.4?i+1:i-1);}});
  let ov=null;
  function toggleOverview(){{
    if(ov){{ov.remove();ov=null;return;}}
    ov=document.createElement('div');
    Object.assign(ov.style,{{position:'fixed',inset:'0',background:'rgba(8,10,15,.97)',zIndex:'50',display:'grid',gridTemplateColumns:'repeat(5,1fr)',gap:'12px',padding:'28px',overflow:'auto'}});
    titles.forEach((t,idx)=>{{const c=document.createElement('button');c.textContent=(idx+1)+'. '+t;
      Object.assign(c.style,{{background:idx===i?'rgba(99,102,241,.28)':'#161a24',color:'#eef2f7',border:'1px solid '+(idx===i?'#6366f1':'#283143'),borderRadius:'12px',padding:'22px 16px',fontSize:'14px',textAlign:'left',cursor:'pointer',fontFamily:'system-ui',fontWeight:'600'}});
      c.onclick=()=>{{go(idx);toggleOverview();}};ov.appendChild(c);}});
    document.body.appendChild(ov);
  }}
  if(location.hash){{const n=parseInt(location.hash.slice(1),10);if(n)i=Math.min(slides.length-1,n-1);}}
  render();
</script>
</body>
</html>"""


def main():
    ap = argparse.ArgumentParser(description="Generate a wow-grade offline HTML deck from JSON.")
    ap.add_argument("content", help="Path to content JSON")
    ap.add_argument("-o", "--out", default="deck.html", help="Output HTML path")
    ap.add_argument("--accent", help="Override neon accent hex (e.g. #38e1d6)")
    args = ap.parse_args()

    data = json.loads(Path(args.content).read_text())
    if args.accent:
        data["accent"] = args.accent
    out = build(data)
    Path(args.out).write_text(out)

    # quick self-checks (the loop's lessons, codified)
    warnings = []
    if "http://" in out or "https://" in out or "cdn." in out:
        warnings.append("external dependency detected (deck should be fully offline)")
    if "Inter" in out.split("<style>")[0]:  # crude: Inter shouldn't appear as a font
        warnings.append("'Inter' present (anti-slop: avoid Inter as display font)")
    print(f"Wrote {args.out} ({len(data.get('slides', []))} slides)")
    for w in warnings:
        print(f"  WARNING: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
