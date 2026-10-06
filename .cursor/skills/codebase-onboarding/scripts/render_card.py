#!/usr/bin/env python3
"""Render a Teaching Card (JSON) into a self-contained dark-themed HTML file.

Why this exists: generating full HTML/CSS inline in chat burns thousands of
tokens per card and drifts in style. Instead the agent emits only the card
*content* as compact JSON; this script owns all the layout, styling, collapsible
answers, and diagram rendering. Reusable, deterministic, offline by default.

Usage:
    python render_card.py card.json                 # -> ~/teach-cards/<slug>-<date>.html
    python render_card.py card.json -o out.html     # explicit output path
    cat card.json | python render_card.py -         # read JSON from stdin
    python render_card.py --schema                  # print the JSON contract + example
    python render_card.py card.json --open          # also open in default browser

Stdlib only. No pip installs. Mermaid diagrams pull mermaid.js from a CDN
(needs internet) only when a `mermaid` picture is present; ASCII/table pictures
are fully offline.
"""

# flake8: noqa: E501
#   Embedded CSS/HTML string literals are intentionally long; line-length
#   wrapping them hurts readability for zero functional gain.

import argparse
import datetime as _dt
import html
import json
import re
import sys
import webbrowser
from pathlib import Path

EXAMPLE = {
    "topic": "Idempotency keys",
    "audience": "backend engineers",
    "one_liner": "An idempotency key is a 'you already asked me this' tag on a request, so a retry does the work once and replays the same answer instead of charging twice.",
    "analogy": {
        "text": "A coat-check ticket: hand over your coat, get ticket 42; ask for 'the coat for 42' ten times and you get the same one coat back.",
        "seam": "A coat check assumes your coat already exists; an idempotency key must also handle the first request still being in-flight when the duplicate arrives.",
    },
    "picture": {
        "type": "mermaid",
        "content": "flowchart TD\n  A[Request + key abc] --> B{Seen abc?}\n  B -- no --> C[Do work once]\n  C --> D[Store result]\n  B -- yes --> E[Replay stored result]",
        "caption": "First request does the work; duplicates replay the stored result.",
    },
    "how_it_works": {
        "intro": "Trace one $50 charge that gets retried after a network hiccup.",
        "steps": [
            "Client sends `POST /charge` with header `Idempotency-Key: abc-123`.",
            "Network drops the response, so the client retries the exact same request with the same key.",
            "Server sees `abc-123` is new, charges the card once, stores `{charge_id: ch_9}` under the key.",
            "The retry finds `abc-123` done and replays `ch_9`. Customer charged once.",
        ],
    },
    "depth_ladder": {
        "eli5": "A sticker that says 'if you've seen this before, don't do it again, just tell me what happened last time.'",
        "practitioner": "Client generates one stable key per operation and resends it on retries; server stores key -> response and replays on repeat.",
        "expert": "Correctness hinges on an atomic check-and-set. A naive check-then-write races: two duplicates both read 'not found' and both charge.",
    },
    "curveballs": [
        {
            "lens": "Boundary",
            "question": "What if two duplicates arrive in the same millisecond, before the first finishes?",
            "answer": "A plain check-then-write double-charges. You need an atomic reservation (unique-constraint insert / SETNX); the loser gets 409 or waits.",
        },
        {
            "lens": "Why-not-X",
            "question": "Why not dedupe on amount + card + timestamp instead?",
            "answer": "Legitimate identical charges exist and timestamps drift on retries. A client key encodes intent, which content-matching can't infer.",
        },
    ],
    "check_yourself": [
        {
            "q": "A retry arrives while the original is still processing. What must the server do, and what bug appears with a naive check-then-write?",
            "a": "Atomically reserve the key first; the duplicate loses and waits or 409s. Check-then-write races and double-charges.",
        }
    ],
    "teach_back": "An idempotency key is a client tag that makes retries safe: first time the server does the work and stores the result under the key; every later request with that key replays the stored result. The whole game is the in-flight race, so you reserve the key atomically before doing the work.",
    "grounding": "Payments-flavored example; mechanics standard across Stripe/PayPal-style idempotency.",
}


# ---------- inline formatting ----------

def _fmt(text):
    """Escape HTML, then support `code` and **bold** inline."""
    if text is None:
        return ""
    text = html.escape(str(text))
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def _pre(text):
    return html.escape(str(text or ""))


def _slug(text):
    s = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return s or "teaching-card"


# ---------- section renderers ----------

# ---------- SVG diagram engine (beautiful, offline, token-cheap) ----------
# The agent supplies a compact structured spec; these generators own the SVG.

_SVG_BG = "#0b0f16"
_SVG_NODE = "#1c2230"
_SVG_STROKE = "#31415a"
_SVG_INK = "#e6edf3"
_SVG_MUTED = "#9aa7b5"
_SVG_ACCENT = "#4ade80"
_SVG_ACCENT2 = "#38bdf8"
_SVG_WARN = "#fbbf24"
_MARKER_SEQ = [0]

_SHAPE_COLOR = {
    "box": _SVG_STROKE,
    "pill": _SVG_ACCENT,
    "diamond": _SVG_WARN,
    "cloud": _SVG_MUTED,
}


def _wrap(text, max_chars):
    words = str(text).split()
    lines, cur = [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > max_chars:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    if cur:
        lines.append(cur)
    return lines or [""]


def _svg_text(cx, cy, lines, size=13, color=None, weight="500"):
    color = color or _SVG_INK
    n = len(lines)
    y0 = cy - (n - 1) * (size + 3) / 2
    spans = []
    for i, ln in enumerate(lines):
        spans.append(
            f'<text x="{cx:.1f}" y="{y0 + i * (size + 3):.1f}" fill="{color}" '
            f'font-size="{size}" font-weight="{weight}" text-anchor="middle" '
            f'dominant-baseline="middle" font-family="-apple-system,Segoe UI,Roboto,sans-serif">'
            f"{html.escape(ln)}</text>"
        )
    return "".join(spans)


def _rect_border(cx, cy, w, h, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    hw, hh = w / 2, h / 2
    sx = hw / abs(dx) if dx else float("inf")
    sy = hh / abs(dy) if dy else float("inf")
    s = min(sx, sy)
    return cx + dx * s, cy + dy * s


def _node_shape(shape, cx, cy, w, h, color):
    if shape == "diamond":
        pts = f"{cx:.1f},{cy - h/2:.1f} {cx + w/2:.1f},{cy:.1f} {cx:.1f},{cy + h/2:.1f} {cx - w/2:.1f},{cy:.1f}"
        return f'<polygon points="{pts}" fill="{_SVG_NODE}" stroke="{color}" stroke-width="1.5"/>'
    if shape == "cloud":
        return (
            f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{w/2:.1f}" ry="{h/2:.1f}" '
            f'fill="{_SVG_NODE}" stroke="{color}" stroke-width="1.5" stroke-dasharray="4 3"/>'
        )
    rx = h / 2 if shape == "pill" else 12
    return (
        f'<rect x="{cx - w/2:.1f}" y="{cy - h/2:.1f}" width="{w:.1f}" height="{h:.1f}" '
        f'rx="{rx:.1f}" fill="{_SVG_NODE}" stroke="{color}" stroke-width="1.5"/>'
    )


def _svg_shell(inner, w, h):
    mid = _MARKER_SEQ[0]
    _MARKER_SEQ[0] += 1
    marker = (
        f'<marker id="ah{mid}" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{_SVG_MUTED}"/></marker>'
    )
    return (
        f'<svg viewBox="0 0 {w:.0f} {h:.0f}" width="100%" '
        f'style="max-width:{w:.0f}px;height:auto" xmlns="http://www.w3.org/2000/svg">'
        f"<defs>{marker}</defs>"
        f'<rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" rx="12" fill="{_SVG_BG}"/>'
        f"{inner}</svg>",
        f"ah{mid}",
    )


def _edge_label(mx, my, text):
    if not text:
        return ""
    w = len(text) * 7 + 12
    return (
        f'<rect x="{mx - w/2:.1f}" y="{my - 10:.1f}" width="{w}" height="20" rx="6" '
        f'fill="{_SVG_BG}" stroke="{_SVG_STROKE}"/>'
        f'<text x="{mx:.1f}" y="{my:.1f}" fill="{_SVG_MUTED}" font-size="11" '
        f'text-anchor="middle" dominant-baseline="middle" '
        f'font-family="-apple-system,Segoe UI,sans-serif">{html.escape(text)}</text>'
    )


def _edge_path(a, b):
    """Orthogonal (elbow) routing between two node boxes. a,b = (cx,cy,w,h)."""
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    if abs(ax - bx) < 1:  # vertical neighbor -> straight
        down = by > ay
        y1 = ay + ah / 2 if down else ay - ah / 2
        y2 = by - bh / 2 if down else by + bh / 2
        return f"M{ax:.1f},{y1:.1f} L{bx:.1f},{y2:.1f}", (ax, (y1 + y2) / 2)
    if abs(ay - by) < 1:  # same row -> straight horizontal
        right = bx > ax
        x1 = ax + aw / 2 if right else ax - aw / 2
        x2 = bx - bw / 2 if right else bx + bw / 2
        return f"M{x1:.1f},{ay:.1f} L{x2:.1f},{by:.1f}", ((x1 + x2) / 2, ay - 2)
    # different row and col -> vertical, then across, then into target
    down = by > ay
    y1 = ay + ah / 2 if down else ay - ah / 2
    y2 = by - bh / 2 if down else by + bh / 2
    my = (y1 + y2) / 2
    d = f"M{ax:.1f},{y1:.1f} L{ax:.1f},{my:.1f} L{bx:.1f},{my:.1f} L{bx:.1f},{y2:.1f}"
    return d, ((ax + bx) / 2, my)


def _render_orderbook(pic):
    asks = sorted(pic.get("asks", []) or [], key=lambda r: -float(r[0]))
    bids = sorted(pic.get("bids", []) or [], key=lambda r: -float(r[0]))
    if not asks and not bids:
        return ""
    sizes = [float(r[1]) for r in asks + bids] or [1.0]
    maxs = max(sizes) or 1.0
    P, row_h, price_w, bar_max, size_w, gap = 16, 30, 66, 234, 52, 10
    x_price = P + price_w
    x_bar = x_price + gap
    w = x_bar + bar_max + gap + size_w + P
    rows = len(asks) + (1 if asks and bids else 0) + len(bids)
    h = P + rows * row_h + P
    body = []

    def _row(y, price, size, color, best):
        bw = max(3.0, bar_max * (float(size) / maxs))
        op = "0.34" if best else "0.20"
        weight = "700" if best else "500"
        seg = [
            f'<rect x="{x_bar}" y="{y + 5:.1f}" width="{bw:.1f}" height="{row_h - 10}" '
            f'rx="4" fill="{color}" fill-opacity="{op}" stroke="{color}" stroke-opacity="0.85"/>',
            f'<text x="{x_price}" y="{y + row_h / 2:.1f}" fill="{color}" font-size="13.5" '
            f'font-weight="{weight}" text-anchor="end" dominant-baseline="middle" '
            f'font-family="ui-monospace,Menlo,monospace">{float(price):.2f}</text>',
            f'<text x="{x_bar + bar_max + gap}" y="{y + row_h / 2:.1f}" fill="{_SVG_MUTED}" '
            f'font-size="12" text-anchor="start" dominant-baseline="middle" '
            f'font-family="ui-monospace,Menlo,monospace">&#215;{int(float(size))}</text>',
        ]
        if best:
            seg.append(
                f'<circle cx="{P + 5}" cy="{y + row_h / 2:.1f}" r="3.5" fill="{color}"/>'
            )
        return "".join(seg)

    y = P
    for i, (p, s) in enumerate(asks):
        body.append(_row(y, p, s, "#f87171", best=(i == len(asks) - 1)))
        y += row_h
    if asks and bids:
        spread = float(asks[-1][0]) - float(bids[0][0])
        lbl = pic.get("spread_label") or f"spread {spread:.2f}"
        body.append(
            f'<rect x="{P}" y="{y + 4:.1f}" width="{w - 2 * P}" height="{row_h - 8}" rx="5" '
            f'fill="#132433" stroke="{_SVG_ACCENT2}" stroke-opacity="0.55"/>'
            f'<text x="{w / 2:.1f}" y="{y + row_h / 2:.1f}" fill="{_SVG_ACCENT2}" font-size="11.5" '
            f'text-anchor="middle" dominant-baseline="middle" letter-spacing="1.2" '
            f'font-family="-apple-system,Segoe UI,sans-serif">{html.escape(lbl.upper())}</text>'
        )
        y += row_h
    for i, (p, s) in enumerate(bids):
        body.append(_row(y, p, s, "#4ade80", best=(i == 0)))
        y += row_h
    svg, _ = _svg_shell("".join(body), w, h)
    return svg


def _render_queue_spread(pic):
    """Two sorted queues facing a clerk at the spread — the core matching metaphor."""
    bids = sorted(pic.get("bids", []) or [], key=lambda r: -float(r[0]))
    asks = sorted(pic.get("asks", []) or [], key=lambda r: float(r[0]))
    if not bids or not asks:
        return ""
    depth = min(3, len(bids), len(asks))
    best_bid = float(bids[0][0])
    best_ask = float(asks[0][0])
    spread = best_ask - best_bid
    crosses = pic.get("crosses", best_bid >= best_ask)
    lbl = pic.get("spread_label") or f"spread {spread:.2f}"

    w, h = 720, 300
    cy = h / 2 + 8
    row_h = 46
    # zones
    lx, cx, rx = 24, w / 2, w - 24
    box_w, box_h = 118, 36
    body = []

    # column headers
    body.append(
        f'<text x="{lx + 90}" y="34" fill="{_SVG_ACCENT}" font-size="11" '
        f'text-anchor="middle" letter-spacing="1" font-weight="700" '
        f'font-family="-apple-system,sans-serif">BUYERS</text>'
        f'<text x="{lx + 90}" y="50" fill="{_SVG_MUTED}" font-size="10" '
        f'text-anchor="middle" font-family="-apple-system,sans-serif">highest bid in front</text>'
        f'<text x="{rx - 90}" y="34" fill="#f87171" font-size="11" '
        f'text-anchor="middle" letter-spacing="1" font-weight="700" '
        f'font-family="-apple-system,sans-serif">SELLERS</text>'
        f'<text x="{rx - 90}" y="50" fill="{_SVG_MUTED}" font-size="10" '
        f'text-anchor="middle" font-family="-apple-system,sans-serif">lowest ask in front</text>'
    )

    def _queue_box(x, y, price, size, side, front, fade):
        color = _SVG_ACCENT if side == "bid" else "#f87171"
        op = "1" if front else ("0.55" if fade == 1 else "0.28")
        stroke = "2.5" if front else "1.2"
        is_bid = side == "bid"
        rx = x - box_w if is_bid else x
        tx = x - 8 if is_bid else x + 8
        anchor = "end" if is_bid else "start"
        body.append(
            f'<rect x="{rx:.1f}" y="{y - box_h/2:.1f}" width="{box_w}" height="{box_h}" '
            f'rx="8" fill="{_SVG_NODE}" stroke="{color}" stroke-width="{stroke}" opacity="{op}"/>'
            f'<text x="{tx:.1f}" y="{y - 4:.1f}" fill="{color}" font-size="13" '
            f'font-weight="{"700" if front else "500"}" text-anchor="{anchor}" '
            f'dominant-baseline="middle" font-family="ui-monospace,Menlo,monospace">'
            f"{price:.2f}</text>"
            f'<text x="{tx:.1f}" y="{y + 12:.1f}" fill="{_SVG_MUTED}" font-size="10" '
            f'text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-family="ui-monospace,monospace">&#215;{int(size)}</text>'
        )
        if front:
            fx = x - box_w / 2 if is_bid else x + box_w / 2
            body.append(
                f'<text x="{fx:.1f}" y="{y + box_h/2 + 14:.1f}" fill="{color}" '
                f'font-size="9" font-weight="700" text-anchor="middle" letter-spacing="0.8" '
                f'font-family="-apple-system,sans-serif">FRONT</text>'
            )

    # center clerk / spread band
    band_w, band_h = 108, 52
    body.append(
        f'<rect x="{cx - band_w/2:.1f}" y="{cy - band_h/2:.1f}" width="{band_w}" height="{band_h}" '
        f'rx="10" fill="#132433" stroke="{_SVG_ACCENT2}" stroke-width="2"/>'
        f'<text x="{cx:.1f}" y="{cy - 6:.1f}" fill="{_SVG_ACCENT2}" font-size="10" '
        f'text-anchor="middle" letter-spacing="1.2" font-weight="700" '
        f'font-family="-apple-system,sans-serif">MATCHER</text>'
        f'<text x="{cx:.1f}" y="{cy + 12:.1f}" fill="{_SVG_ACCENT2}" font-size="11.5" '
        f'text-anchor="middle" font-family="ui-monospace,monospace">{html.escape(lbl.upper())}</text>'
    )

    bid_x_front = cx - band_w / 2 - 24
    ask_x_front = cx + band_w / 2 + 24

    # row order: top=worse, middle=FRONT (best), bottom=second tier
    row_map = [(2, 2), (0, 0), (1, 1)] if depth >= 3 else [(0, 0)]
    if depth == 2:
        row_map = [(1, 1), (0, 0)]

    for ri, (bi, ai) in enumerate(row_map):
        y = cy + (ri - (len(row_map) - 1) / 2) * row_h
        front = ri == len(row_map) // 2
        fade = 0 if front else 1
        back_off = 0 if front else 22
        bx = bid_x_front - back_off
        ax = ask_x_front + back_off
        bp, bs = float(bids[bi][0]), float(bids[bi][1])
        ap, ass = float(asks[ai][0]), float(asks[ai][1])
        _queue_box(bx, y, bp, bs, "bid", front, fade)
        _queue_box(ax, y, ap, ass, "ask", front, fade)

        if front:
            body.append(
                f'<path d="M{bid_x_front - box_w - 4:.1f},{y:.1f} L{cx - band_w/2 - 6:.1f},{y:.1f}" '
                f'stroke="{_SVG_ACCENT}" stroke-width="2" marker-end="url(#__AH__)"/>'
                f'<path d="M{ask_x_front + box_w + 4:.1f},{y:.1f} L{cx + band_w/2 + 6:.1f},{y:.1f}" '
                f'stroke="#f87171" stroke-width="2" marker-end="url(#__AH__)"/>'
            )
            if crosses:
                body.append(
                    f'<path d="M{bid_x_front - 8:.1f},{y:.1f} L{ask_x_front + 8:.1f},{y:.1f}" '
                    f'stroke="{_SVG_WARN}" stroke-width="3" stroke-dasharray="6 4" opacity="0.9"/>'
                    f'<text x="{cx:.1f}" y="{y - 28:.1f}" fill="{_SVG_WARN}" font-size="11" '
                    f'font-weight="700" text-anchor="middle" '
                    f'font-family="-apple-system,sans-serif">TRADE</text>'
                )
            else:
                gx1, gx2 = bid_x_front - 6, ask_x_front + 6
                body.append(
                    f'<path d="M{gx1:.1f},{y - 22:.1f} L{gx1:.1f},{y - 14:.1f} '
                    f'L{gx2:.1f},{y - 14:.1f} L{gx2:.1f},{y - 22:.1f}" '
                    f'fill="none" stroke="{_SVG_MUTED}" stroke-width="1.2" opacity="0.7"/>'
                    f'<text x="{cx:.1f}" y="{y - 18:.1f}" fill="{_SVG_MUTED}" font-size="9.5" '
                    f'text-anchor="middle" font-family="-apple-system,sans-serif">'
                    f"no overlap yet</text>"
                )

    svg, ah = _svg_shell("".join(body), w, h)
    return svg.replace("__AH__", ah)


def _render_graph(pic):
    nodes = pic.get("nodes", []) or []
    edges = pic.get("edges", []) or []
    if not nodes:
        return ""
    cw, rh, mx, my = 210, 130, 30, 28
    maxc = max((n.get("col", 0) for n in nodes), default=0)
    maxr = max((n.get("row", i) for i, n in enumerate(nodes)), default=0)
    max_lines = max(
        (len(_wrap(n.get("label", ""), 22)) for n in nodes), default=1
    )
    nh = max(52, 16 + max_lines * 18)
    geo = {}
    body = []
    for i, n in enumerate(nodes):
        col = n.get("col", 0)
        row = n.get("row", i)
        shape = n.get("shape", "box")
        label = n.get("label", "")
        lines = _wrap(label, 22)
        w = 168 if shape != "pill" else max(96, len(label) * 8 + 26)
        h = 74 if shape == "diamond" else nh
        cx = mx + col * cw + cw / 2
        cy = my + row * rh + rh / 2
        color = n.get("color") or _SHAPE_COLOR.get(shape, _SVG_STROKE)
        geo[n.get("id", i)] = (cx, cy, w, h)
        body.append(
            _node_shape(shape, cx, cy, w, h, color)
            + _svg_text(cx, cy, lines, color=_SVG_INK)
        )
    edge_svg = []
    for e in edges:
        a = geo.get(e.get("from"))
        b = geo.get(e.get("to"))
        if not a or not b:
            continue
        d, (lx, ly) = _edge_path(a, b)
        edge_svg.append(
            f'<path d="{d}" fill="none" stroke="{_SVG_MUTED}" stroke-width="1.6" '
            f'stroke-linejoin="round" marker-end="url(#__AH__)"/>'
        )
        edge_svg.append(_edge_label(lx, ly, e.get("label", "")))
    w = mx * 2 + (maxc + 1) * cw
    h = my * 2 + (maxr + 1) * rh
    svg, ah = _svg_shell("".join(edge_svg) + "".join(body), w, h)
    return svg.replace("__AH__", ah)


def _render_loop(pic):
    import math

    labels = pic.get("nodes", []) or []
    if not labels:
        return ""
    kind = (pic.get("kind") or "reinforcing").lower()
    is_r = kind.startswith("r")
    color = _SVG_ACCENT if is_r else _SVG_ACCENT2
    letter = "R" if is_r else "B"
    word = "reinforcing" if is_r else "balancing"
    n = len(labels)
    size = 360
    cx0, cy0 = size / 2, size / 2
    radius = 118
    pos = []
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        pos.append((cx0 + radius * math.cos(ang), cy0 + radius * math.sin(ang)))
    body = []
    for i in range(n):
        ax, ay = pos[i]
        bx, by = pos[(i + 1) % n]
        mxp, myp = (ax + bx) / 2, (ay + by) / 2
        # bow the arc outward from center
        ox, oy = mxp - cx0, myp - cy0
        d = math.hypot(ox, oy) or 1
        ctrlx, ctrly = mxp + ox / d * 46, myp + oy / d * 46
        # trim endpoints toward node centers so arrow doesn't overlap the pill
        def _trim(px, py, tx, ty, r=42):
            dx, dy = tx - px, ty - py
            dd = math.hypot(dx, dy) or 1
            return px + dx / dd * r, py + dy / dd * r
        s = _trim(ax, ay, ctrlx, ctrly)
        en = _trim(bx, by, ctrlx, ctrly)
        body.append(
            f'<path d="M{s[0]:.1f},{s[1]:.1f} Q{ctrlx:.1f},{ctrly:.1f} {en[0]:.1f},{en[1]:.1f}" '
            f'fill="none" stroke="{color}" stroke-width="1.8" marker-end="url(#__AH__)" opacity="0.85"/>'
        )
    for i, lbl in enumerate(labels):
        px, py = pos[i]
        lines = _wrap(lbl, 14)
        w = max(88, max(len(x) for x in lines) * 8 + 22)
        body.append(_node_shape("pill", px, py, w, 40, color))
        body.append(_svg_text(px, py, lines, size=12))
    body.append(
        f'<circle cx="{cx0}" cy="{cy0}" r="30" fill="{_SVG_NODE}" stroke="{color}" stroke-width="2"/>'
        f'<text x="{cx0}" y="{cy0 - 3}" fill="{color}" font-size="24" font-weight="800" '
        f'text-anchor="middle" dominant-baseline="middle" font-family="Georgia,serif">{letter}</text>'
        f'<text x="{cx0}" y="{cy0 + 16}" fill="{_SVG_MUTED}" font-size="9.5" '
        f'text-anchor="middle" font-family="-apple-system,sans-serif">{word}</text>'
    )
    svg, ah = _svg_shell("".join(body), size, size)
    return svg.replace("__AH__", ah)


def _render_stock_flow(pic):
    stock = pic.get("stock", "stock")
    inflow = pic.get("inflow", "in")
    outflow = pic.get("outflow", "out")
    w, h = 640, 200
    cy = h / 2
    body = []
    # source + sink clouds
    body.append(_node_shape("cloud", 78, cy, 96, 66, _SVG_MUTED))
    body.append(_svg_text(78, cy, _wrap(inflow, 12), size=12, color=_SVG_MUTED))
    body.append(_node_shape("cloud", w - 78, cy, 96, 66, _SVG_MUTED))
    body.append(_svg_text(w - 78, cy, _wrap(outflow, 12), size=12, color=_SVG_MUTED))
    # stock box (center)
    body.append(_node_shape("box", w / 2, cy, 170, 84, _SVG_ACCENT))
    body.append(_svg_text(w / 2, cy - 10, ["STOCK"], size=12, color=_SVG_ACCENT, weight="700"))
    body.append(_svg_text(w / 2, cy + 12, _wrap(stock, 20), size=13))
    # inflow pipe + valve
    body.append(
        f'<line x1="126" y1="{cy}" x2="{w/2 - 85}" y2="{cy}" stroke="{_SVG_ACCENT}" '
        f'stroke-width="3" marker-end="url(#__AH__)"/>'
        f'<circle cx="200" cy="{cy}" r="9" fill="{_SVG_BG}" stroke="{_SVG_ACCENT}" stroke-width="2.5"/>'
    )
    # outflow pipe + valve
    body.append(
        f'<line x1="{w/2 + 85}" y1="{cy}" x2="{w - 126}" y2="{cy}" stroke="{_SVG_WARN}" '
        f'stroke-width="3" marker-end="url(#__AH__)"/>'
        f'<circle cx="{w - 200}" cy="{cy}" r="9" fill="{_SVG_BG}" stroke="{_SVG_WARN}" stroke-width="2.5"/>'
    )
    svg, ah = _svg_shell("".join(body), w, h)
    return svg.replace("__AH__", ah)


_SVG_RENDERERS = {
    "graph": _render_graph,
    "loop": _render_loop,
    "stock_flow": _render_stock_flow,
    "orderbook": _render_orderbook,
    "queue_spread": _render_queue_spread,
}


def _figure(inner_html, caption):
    cap = f'<figcaption class="caption">{_fmt(caption)}</figcaption>' if caption else ""
    return f'<figure class="fig">{inner_html}{cap}</figure>'


def _one_picture(pic):
    if not pic:
        return ""
    ptype = pic.get("type", "ascii")
    caption = pic.get("caption", "")
    if ptype in _SVG_RENDERERS:
        svg = _SVG_RENDERERS[ptype](pic)
        return _figure(svg, caption) if svg else ""
    content = pic.get("content", "")
    if ptype == "mermaid":
        return _figure(f'<pre class="mermaid">{_pre(content)}</pre>', caption)
    return _figure(f'<pre class="ascii">{_pre(content)}</pre>', caption)


def _picture_html(pic):
    if not pic:
        return ""
    pics = pic if isinstance(pic, list) else [pic]
    figs = "".join(_one_picture(p) for p in pics if p)
    if not figs:
        return ""
    return f'<section id="picture"><h2>The picture</h2>{figs}</section>'


def _steps_html(hiw):
    if not hiw:
        return ""
    intro = hiw.get("intro", "")
    steps = hiw.get("steps", []) or []
    intro_html = f"<p>{_fmt(intro)}</p>" if intro else ""
    items = "".join(f"<li>{_fmt(s)}</li>" for s in steps)
    return (
        '<section id="how"><h2>How it actually works</h2>'
        f"{intro_html}<ol class=\"trace\">{items}</ol></section>"
    )


def _ladder_html(ladder):
    if not ladder:
        return ""
    rungs = [
        ("ELI5", ladder.get("eli5", "")),
        ("Practitioner", ladder.get("practitioner", "")),
        ("Expert", ladder.get("expert", "")),
    ]
    rows = "".join(
        f'<div class="rung"><span class="rung-label">{html.escape(lbl)}</span>'
        f'<div class="rung-body">{_fmt(body)}</div></div>'
        for lbl, body in rungs
        if body
    )
    return f'<section id="ladder"><h2>The depth ladder</h2>{rows}</section>'


def _curveballs_html(cbs):
    if not cbs:
        return ""
    cards = []
    for i, cb in enumerate(cbs, 1):
        lens = cb.get("lens", "")
        q = cb.get("question", "")
        a = cb.get("answer", "")
        is_open = str(a).strip().upper().startswith("OPEN")
        badge = f'<span class="lens">{html.escape(lens)}</span>' if lens else ""
        open_cls = " open-gap" if is_open else ""
        cards.append(
            f'<div class="cb{open_cls}"><div class="cb-head"><span class="cb-num">{i}</span>{badge}</div>'
            f'<p class="cb-q">{_fmt(q)}</p><p class="cb-a">{_fmt(a)}</p></div>'
        )
    return (
        '<section id="curveballs"><h2>Curveball defense</h2>'
        '<p class="hint">Ordered worst-first. Hold these and you won\'t get rattled.</p>'
        f'{"".join(cards)}</section>'
    )


def _check_html(items):
    if not items:
        return ""
    rows = []
    for i, it in enumerate(items, 1):
        q = it.get("q", "")
        a = it.get("a", "")
        rows.append(
            f'<details class="cy"><summary><span class="cy-num">{i}</span>{_fmt(q)}</summary>'
            f'<div class="cy-a">{_fmt(a)}</div></details>'
        )
    return (
        '<section id="check"><h2>Check yourself</h2>'
        '<p class="hint">Answer out loud before opening. Saying it is what makes it stick.</p>'
        f'{"".join(rows)}</section>'
    )


def _capabilities_html(caps):
    if not caps:
        return ""
    prefixes = sorted((caps.get("display_prefixes") or {}).items(), key=lambda kv: -len(kv[0]))

    def _shorten(path):
        for full, short in prefixes:
            if path.startswith(full):
                return short + path[len(full):]
        return path

    def _paths(paths):
        return "<br>".join(
            f'<code title="{html.escape(p)}">{html.escape(_shorten(p))}</code>' for p in paths or []
        )

    rows = []
    group = None
    for r in caps.get("rows", []) or []:
        if r.get("group") and r["group"] != group:
            group = r["group"]
            rows.append(f'<tr class="cap-group"><td colspan="4">{html.escape(group)}</td></tr>')
        rows.append(
            f'<tr><td><span class="cap-name">{_fmt(r.get("capability", ""))}</span>'
            f'<span class="cap-what">{_fmt(r.get("what", ""))}</span></td>'
            f'<td>{_paths(r.get("backend"))}</td><td>{_paths(r.get("client"))}</td>'
            f'<td>{_fmt(r.get("read", ""))}</td></tr>'
        )
    intro = caps.get("intro", "")
    legend = " &middot; ".join(
        f"<code>{html.escape(short)}</code> = <code>{html.escape(full)}</code>" for full, short in prefixes
    )
    return (
        '<section id="capabilities"><h2>Product capabilities to code</h2>'
        f'{f"<p>{_fmt(intro)}</p>" if intro else ""}'
        f'<p class="hint">{legend}</p>'
        '<div class="cap-wrap"><table class="cap"><thead><tr><th>Capability</th><th>Backend</th>'
        '<th>Web</th><th>Read next</th></tr></thead>'
        f'<tbody>{"".join(rows)}</tbody></table></div></section>'
    )


def render(card):
    topic = card.get("topic", "Teaching Card")
    audience = card.get("audience", "")
    one_liner = card.get("one_liner", "")
    analogy = card.get("analogy", {}) or {}
    picture = card.get("picture", {}) or {}
    grounding = card.get("grounding", "")
    teach_back = card.get("teach_back", "")

    _pics = picture if isinstance(picture, list) else [picture]
    needs_mermaid = any((p or {}).get("type") == "mermaid" for p in _pics)

    # nav (only sections that exist)
    nav_items = [("one-liner", "One-liner")]
    if analogy:
        nav_items.append(("analogy", "Analogy"))
    if picture:
        nav_items.append(("picture", "Picture"))
    if card.get("capabilities"):
        nav_items.append(("capabilities", "Capabilities"))
    if card.get("how_it_works"):
        nav_items.append(("how", "How it works"))
    if card.get("depth_ladder"):
        nav_items.append(("ladder", "Depth ladder"))
    if card.get("curveballs"):
        nav_items.append(("curveballs", "Curveballs"))
    if card.get("check_yourself"):
        nav_items.append(("check", "Check yourself"))
    if teach_back:
        nav_items.append(("teachback", "Teach-back"))
    nav_html = "".join(
        f'<a href="#{anchor}">{html.escape(label)}</a>' for anchor, label in nav_items
    )

    date = _dt.date.today().isoformat()
    sub = f"Teaching Card &middot; {html.escape(date)}"
    if audience:
        sub += f" &middot; for {html.escape(audience)}"

    parts = []
    parts.append(
        f'<section id="one-liner"><h2>The one-liner</h2>'
        f'<p class="oneliner">{_fmt(one_liner)}</p></section>'
    )
    if analogy:
        seam = analogy.get("seam", "")
        seam_html = (
            f'<div class="seam"><span class="seam-label">Where it breaks</span>'
            f'<div>{_fmt(seam)}</div></div>'
            if seam
            else ""
        )
        parts.append(
            f'<section id="analogy"><h2>The analogy</h2>'
            f'<p>{_fmt(analogy.get("text", ""))}</p>{seam_html}</section>'
        )
    parts.append(_picture_html(picture))
    parts.append(_capabilities_html(card.get("capabilities")))
    parts.append(_steps_html(card.get("how_it_works")))
    parts.append(_ladder_html(card.get("depth_ladder")))
    parts.append(_curveballs_html(card.get("curveballs")))
    parts.append(_check_html(card.get("check_yourself")))
    if teach_back:
        parts.append(
            f'<section id="teachback"><h2>The 60-second teach-back</h2>'
            f'<blockquote class="teachback">{_fmt(teach_back)}</blockquote></section>'
        )
    if grounding:
        parts.append(f'<p class="grounding">Grounding: {_fmt(grounding)}</p>')

    body = "".join(p for p in parts if p)

    mermaid_script = (
        '<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>'
        '<script>mermaid.initialize({startOnLoad:true,theme:"dark"});</script>'
        if needs_mermaid
        else ""
    )

    return (
        _HTML_HEAD.replace("__TITLE__", html.escape(str(topic)))
        + f'<header><h1>{_fmt(topic)}</h1><p class="sub">{sub}</p></header>'
        + '<div class="wrap">'
        + f'<nav class="toc">{nav_html}</nav>'
        + f'<main>{body}</main>'
        + "</div>"
        + mermaid_script
        + _HTML_TAIL
    )


_HTML_HEAD = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__ — Teaching Card</title>
<style>
:root{
  --bg:#0d1117; --panel:#161b22; --panel2:#1c2230; --ink:#e6edf3; --muted:#9aa7b5;
  --accent:#4ade80; --accent2:#38bdf8; --warn:#fbbf24; --line:#273040; --code:#f0883e;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;}
header{padding:40px 24px 20px;max-width:1100px;margin:0 auto;border-bottom:1px solid var(--line)}
h1{margin:0;font-size:34px;letter-spacing:-.02em}
.sub{color:var(--muted);margin:8px 0 0;font-size:14px}
.wrap{display:flex;gap:28px;max-width:1100px;margin:0 auto;padding:24px}
.toc{position:sticky;top:16px;align-self:flex-start;min-width:160px;display:flex;flex-direction:column;gap:2px;
  padding:12px;background:var(--panel);border:1px solid var(--line);border-radius:12px;font-size:13px}
.toc a{color:var(--muted);text-decoration:none;padding:6px 8px;border-radius:7px}
.toc a:hover{color:var(--ink);background:var(--panel2)}
main{flex:1;min-width:0}
section{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin:0 0 18px}
h2{margin:0 0 12px;font-size:16px;text-transform:uppercase;letter-spacing:.08em;color:var(--accent)}
p{margin:0 0 10px}
.oneliner{font-size:20px;line-height:1.5;color:#fff}
code{background:#0b0f16;color:var(--code);padding:1px 6px;border-radius:5px;font-size:.9em;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
pre.ascii{background:#0b0f16;border:1px solid var(--line);border-radius:10px;padding:16px;overflow:auto;
  font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;line-height:1.45;color:#cfe3ff}
pre.mermaid{background:#0b0f16;border:1px solid var(--line);border-radius:10px;padding:16px;text-align:center}
.fig{margin:0 0 16px;text-align:center}
.fig:last-child{margin-bottom:0}
.fig svg{display:block;margin:0 auto}
.caption{color:var(--muted);font-size:13px;margin-top:8px;text-align:center}
.seam{margin-top:12px;background:var(--panel2);border-left:3px solid var(--warn);border-radius:8px;padding:10px 14px}
.seam-label{display:block;font-size:11px;text-transform:uppercase;letter-spacing:.08em;color:var(--warn);margin-bottom:4px}
ol.trace{margin:0;padding-left:22px}
ol.trace li{margin:0 0 8px}
.rung{display:flex;gap:14px;padding:10px 0;border-bottom:1px dashed var(--line)}
.rung:last-child{border-bottom:0}
.rung-label{flex:0 0 108px;color:var(--accent2);font-weight:600;font-size:14px}
.rung-body{flex:1}
.hint{color:var(--muted);font-size:13px;margin:-4px 0 14px}
.cb{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin:0 0 12px}
.cb.open-gap{border-color:var(--warn)}
.cb-head{display:flex;align-items:center;gap:10px;margin-bottom:6px}
.cb-num{display:inline-grid;place-items:center;width:22px;height:22px;border-radius:50%;
  background:var(--accent);color:#08130a;font-weight:700;font-size:12px}
.lens{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--accent2);
  border:1px solid var(--accent2);border-radius:20px;padding:2px 10px}
.cb-q{font-weight:600;color:#fff;margin:0 0 6px}
.cb-a{margin:0;color:var(--ink)}
details.cy{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 14px;margin:0 0 10px}
details.cy summary{cursor:pointer;font-weight:500;list-style:none;display:flex;gap:10px;align-items:flex-start}
details.cy summary::-webkit-details-marker{display:none}
.cy-num{display:inline-grid;place-items:center;width:20px;height:20px;border-radius:50%;
  background:var(--accent2);color:#04121a;font-weight:700;font-size:12px;flex:0 0 auto;margin-top:2px}
details.cy[open] summary{color:var(--accent)}
.cy-a{margin:10px 0 0 30px;color:var(--muted)}
blockquote.teachback{margin:0;padding:16px 18px;background:linear-gradient(135deg,#132b1e,#0b1f2b);
  border:1px solid var(--accent);border-radius:12px;font-size:17px;line-height:1.6;color:#eaffef}
.cap-wrap{overflow-x:auto}
table.cap{width:100%;border-collapse:collapse;font-size:13px}
table.cap th{text-align:left;color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase;
  letter-spacing:.06em;padding:6px 8px;border-bottom:1px solid var(--line)}
table.cap td{vertical-align:top;padding:8px;border-bottom:1px dashed var(--line)}
table.cap td code{font-size:12px;white-space:nowrap}
tr.cap-group td{color:var(--accent2);font-weight:700;text-transform:uppercase;font-size:11px;
  letter-spacing:.08em;padding-top:16px;border-bottom:1px solid var(--line)}
.cap-name{display:block;font-weight:600;color:#fff}
.cap-what{display:block;color:var(--muted);font-size:12px}
.grounding{color:var(--muted);font-size:12px;text-align:center;margin:8px 0 32px}
@media(max-width:760px){.wrap{flex-direction:column}.toc{position:static;flex-direction:row;flex-wrap:wrap}}
</style></head><body>
"""

_HTML_TAIL = "</body></html>"


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render a Teaching Card JSON into HTML.")
    ap.add_argument("input", nargs="?", help="Path to card JSON, or '-' for stdin")
    ap.add_argument("-o", "--output", help="Output HTML path")
    ap.add_argument("--open", action="store_true", help="Open the result in a browser")
    ap.add_argument("--schema", action="store_true", help="Print the JSON contract + example and exit")
    args = ap.parse_args(argv)

    if args.schema:
        print(json.dumps(EXAMPLE, indent=2))
        return 0

    if not args.input:
        ap.error("provide a card JSON path, '-' for stdin, or --schema")

    if args.input == "-":
        raw = sys.stdin.read()
    else:
        raw = Path(args.input).read_text(encoding="utf-8")

    try:
        card = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"error: input is not valid JSON: {e}", file=sys.stderr)
        return 2

    if not card.get("topic"):
        print("warning: card has no 'topic'", file=sys.stderr)

    html_out = render(card)

    if args.output:
        out = Path(args.output).expanduser()
    else:
        out = Path.home() / "teach-cards" / f"{_slug(card.get('topic', 'card'))}-{_dt.date.today().isoformat()}.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8")
    print(str(out))

    if args.open:
        webbrowser.open(f"file://{out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
