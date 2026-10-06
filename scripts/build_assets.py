#!/usr/bin/env python3
"""Builds every SVG in assets/ in a dark and a light variant.

    python3 scripts/build_assets.py

GitHub strips CSS and JS from READMEs, so all visual design lives in these
SVGs. Each one is self-contained (no external fonts or images), sits on a
transparent background so it blends with any GitHub theme, and honours
prefers-reduced-motion. Edit the content blocks below and re-run.
"""
import math
from pathlib import Path
from string import Template
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "assets"
W = 800

SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', 'Noto Sans', Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"

# One neutral ramp and one accent per theme. Nothing else.
THEMES = {
    "dark": dict(fg="#F0F6FC", tx="#C9D1D9", mu="#9198A1", fa="#6E7681", ac="#5B9DFF", on_ac="#0D1117"),
    "light": dict(fg="#1F2328", tx="#3B434B", mu="#59636E", fa="#818B98", ac="#1D5FD6", on_ac="#FFFFFF"),
}

BASE_CSS = """
text{font-family:$sans}
.mono{font-family:$mono}
.fg{fill:$fg}.tx{fill:$tx}.mu{fill:$mu}.fa{fill:$fa}.ac{fill:$ac}.on{fill:$on_ac}
.b{font-weight:600}
.hair{stroke:$fg;stroke-opacity:.16;fill:none}
.panel{fill:$fg;fill-opacity:.03;stroke:$fg;stroke-opacity:.15}
.node{fill:$fg;fill-opacity:.04;stroke:$fg;stroke-opacity:.24}
.node-ac{fill:$ac;fill-opacity:.12;stroke:$ac;stroke-opacity:.75}
.wire{stroke:$mu;stroke-width:1.3;fill:none}
.wire-ac{stroke:$ac;stroke-width:1.5;fill:none}
.head{fill:$mu}.head-ac{fill:$ac}
"""

REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}%s}"


def svg(w, h, body, css, title, th, reduced=""):
    style = Template(BASE_CSS + css + REDUCED % reduced).substitute(sans=SANS, mono=MONO, **th)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title><style>{style}</style>{body}</svg>\n"
    )


def write(name, w, h, body, css, title, reduced=""):
    for mode, th in THEMES.items():
        (OUT / f"{name}-{mode}.svg").write_text(svg(w, h, body, css, title, th, reduced), encoding="utf-8")


def smooth(pts):
    """Catmull-Rom spline through pts, as a cubic Bezier path."""
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d


MARKERS = (
    '<defs><marker id="a" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
    '<path d="M0 .8 7.2 4 0 7.2z" class="head"/></marker>'
    '<marker id="b" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="7" markerHeight="7" orient="auto">'
    '<path d="M0 .8 7.2 4 0 7.2z" class="head-ac"/></marker></defs>'
)


def node(x, y, w, h, label, sub=None, accent=False):
    cx = x + w / 2
    out = f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="8" class="{"node-ac" if accent else "node"}"/>'
    ly = y + h / 2 + (-3 if sub else 5)
    out += f'<text x="{cx:.1f}" y="{ly:.1f}" text-anchor="middle" font-size="13.5" class="fg b">{escape(label)}</text>'
    if sub:
        out += f'<text x="{cx:.1f}" y="{ly + 17:.1f}" text-anchor="middle" font-size="10.5" class="mono mu">{escape(sub)}</text>'
    return out


def arrow(x1, y1, x2, y2, accent=False):
    return (
        f'<path d="M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}" class="{"wire-ac" if accent else "wire"}" '
        f'marker-end="url(#{"b" if accent else "a"})"/>'
    )


# --------------------------------------------------------------------------
# Header: name, role, tagline, and the positioning curve (where an AI engineer sits)
# --------------------------------------------------------------------------
def header():
    x0, x1, base, amp, sigma, cx = 404.0, 796.0, 192.0, 118.0, 38.0, 612.0
    n = 72
    pts = []
    for i in range(n):
        x = x0 + i * (x1 - x0) / (n - 1)
        pts.append((x, base - amp * math.exp(-((x - cx) ** 2) / (2 * sigma ** 2))))
    curve = smooth(pts)
    area = curve + f"L{x1:.1f} {base:.1f}L{x0:.1f} {base:.1f}Z"
    peak_y = base - amp

    body = (
        '<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" class="stop-a"/><stop offset="1" class="stop-b"/></linearGradient></defs>'
        '<rect x="1" y="35" width="26" height="2" class="ac"/>'
        '<text x="38" y="41" font-size="12.5" letter-spacing="2.6" class="mono ac b">AI / ML ENGINEER</text>'
        '<text x="-2" y="116" font-size="70" font-weight="700" letter-spacing="-2.6" class="fg">Yogdeep</text>'
        '<text x="-2" y="188" font-size="70" font-weight="700" letter-spacing="-2.6" class="fg">Benchimath</text>'
        '<text x="1" y="236" font-size="18" class="tx">Building ML systems that survive contact with real-world data.</text>'
        f'<path d="{area}" fill="url(#g)" class="area"/>'
        f'<path d="{curve}" pathLength="1" class="curve"/>'
        # left tail
        f'<g class="l1"><text x="{x0:.0f}" y="151" font-size="11" letter-spacing="1.4" class="mono fg b">AI VIBE CODER</text>'
        f'<text x="{x0:.0f}" y="166" font-size="10" class="mu">Random AI vibe-coded apps</text></g>'
        # peak
        f'<g class="l2"><text x="{cx:.0f}" y="36" font-size="12.5" letter-spacing="2" text-anchor="middle" class="mono ac b">AI ENGINEER</text>'
        f'<text x="{cx:.0f}" y="52" font-size="10.5" text-anchor="middle" class="mu">AI + Engineering + Communication</text></g>'
        # right tail
        f'<g class="l3"><text x="{x1:.0f}" y="151" font-size="11" letter-spacing="1.4" text-anchor="end" class="mono fg b">SDE</text>'
        f'<text x="{x1:.0f}" y="166" font-size="10" text-anchor="end" class="mu">Zero AI knowledge</text></g>'
        f'<circle cx="{cx:.1f}" cy="{peak_y:.1f}" r="3.8" class="ac dot"/>'
        f'<circle cx="{cx:.1f}" cy="{peak_y:.1f}" r="3.8" class="ring"/>'
    )
    css = """
.stop-a{stop-color:$ac;stop-opacity:.20}.stop-b{stop-color:$ac;stop-opacity:0}
.curve{stroke:$fg;stroke-width:2;fill:none;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;animation:draw 2.2s cubic-bezier(.4,.1,.3,1) .3s backwards}
.area{animation:fade 1.2s ease-out 2.1s backwards}
.l1{animation:fade .5s ease-out .7s backwards}
.l2{animation:fade .5s ease-out 1.5s backwards}
.l3{animation:fade .5s ease-out 2.2s backwards}
.dot{animation:fade .3s ease-out 1.5s backwards}
.ring{fill:none;stroke:$ac;stroke-width:1.4;opacity:0;transform-box:fill-box;transform-origin:center;animation:pulse 2.8s ease-out 2.8s infinite}
@keyframes draw{from{stroke-dashoffset:1}}
@keyframes fade{from{opacity:0}}
@keyframes pulse{0%{opacity:.7;transform:scale(1)}70%,100%{opacity:0;transform:scale(3.4)}}
"""
    # Resting state is the finished frame, so nothing is hidden if animation never runs.
    write("header", W, 256, body, css,
          "Yogdeep Benchimath, AI / ML Engineer. Building ML systems that survive contact with real-world data. "
          "A bell curve places the AI engineer (AI + engineering + communication) at the peak, "
          "between the AI vibe coder and the SDE with zero AI knowledge.")


# --------------------------------------------------------------------------
# Link buttons
# --------------------------------------------------------------------------
def buttons():
    for name, label, w, primary in [
        ("portfolio", "Portfolio", 112, True),
        ("linkedin", "LinkedIn", 108, False),
        ("resume", "Resume", 100, False),
        ("email", "Email", 88, False),
    ]:
        h = 34
        box = (
            f'<rect width="{w}" height="{h}" rx="8" class="ac"/>' if primary
            else f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="7.5" class="panel"/>'
        )
        tone = "on" if primary else "fg"
        body = (
            box
            + f'<text x="14" y="22" font-size="13.5" class="{tone} b">{label}</text>'
            + f'<path d="M{w - 23} 21.5l8-8m-5.5 0h5.5v5.5" class="tick-{tone}"/>'
        )
        css = (
            ".tick-on{stroke:$on_ac;stroke-width:1.6;fill:none;stroke-linecap:round;stroke-linejoin:round}"
            ".tick-fg{stroke:$mu;stroke-width:1.6;fill:none;stroke-linecap:round;stroke-linejoin:round}"
        )
        write(f"btn-{name}", w, h, body, css, label)


# --------------------------------------------------------------------------
# Terminal intro. Commands type themselves once, then hold.
# --------------------------------------------------------------------------
def terminal():
    SEP = ("fa", "  /  ")
    session = [
        ("whoami", [("fg b", "Yogdeep Benchimath"), SEP, ("tx", "AI/ML engineer"), SEP, ("tx", "B.Tech AI & ML, VIT Vellore")]),
        ("focus", [("tx", "AI systems"), SEP, ("tx", "machine learning"), SEP, ("tx", "generative AI"), SEP, ("tx", "quantitative ML")]),
        ("currently_building", [("tx", "financial ML research pipeline"), SEP, ("tx", "retrieval systems"), SEP, ("tx", "production ML")]),
    ]
    cw, fs, lh = 9.0, 15, 25
    px, tx_x, y = 22, 40, 74
    dt, t = 0.06, 0.7
    body = (
        f'<rect x=".5" y=".5" width="{W - 1}" height="243" rx="10" class="panel"/>'
        '<text x="22" y="27" font-size="12" class="mono fa">~/yogdeep</text>'
        f'<path d="M.5 42.5h{W - 1}" class="hair"/>'
    )
    css = (
        # Resting state is the finished session: text visible, typing cursors hidden.
        ".p,.c{animation:show .01s linear backwards}"
        ".o{animation:show .35s ease-out backwards}"
        ".cur{opacity:0}"
        ".cur,.fin rect{fill:$fg;fill-opacity:.85}"
        "@keyframes show{from{opacity:0}}@keyframes on{from{opacity:1}to{opacity:1}}"
        "@keyframes blink{0%{opacity:1}50%{opacity:0}100%{opacity:0}}"
    )
    for i, (cmd, out) in enumerate(session):
        n = len(cmd)
        end = t + n * dt
        body += f'<text x="{px}" y="{y}" font-size="{fs}" class="mono ac p" style="animation-delay:{t - .15:.2f}s">$</text>'
        for k, ch in enumerate(cmd):
            body += (
                f'<text x="{tx_x + k * cw:.1f}" y="{y}" font-size="{fs}" class="mono fg c" '
                f'style="animation-delay:{t + (k + 1) * dt:.2f}s">{escape(ch)}</text>'
            )
        body += f'<rect x="{tx_x}" y="{y - 13}" width="8.5" height="17" class="cur k{i}"/>'
        css += (
            f"@keyframes m{i}{{to{{transform:translateX({n * cw:.1f}px)}}}}"
            f".k{i}{{animation:on {n * dt + .35:.2f}s linear {t - .15:.2f}s,"
            f"m{i} {n * dt:.2f}s steps({n},end) {t:.2f}s forwards}}"
        )
        y += lh
        spans = "".join(f'<tspan class="{c}">{escape(s)}</tspan>' for c, s in out)
        body += (
            f'<text x="{px}" y="{y}" font-size="{fs}" class="mono o" xml:space="preserve" '
            f'style="white-space:pre;animation-delay:{end + .22:.2f}s">{spans}</text>'
        )
        y += lh
        t = end + 0.22 + 0.55
    body += (
        f'<g class="fin" style="animation:show .01s linear {t:.2f}s backwards">'
        f'<text x="{px}" y="{y}" font-size="{fs}" class="mono ac">$</text>'
        f'<rect x="{tx_x}" y="{y - 13}" width="8.5" height="17" '
        f'style="animation:blink 1.15s steps(1,end) {t:.2f}s infinite"/></g>'
    )
    reduced = ""
    title = (
        "Terminal session. whoami: Yogdeep Benchimath, AI/ML engineer, B.Tech AI and ML at VIT Vellore. "
        "focus: AI systems, machine learning, generative AI, quantitative ML. "
        "currently_building: financial ML research pipeline, retrieval systems, production ML."
    )
    write("terminal", W, 244, body, css, title, reduced)


# --------------------------------------------------------------------------
# Figure: TBC-GAN architecture and headline results
# --------------------------------------------------------------------------
def fig_tbcgan():
    ny, nh = 94, 56
    mid = ny + nh / 2
    body = MARKERS
    body += f'<rect x=".5" y=".5" width="{W - 1}" height="339" rx="10" class="panel"/>'
    body += '<text x="24" y="33" font-size="12" letter-spacing="1.4" class="mono fg b">TBC-GAN</text>'
    body += '<text x="776" y="33" font-size="11.5" text-anchor="end" class="mono mu">VSTOXX volatility index, 2,000+ trading days</text>'
    # generator group
    body += '<rect x="150.5" y="78.5" width="384" height="86" rx="10" class="group"/>'
    body += '<text x="162" y="70" font-size="10.5" letter-spacing="1.6" class="mono mu">GENERATOR</text>'
    body += node(24, ny, 100, nh, "noise z", "+ condition")
    body += arrow(127, mid, 147, mid)
    for i, (label, sub) in enumerate([("Transformer", "global context"), ("BiLSTM", "sequence memory"), ("CNN", "local patterns")]):
        x = 162 + i * 124
        body += node(x, ny, 112, nh, label, sub)
        if i:
            body += arrow(x - 10, mid, x - 2, mid)
    body += arrow(537, mid, 553, mid)
    body += node(556, ny, 108, nh, "synthetic", "24-step window")
    body += arrow(667, mid, 685, mid)
    body += node(688, ny, 88, nh, "critic", "realism score", accent=True)
    # real data into the critic
    body += '<text x="732" y="64" font-size="10.5" text-anchor="middle" class="mono mu">real window</text>'
    body += arrow(732, 70, 732, 91)
    # adversarial feedback
    body += '<path d="M732 153V192H342V168" class="wire-ac loop" marker-end="url(#b)"/>'
    body += '<text x="537" y="211" font-size="11" text-anchor="middle" class="mono ac">WGAN-GP: Wasserstein loss + gradient penalty</text>'
    # results
    body += f'<path d="M24 236.5h{W - 48}" class="hair"/>'
    for i, (value, label) in enumerate([
        ("98.2%", "lower kurtosis error"),
        ("94%", "lower skewness deviation"),
        ("68.7%", "lower KS statistic"),
        ("0.0107", "ACF MSE over 20 lags"),
    ]):
        x = 24 + i * 190
        body += f'<text x="{x}" y="286" font-size="36" font-weight="700" letter-spacing="-1" class="fg">{value}</text>'
        body += f'<text x="{x + 1}" y="311" font-size="11.5" class="mono mu">{label}</text>'
    css = (
        ".group{fill:none;stroke:$fg;stroke-opacity:.14;stroke-dasharray:3 4}"
        ".loop{stroke-dasharray:5 5;animation:march 1.6s linear infinite}"
        "@keyframes march{to{stroke-dashoffset:-20}}"
    )
    title = (
        "TBC-GAN architecture: noise and a condition pass through a generator of Transformer, BiLSTM and CNN blocks "
        "to produce a 24-step synthetic window, scored by a critic trained with WGAN-GP. "
        "Results against baseline: 98.2% lower kurtosis error, 94% lower skewness deviation, 68.7% lower KS statistic, "
        "ACF MSE of 0.0107 over 20 lags."
    )
    write("fig-tbcgan", W, 340, body, css, title)


# --------------------------------------------------------------------------
# Pipeline strips for the other featured projects
# --------------------------------------------------------------------------
def strip(name, nodes, focus, title):
    n, gap, h, top = len(nodes), 26, 60, 2
    w = (W - 1 - (n - 1) * gap) / n
    mid = top + h / 2
    body = MARKERS
    for i, (label, sub) in enumerate(nodes):
        x = 0.5 + i * (w + gap)
        body += node(x, top + 0.5, w, h, label, sub, accent=(i == focus))
        if i < n - 1:
            body += arrow(x + w + 5, mid + 0.5, x + w + gap - 4, mid + 0.5)
    write(name, W, h + 5, body, "", title)


def strips():
    strip("flow-search", [
        ("embed query", "MiniLM, 384-dim"),
        ("cluster router", "fuzzy c-means, k=20"),
        ("semantic cache", "42% hits at 0.85"),
        ("BM25 recall", "top-100 candidates"),
        ("FAISS re-rank", "dense, exact search"),
    ], 2, "Hybrid semantic search pipeline: query embedding with MiniLM, fuzzy c-means cluster routing, "
       "cluster-partitioned semantic cache, BM25 candidate recall, FAISS dense re-ranking.")
    strip("flow-resume", [
        ("resumes + JD", "PDF, DOCX, TXT"),
        ("parse + clean", "spaCy lemmas"),
        ("classify", "TF-IDF + SVM"),
        ("match score", "skills + cosine"),
        ("ranked shortlist", "FastAPI + Next.js"),
    ], 3, "Resume screening pipeline: resumes and a job description are parsed and cleaned, classified with TF-IDF and an SVM, "
       "scored for match, and returned as a ranked shortlist.")
    strip("flow-consent", [
        ("video frames", "real time"),
        ("detection", "YOLOv8 + RetinaFace"),
        ("identity match", "FAISS vector search"),
        ("consent map", "FastAPI services"),
        ("admin portal", "React, RBAC"),
    ], 2, "Consent Map pipeline: video frames, detection with YOLOv8 and RetinaFace, identity matching with FAISS vector search, "
       "consent mapping through FastAPI services, and a role-based React admin portal.")


# --------------------------------------------------------------------------
# Signature visual: how the work moves, and where it loops back
# --------------------------------------------------------------------------
def method():
    xs = [64 + i * 134.4 for i in range(6)]
    y = 112
    stations = [
        ("DATA", "messy, real"),
        ("RESEARCH", "find the gap"),
        ("MODEL", "hypothesis in code"),
        ("EVALUATION", "measured first"),
        ("SYSTEM", "shipped as a service"),
        ("REAL WORLD", "where it breaks"),
    ]
    body = MARKERS
    body += f'<path d="M{xs[-1]:.1f} {y - 14}C{xs[-1]:.1f} 22 {xs[0]:.1f} 22 {xs[0]:.1f} {y - 13}" class="wire-ac loop" marker-end="url(#b)"/>'
    body += '<text x="400" y="26" font-size="11.5" text-anchor="middle" class="mono ac">failures become the next dataset</text>'
    body += f'<path d="M{xs[0]:.1f} {y}H{xs[-1]:.1f}" class="rail"/>'
    body += f'<circle cx="{xs[0]:.1f}" cy="{y}" r="3" class="ac pulse"/>'
    for i, (x, (label, cap)) in enumerate(zip(xs, stations)):
        gate = label == "EVALUATION"
        if gate:
            body += f'<circle cx="{x:.1f}" cy="{y}" r="13" class="halo"/>'
            body += f'<circle cx="{x:.1f}" cy="{y}" r="6.5" class="ac"/>'
        else:
            body += f'<circle cx="{x:.1f}" cy="{y}" r="5.5" class="stop"/>'
        body += (
            f'<text x="{x:.1f}" y="{y + 36}" font-size="12.5" letter-spacing="1.5" text-anchor="middle" '
            f'class="mono b {"ac" if gate else "fg"}">{label}</text>'
        )
        body += f'<text x="{x:.1f}" y="{y + 55}" font-size="11" text-anchor="middle" class="mono mu">{cap}</text>'
    span = xs[-1] - xs[0]
    css = (
        ".rail{stroke:$fg;stroke-opacity:.28;stroke-width:1.3;fill:none}"
        ".stop{fill:$fg;fill-opacity:.06;stroke:$fg;stroke-opacity:.6;stroke-width:1.3}"
        ".halo{fill:$ac;fill-opacity:.14}"
        ".loop{stroke-dasharray:5 5;animation:march 1.6s linear infinite}"
        f".pulse{{opacity:0;animation:run 7s linear 1s infinite}}"
        "@keyframes march{to{stroke-dashoffset:-20}}"
        f"@keyframes run{{0%{{opacity:0;transform:translateX(0)}}6%{{opacity:1}}94%{{opacity:1}}100%{{opacity:0;transform:translateX({span:.1f}px)}}}}"
    )
    title = (
        "How the work moves: data, research, model, evaluation, system, real world. "
        "Evaluation is the gate, and failures in the real world loop back to become the next dataset."
    )
    write("method", W, 182, body, css, title)


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    header()
    buttons()
    terminal()
    fig_tbcgan()
    strips()
    method()
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.stat().st_size:>6} B  {f.name}")
