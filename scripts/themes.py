"""Seasonal layers for hero.svg: the pixel mascot crew (every day) and Tết decorations.

Each builder returns (svg_markup, css). Everything is pure CSS animation so it
still runs inside a GitHub README <img>.
"""
from html import escape
import random

import lunar


def tet_window(year):
    """(23 tháng Chạp, mùng 1 Tết, mùng 10) as solar dates for the lunar year starting in `year`."""
    return (lunar.lunar_to_solar(23, 12, year - 1), lunar.lunar_to_solar(1, 1, year),
            lunar.lunar_to_solar(10, 1, year))


def tet_for(today):
    """(year, can_chi, animal, emoji) while `today` is between 23 tháng Chạp and mùng 10, else None.
    Computed from the lunar calendar, so it never needs a manual update."""
    for year in (today.year, today.year + 1):
        start, _, end = tet_window(year)
        if start <= today <= end:
            return (year, *lunar.year_name(year))
    return None


def next_tet(today):
    """The upcoming (or current) Tết, for previewing the theme out of season."""
    year = today.year if tet_window(today.year)[2] >= today else today.year + 1
    return (year, *lunar.year_name(year))


# ---------------------------------------------------------------- mascots
ORANGE, DARK = "#D97757", "#1F1F24"
PX = 4  # one "pixel" of the sprite


def _px(x, y, w=1, h=1, fill=ORANGE, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<rect x="{x * PX}" y="{y * PX}" width="{w * PX}" height="{h * PX}" fill="{fill}"{c}/>'


def sprite():
    """12x8 pixel creature: square body, side nubs, two eyes, four stepping legs."""
    return (
        _px(1, 0, 10, 6) + _px(0, 2, 1, 2) + _px(11, 2, 1, 2)
        + _px(3, 2, 1, 2, DARK) + _px(8, 2, 1, 2, DARK)
        + f'<g class="legA">{_px(2, 6, 1, 2)}{_px(7, 6, 1, 2)}</g>'
        + f'<g class="legB">{_px(4, 6, 1, 2)}{_px(9, 6, 1, 2)}</g>'
    )


def mascots(x0, y0, comment_color="#6C7986"):
    """Four stations stacked in the empty right column of the editor."""
    s = []
    gap = 115

    def label(y, text):
        return (f'<text x="{x0}" y="{y}" font-size="11.5" fill="{comment_color}" class="mono">'
                f'// {escape(text)}</text>')

    # 1. bug hunter: chases a bug across the station, squashes it, repeats
    y = y0
    s.append(label(y, "hunting bugs"))
    s.append(f'''<g class="hunt" transform="translate({x0},{y + 30})">
  <g class="chaser"><g class="bob">{sprite()}</g>
    <circle cx="58" cy="14" r="7" fill="none" stroke="#C8C8CE" stroke-width="2.5"/>
    <line x1="52" y1="20" x2="47" y2="26" stroke="#C8C8CE" stroke-width="3" stroke-linecap="round"/></g>
  <g class="bug" transform="translate(96,20)">
    <rect x="0" y="0" width="12" height="8" rx="3" fill="#32D74B"/>
    <rect x="9" y="1" width="5" height="6" rx="2" fill="#1E9E3A"/>
    <line x1="2" y1="8" x2="0" y2="12" stroke="#32D74B" stroke-width="1.5"/>
    <line x1="6" y1="8" x2="6" y2="12" stroke="#32D74B" stroke-width="1.5"/>
    <line x1="10" y1="8" x2="12" y2="12" stroke="#32D74B" stroke-width="1.5"/>
  </g>
  <text x="104" y="30" font-size="14" fill="#FFD60A" text-anchor="middle" class="ui squash">✦</text>
</g>''')

    # 2. builder: hammers while code blocks stack up
    y = y0 + gap
    s.append(label(y, "building features"))
    blocks = "".join(
        f'<g class="blk blk{i}"><rect x="{120 + i * 34}" y="{32 - i * 0}" width="30" height="20" rx="4" fill="#2C2C34" stroke="#3A3A42"/>'
        f'<text x="{135 + i * 34}" y="{46}" font-size="10" fill="{c}" text-anchor="middle" class="mono">{t}</text></g>'
        for i, (t, c) in enumerate([("{ }", "#5DD8FF"), ("fn", "#FC5FA3"), ("✓", "#32D74B")])
    )
    s.append(f'''<g transform="translate({x0},{y + 18})">
  <g class="bob" transform="translate(0,12)">{sprite()}</g>
  <g class="hammer"><rect x="54" y="6" width="4" height="26" rx="2" fill="#A07050"/><rect x="47" y="2" width="18" height="9" rx="2" fill="#9A9AA2"/></g>
  {blocks}
</g>''')

    # 3. painter: brushes colour into a tiny iPhone wireframe
    y = y0 + 2 * gap
    s.append(label(y, "drawing UI"))
    strokes = "".join(
        f'<rect x="138" y="{12 + i * 13}" width="44" height="8" rx="3" fill="{c}" class="paint paint{i}"/>'
        for i, c in enumerate(["#F05138", "#0A84FF", "#32D74B", "#BF5AF2"])
    )
    s.append(f'''<g transform="translate({x0},{y + 14})">
  <g class="bob" transform="translate(0,26)">{sprite()}</g>
  <g class="brush"><line x1="56" y1="40" x2="104" y2="22" stroke="#C8C8CE" stroke-width="3" stroke-linecap="round"/><circle cx="106" cy="21" r="4" fill="#FF9F0A"/></g>
  <rect x="128" y="0" width="64" height="66" rx="10" fill="#0D1117" stroke="#3A3A42" stroke-width="2"/>
  {strokes}
</g>''')

    # 4. manager: paces with a clipboard, ticking off a checklist
    y = y0 + 3 * gap
    s.append(label(y, "planning & design"))
    checks = "".join(
        f'<g transform="translate(150,{14 + i * 16})"><rect width="10" height="10" rx="2" fill="none" stroke="#5A5A64"/>'
        f'<path d="M2 5 L4.5 7.5 L8.5 2.5" fill="none" stroke="#32D74B" stroke-width="2" class="tick tick{i}"/>'
        f'<rect x="16" y="3" width="{[60, 44, 52][i]}" height="4" rx="2" fill="#3A3A42"/></g>'
        for i in range(3)
    )
    s.append(f'''<g transform="translate({x0},{y + 18})">
  <g class="pace"><g class="bob" transform="translate(0,16)">{sprite()}</g>
    <rect x="50" y="18" width="16" height="20" rx="2" fill="#E6EDF3"/><rect x="54" y="15" width="8" height="5" rx="1" fill="#9A9AA2"/>
    <rect x="53" y="24" width="10" height="2" fill="#9A9AA2"/><rect x="53" y="29" width="8" height="2" fill="#9A9AA2"/></g>
  {checks}
</g>''')

    css = """
.legA{animation:legA .36s steps(1) infinite}.legB{animation:legB .36s steps(1) infinite}
@keyframes legA{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes legB{0%{transform:translateY(-3px)}50%{transform:translateY(0)}}
.bob{animation:bob .36s steps(1) infinite}
@keyframes bob{0%{translate:0 0}50%{translate:0 -2px}}
.hunt .bug{animation:bug 4s linear infinite}
@keyframes bug{0%{transform:translate(96px,20px);opacity:1}70%{transform:translate(190px,20px);opacity:1}78%,100%{transform:translate(190px,20px);opacity:0}}
.chaser{animation:chase 4s linear infinite}
@keyframes chase{0%{transform:translateX(0)}78%{transform:translateX(126px)}88%{transform:translateX(126px);opacity:1}96%{opacity:0}100%{transform:translateX(0);opacity:0}}
.squash{opacity:0;animation:squash 4s infinite}
@keyframes squash{0%,74%{opacity:0;transform:translate(86px,0) scale(.5)}80%{opacity:1;transform:translate(86px,0) scale(1.4)}90%,100%{opacity:0;transform:translate(86px,0) scale(1.4)}}
.hammer{transform-box:fill-box;transform-origin:50% 100%;animation:hammer .5s ease-in infinite}
@keyframes hammer{0%{transform:rotate(-35deg)}60%{transform:rotate(25deg)}100%{transform:rotate(-35deg)}}
.blk{animation:3s infinite}.blk0{animation-name:b0}.blk1{animation-name:b1}.blk2{animation-name:b2}
@keyframes b0{0%,10%{opacity:0;transform:translateY(-8px)}20%,90%{opacity:1;transform:translateY(0)}100%{opacity:0}}
@keyframes b1{0%,35%{opacity:0;transform:translateY(-8px)}45%,90%{opacity:1;transform:translateY(0)}100%{opacity:0}}
@keyframes b2{0%,60%{opacity:0;transform:translateY(-8px)}70%,90%{opacity:1;transform:translateY(0)}100%{opacity:0}}
.brush{transform-box:fill-box;transform-origin:0 100%;animation:brush .8s ease-in-out infinite alternate}
@keyframes brush{0%{transform:rotate(-8deg)}100%{transform:rotate(14deg)}}
.paint{transform-box:fill-box;transform-origin:left;animation:4s infinite}
.paint0{animation-name:p0}.paint1{animation-name:p1}.paint2{animation-name:p2}.paint3{animation-name:p3}
@keyframes p0{0%,5%{transform:scaleX(0)}20%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}
@keyframes p1{0%,22%{transform:scaleX(0)}37%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}
@keyframes p2{0%,39%{transform:scaleX(0)}54%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}
@keyframes p3{0%,56%{transform:scaleX(0)}71%,92%{transform:scaleX(1)}100%{transform:scaleX(0)}}
.pace{animation:pace 5s ease-in-out infinite alternate}
@keyframes pace{0%{transform:translateX(0)}100%{transform:translateX(70px)}}
.tick{stroke-dasharray:12;animation:4.5s infinite}.tick0{animation-name:t0}.tick1{animation-name:t1}.tick2{animation-name:t2}
@keyframes t0{0%,15%{stroke-dashoffset:12}25%,92%{stroke-dashoffset:0}100%{stroke-dashoffset:12}}
@keyframes t1{0%,40%{stroke-dashoffset:12}50%,92%{stroke-dashoffset:0}100%{stroke-dashoffset:12}}
@keyframes t2{0%,65%{stroke-dashoffset:12}75%,92%{stroke-dashoffset:0}100%{stroke-dashoffset:12}}
"""
    return "".join(s), css


# ---------------------------------------------------------------- Tết
def blossom(cx, cy, r, cls=""):
    c = f' class="{cls}"' if cls else ""
    petals = "".join(
        f'<ellipse cx="{cx}" cy="{cy - r * 0.55:.1f}" rx="{r * 0.42:.1f}" ry="{r * 0.55:.1f}" fill="#FFB3C7" transform="rotate({a} {cx} {cy})"/>'
        for a in range(0, 360, 72)
    )
    return f'<g{c}>{petals}<circle cx="{cx}" cy="{cy}" r="{r * 0.28:.1f}" fill="#FF5C8A"/></g>'


def peach_branch():
    """Hangs along the title bar, clear of the traffic lights and the code."""
    flowers = [(140, 18, 7), (180, 30, 8), (218, 14, 6), (256, 32, 8), (296, 22, 7), (330, 38, 6)]
    buds = [(160, 12), (238, 24), (316, 30), (346, 44)]
    return (
        '<path d="M96 6 C160 32 210 8 260 26 S320 24 350 46" fill="none" stroke="#6B3E26" stroke-width="3.5" stroke-linecap="round"/>'
        '<path d="M196 20 L206 4 M284 26 L296 44 M322 30 L334 14" stroke="#6B3E26" stroke-width="2" stroke-linecap="round"/>'
        + "".join(blossom(x, y, r) for x, y, r in flowers)
        + "".join(f'<circle cx="{x}" cy="{y}" r="3" fill="#FF7FA3"/>' for x, y in buds)
    )


def falling_petals(W, H, n=16, seed=7):
    rnd = random.Random(seed)
    out, css = [], []
    for i in range(n):
        x = rnd.uniform(20, W - 20)
        dur = rnd.uniform(7, 12)
        delay = -rnd.uniform(0, dur)
        drift = rnd.uniform(-80, 80)
        r = rnd.uniform(4, 7)
        out.append(f'<g class="pt{i}">{blossom(x, -12, r)}</g>')
        css.append(f".pt{i}{{animation:pt{i} {dur:.1f}s linear {delay:.1f}s infinite}}"
                   f"@keyframes pt{i}{{0%{{transform:translate(0,0) rotate(0)}}100%{{transform:translate({drift:.0f}px,{H + 30}px) rotate({rnd.choice([-1, 1]) * 540}deg)}}}}")
    css.append("[class^=pt]{transform-box:fill-box;transform-origin:center}")
    return "".join(out), "".join(css)


def fireworks(spots):
    """Rocket trail rises, flashes, then two glowing rings of sparks burst out,
    droop under 'gravity' and twinkle out. spots: [(x, y, radius, delay, (outer, inner))]."""
    rnd = random.Random(3)
    out, css = [], []
    cyc = 2.8
    for i, (x, y, r, delay, (c_out, c_in)) in enumerate(spots):
        outer = "".join(f'<g transform="rotate({a})"><circle r="2.6" fill="{c_out}" class="fo{i}"/>'
                        f'<line y1="0" y2="9" stroke="{c_out}" stroke-width="1.6" stroke-linecap="round" class="fo{i} tail"/></g>'
                        for a in range(0, 360, 15))
        inner = "".join(f'<g transform="rotate({a + 7})"><circle r="2" fill="{c_in}" class="fi{i}"/></g>'
                        for a in range(0, 360, 30))
        sparks = "".join(f'<circle cx="{rnd.uniform(-r, r):.0f}" cy="{rnd.uniform(-r, r * .8):.0f}" r="1.4" fill="#FFF6D5" class="tw{i}"/>'
                         for _ in range(10))
        out.append(f'<g transform="translate({x},{y})" filter="url(#glow)">'
                   f'<g class="rk{i}"><circle r="2.4" fill="#FFE8A3"/><line y1="2" y2="26" stroke="#FFD27A" stroke-width="2" stroke-linecap="round" opacity=".6"/></g>'
                   f'<circle r="9" fill="#FFFFFF" class="fl{i}"/>'
                   f'<g class="gr{i}">{outer}{inner}{sparks}</g></g>')
        d = f"animation-duration:{cyc}s;animation-delay:{delay}s;animation-iteration-count:infinite"
        css.append(
            f".rk{i}{{animation-name:rk{i};animation-timing-function:cubic-bezier(.2,.6,.4,1);{d}}}"
            f"@keyframes rk{i}{{0%{{opacity:0;transform:translateY(150px)}}4%{{opacity:1}}24%{{opacity:1;transform:translateY(0)}}26%,100%{{opacity:0;transform:translateY(0)}}}}"
            f".fl{i}{{transform-box:fill-box;transform-origin:center;animation-name:fl{i};{d}}}"
            f"@keyframes fl{i}{{0%,24%{{opacity:0;transform:scale(.2)}}27%{{opacity:.9;transform:scale(1)}}36%,100%{{opacity:0;transform:scale(1.6)}}}}"
            f".fo{i}{{animation-name:fo{i};animation-timing-function:cubic-bezier(.1,.7,.3,1);{d}}}"
            f"@keyframes fo{i}{{0%,25%{{opacity:0;transform:translateY(0)}}28%{{opacity:1}}62%{{opacity:1;transform:translateY(-{r}px)}}88%,100%{{opacity:0;transform:translateY(-{r * 1.08:.0f}px)}}}}"
            f".fi{i}{{animation-name:fi{i};animation-timing-function:cubic-bezier(.1,.7,.3,1);{d}}}"
            f"@keyframes fi{i}{{0%,27%{{opacity:0;transform:translateY(0)}}31%{{opacity:1}}60%{{opacity:1;transform:translateY(-{r * .55:.0f}px)}}84%,100%{{opacity:0;transform:translateY(-{r * .6:.0f}px)}}}}"
            f".gr{i}{{animation-name:gr{i};animation-timing-function:ease-in;{d}}}"
            f"@keyframes gr{i}{{0%,30%{{transform:translateY(0)}}90%,100%{{transform:translateY(14px)}}}}"
            f".tw{i}{{animation-name:tw{i};animation-timing-function:steps(1);{d}}}"
            f"@keyframes tw{i}{{0%,58%{{opacity:0}}62%{{opacity:1}}68%{{opacity:.2}}72%{{opacity:1}}78%{{opacity:.3}}84%,100%{{opacity:0}}}}")
    css.append(".tail{opacity:.55}")
    defs = ('<defs><filter id="glow" x="-50%" y="-50%" width="200%" height="200%">'
            '<feGaussianBlur stdDeviation="1.6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>')
    return defs + "".join(out), "".join(css)
