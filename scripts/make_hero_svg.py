"""Generate assets/hero.svg: an Xcode-like editor that types a SwiftUI body,
presses ▶ and renders the badge-style profile inside an iPhone.

GitHub strips JS from READMEs, so the whole thing is a CSS-animated loop.
Run: python3 scripts/make_hero_svg.py
"""
from pathlib import Path
from html import escape
import base64

AVATAR = Path(__file__).resolve().parent.parent / "assets" / "src" / "avatar-ig.jpg"
AVATAR_URI = "data:image/jpeg;base64," + base64.b64encode(AVATAR.read_bytes()).decode()
_clip_n = 0


def avatar(x, y, size, rx):
    """Embedded photo clipped to a rounded rect (rx=size/2 -> circle).
    Inlined (once, in <defs>) because GitHub won't let an SVG <img> fetch external images."""
    global _clip_n
    _clip_n += 1
    cid = f"av{_clip_n}"
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><use href="#avimg" transform="translate({x},{y}) scale({size / 100})"/></g>')

T = 16.0  # loop length, seconds
W, H = 880, 600
EDIT_W = 880
LINE_H = 19
CODE_X, CODE_Y = 52, 72

C = {
    "kw": "#FC5FA3", "str": "#FC6A5D", "num": "#D0BF69", "type": "#5DD8FF",
    "decl": "#67B7A4", "prop": "#A167E6", "txt": "#DFDFE0", "dim": "#6C7986",
}

# (tokens) per line; each token is (text, color key)
INITIAL = [
    [("import", "kw"), (" SwiftUI", "txt")],
    [],
    [("struct", "kw"), (" Hieu", "decl"), (" {", "txt")],
    [("    let", "kw"), (" role     = ", "txt"), ('"iOS Developer"', "str")],
    [("    let", "kw"), (" location = ", "txt"), ('"Hanoi, Vietnam"', "str")],
    [("    let", "kw"), (" since    = ", "txt"), ("2021", "num")],
    [("    let", "kw"), (" stack    = [", "txt"), ('"Swift"', "str"), (", ", "txt"),
     ('"SwiftUI"', "str"), (", ", "txt"), ('"C++"', "str"), (",", "txt")],
    [("                    ", "txt"), ('"PHP / Laravel"', "str"), (", ", "txt"),
     ('"MySQL"', "str"), ("]", "txt")],
    [("    let", "kw"), (" curious  = [", "txt"), ('"Rust"', "str"), (", ", "txt"),
     ('"RxSwift"', "str"), (", ", "txt"), ('"Claude"', "str"), (", ", "txt"), ('"GitHub"', "str"), ("]", "txt")],
    [("    let", "kw"), (" telegram = ", "txt"), ('"t.me/Hieeus1012"', "str")],
    [("}", "txt")],
]
TYPED = [
    [],
    [("struct", "kw"), (" ContentView", "decl"), (": ", "txt"), ("View", "type"), (" {", "txt")],
    [("    let", "kw"), (" me = ", "txt"), ("Hieu", "decl"), ("()", "txt")],
    [],
    [("    var", "kw"), (" body", "txt"), (": ", "txt"), ("some", "kw"), (" View", "type"), (" {", "txt")],
    [("        VStack", "type"), ("(alignment: .", "txt"), ("leading", "prop"), (") {", "txt")],
    [("            Text", "type"), ("(", "txt"), ('"Hieu Nguyen"', "str"), (").", "txt"), ("font", "prop"), ("(.", "txt"), ("largeTitle", "prop"), (")", "txt")],
    [("            Text", "type"), ("(", "txt"), ('"\\(me.role) · \\(me.location)"', "str"), (")", "txt")],
    [("            BadgeRow", "type"), ("(me.", "txt"), ("stack", "prop"), (")", "txt")],
    [("            BadgeRow", "type"), ("(me.", "txt"), ("curious", "prop"), (", style: .", "txt"), ("flat", "prop"), (")", "txt")],
    [("            Link", "type"), ("(", "txt"), ('"Telegram"', "str"), (", destination: me.", "txt"), ("telegram", "prop"), (")", "txt")],
    [("        }", "txt")],
    [("    }", "txt")],
    [("}", "txt")],
    [],
    [("#Preview", "kw"), (" { ", "txt"), ("ContentView", "decl"), ("() }", "txt")],
]
SCROLL = 0  # whole file fits, so `import SwiftUI` never scrolls out of view


def pct(sec):
    return f"{sec / T * 100:.2f}%"


keyframes = []
anim_rules = []
_n = 0


def animate(states, extra=""):
    """states: list of (second, css-declarations). Returns a class name."""
    global _n
    _n += 1
    name = f"a{_n}"
    frames = []
    for i, (sec, css) in enumerate(states):
        frames.append(f"{pct(sec)}{{{css}}}")
    if states[0][0] > 0:
        frames.insert(0, f"0%{{{states[0][1]}}}")
    if states[-1][0] < T:
        frames.append(f"100%{{{states[-1][1]}}}")
    keyframes.append(f"@keyframes {name}{{{''.join(frames)}}}")
    anim_rules.append(f".{name}{{animation:{name} {T}s infinite;{extra}}}")
    return name


def fade_in(start, dur=0.35, end=15.0, dy=6, dx=0):
    hidden = f"opacity:0;transform:translate({dx}px,{dy}px)"
    shown = "opacity:1;transform:translate(0,0)"
    return animate([(start, hidden), (start + dur, shown), (end, shown), (end + 0.6, hidden)])


def code_line(tokens, y):
    spans = "".join(
        f'<tspan fill="{C[c]}">{escape(t)}</tspan>' for t, c in tokens
    )
    return f'<text x="{CODE_X}" y="{y}" xml:space="preserve">{spans}</text>'


parts = []

# ---------- window chrome ----------
parts.append(f'''
<rect width="{W}" height="{H}" rx="14" fill="#1F1F24"/>
<rect width="{W}" height="40" rx="14" fill="#2A2A30"/>
<rect y="26" width="{W}" height="14" fill="#2A2A30"/>
<circle cx="22" cy="20" r="6" fill="#FF5F57"/><circle cx="42" cy="20" r="6" fill="#FEBC2E"/><circle cx="62" cy="20" r="6" fill="#28C840"/>
''')

# ---------- editor ----------
lines_total = len(INITIAL) + len(TYPED)
scroll_cls = animate([
    (2.4, "transform:translateY(0)"), (3.4, f"transform:translateY(-{SCROLL}px)"),
    (15.0, f"transform:translateY(-{SCROLL}px)"), (15.8, "transform:translateY(0)"),
], "animation-timing-function:cubic-bezier(.4,0,.2,1)")

code = []
for i, toks in enumerate(INITIAL):
    y = CODE_Y + i * LINE_H
    code.append(f'<text x="38" y="{y}" class="ln" text-anchor="end">{i + 1}</text>')
    code.append(code_line(toks, y))
for j, toks in enumerate(TYPED):
    i = len(INITIAL) + j
    y = CODE_Y + i * LINE_H
    cls = fade_in(3.0 + j * 0.24, dur=0.2, dy=0, dx=-8)
    code.append(f'<g class="{cls}"><text x="38" y="{y}" class="ln" text-anchor="end">{i + 1}</text>{code_line(toks, y)}</g>')

parts.append(f'''
<clipPath id="ed"><rect x="0" y="48" width="{EDIT_W}" height="{H - 56}"/></clipPath>
<g clip-path="url(#ed)" class="code"><g class="{scroll_cls}">{''.join(code)}</g></g>
''')

# ---------- play button (top trailing, in the title bar) ----------
BX, BY = W - 30, 20
press = animate([
    (7.55, "transform:scale(1)"), (7.7, "transform:scale(.8)"), (7.9, "transform:scale(1)"),
], "transform-box:fill-box;transform-origin:center")
glow = animate([(7.6, "opacity:0"), (7.75, "opacity:1"), (8.4, "opacity:0")])
parts.append(f'''
<g class="{press}">
  <circle cx="{BX}" cy="{BY}" r="11" fill="#3A3A42"/>
  <path d="M{BX - 3.5} {BY - 6} L{BX + 6} {BY} L{BX - 3.5} {BY + 6} Z" fill="#DFDFE0"/>
</g>
<circle cx="{BX}" cy="{BY}" r="15" fill="none" stroke="#0A84FF" stroke-width="2" class="{glow}"/>
''')
bar = animate([(7.9, "transform:scaleX(0);opacity:1"), (8.5, "transform:scaleX(1);opacity:1"),
               (8.7, "transform:scaleX(1);opacity:0")], "transform-box:fill-box;transform-origin:left")
parts.append(f'<rect x="0" y="40" width="{W}" height="2" fill="#0A84FF" class="{bar}"/>')

# ---------- rendered result: variant D inside an iPhone 18 Pro Max ----------
# Pro Max body is ~77.6 x 163 mm, so keep a ~1 : 2.1 ratio.
PW, PH = 236, 496
PX, PY = (W - PW) / 2, 56
IX, IW = PX + 18, PW - 36          # inner content box
CXP = PX + PW / 2
dim = animate([(8.3, "opacity:0"), (8.7, "opacity:.75"), (15.0, "opacity:.75"), (15.6, "opacity:0")])
phone = animate([
    (8.4, f"opacity:0;transform:translateY({H}px)"), (9.0, "opacity:1;transform:translateY(0)"),
    (15.0, "opacity:1;transform:translateY(0)"), (15.6, "opacity:0;transform:translateY(40px)"),
], "animation-timing-function:cubic-bezier(.2,.9,.25,1.05)")

ui_t = 10.0
def ui(el, k):
    return f'<g class="{fade_in(ui_t + k * 0.18, dur=0.35, dy=8, end=15.0)}">{el}</g>'

def label(x, y, text, size, color, weight=400, anchor="middle", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x:.1f}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}"'
            f' text-anchor="{anchor}"{ls} class="ui">{escape(text)}</text>')

def fill_row(items, y, h, gap, rx, size, weight=700, upper=False, spacing=0):
    """Badges stretched so the row always spans the full inner width.
    Width is shared by label length, so no label can overflow its box."""
    weights = [len(t) + 4 for t, *_ in items]
    free = IW - gap * (len(items) - 1)
    out, x = [], IX
    for (text, bg, fg), wt in zip(items, weights):
        w = free * wt / sum(weights)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{rx}" fill="{bg}"/>'
                   + label(x + w / 2, y + h / 2 + size * 0.36, text.upper() if upper else text, size, fg, weight, spacing=spacing))
        x += w + gap
    return "".join(out)

def section(y, title):
    return label(IX, y, title.upper(), 9.5, "#8B949E", 600, "start", 1.2)

top = PY + 50
parts.append(f'<rect x="0" y="40" width="{W}" height="{H - 40}" fill="#000" class="{dim}"/>')
parts.append(f'''<g class="{phone}">
  <rect x="{PX - 5}" y="{PY - 5}" width="{PW + 10}" height="{PH + 10}" rx="48" fill="#3A3A40"/>
  <rect x="{PX - 2}" y="{PY - 2}" width="{PW + 4}" height="{PH + 4}" rx="45" fill="#000"/>
  <rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="43" fill="#0D1117"/>
  <rect x="{CXP - 38}" y="{PY + 10}" width="76" height="22" rx="11" fill="#000"/>
  {label(PX + 36, PY + 26, "9:41", 11, "#E6EDF3", 600)}
  <rect x="{PX + PW - 44}" y="{PY + 17}" width="20" height="9" rx="2.5" fill="none" stroke="#E6EDF3" stroke-opacity=".6"/>
  <rect x="{PX + PW - 42}" y="{PY + 19}" width="14" height="5" rx="1" fill="#E6EDF3"/>
  <rect x="{CXP - 48}" y="{PY + PH - 12}" width="96" height="4" rx="2" fill="#E6EDF3" fill-opacity=".7"/>
''')
# header: avatar + name, centred
parts.append(ui(f'<circle cx="{CXP}" cy="{top + 30}" r="32" fill="url(#av)"/>'
                + avatar(CXP - 30, top, 60, 30), 0))
parts.append(ui(label(CXP, top + 92, "Hieu Nguyen", 22, "#E6EDF3", 700)
                + label(CXP, top + 112, "iOS Developer", 12.5, "#C9D1D9", 500)
                + label(CXP, top + 130, "Hanoi, Vietnam · since 2021", 11, "#8B949E"), 1))
parts.append(ui(f'<rect x="{IX}" y="{top + 146}" width="{IW}" height="1" fill="#30363D"/>', 2))
# stack
parts.append(ui(section(top + 172, "Stack")
                + fill_row([("Swift", "#F05138", "#fff"), ("SwiftUI", "#0A84FF", "#fff"), ("C++", "#00599C", "#fff")],
                           top + 182, 26, 6, 5, 9.5, upper=True, spacing=1)
                + fill_row([("PHP", "#777BB4", "#fff"), ("Laravel", "#FF2D20", "#fff"), ("MySQL", "#4479A1", "#fff")],
                           top + 214, 26, 6, 5, 9.5, upper=True, spacing=1), 3))
# curious
parts.append(ui(section(top + 270, "Curious about")
                + fill_row([("Rust", "#30363D", "#E6EDF3"), ("RxSwift", "#30363D", "#E6EDF3")], top + 280, 24, 6, 12, 11, 500)
                + fill_row([("Claude", "#D97757", "#fff"), ("GitHub", "#E6EDF3", "#0D1117")], top + 310, 24, 6, 12, 11, 600), 4))
# contact
parts.append(ui(section(top + 366, "Contact")
                + f'<rect x="{IX}" y="{top + 376}" width="{IW}" height="36" rx="12" fill="#26A5E4"/>'
                + label(CXP, top + 399, "Telegram  @Hieeus1012", 12.5, "#fff", 600), 5))
parts.append('</g>')
parts.append(f'<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath>')
parts.append('<defs><linearGradient id="av" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F05138"/><stop offset="1" stop-color="#FF9F0A"/></linearGradient></defs>')

# ---------- Xcode-style status in the title bar ----------
def status(text, color, a, b):
    cls = animate([(a, "opacity:0"), (a + 0.15, "opacity:1"), (b, "opacity:1"), (b + 0.15, "opacity:0")])
    return f'<text x="{W / 2}" y="25" fill="{color}" font-size="12" text-anchor="middle" class="ui {cls}">{text}</text>'
idle = animate([(0, "opacity:1"), (7.8, "opacity:1"), (7.9, "opacity:0"), (15.6, "opacity:0"), (15.8, "opacity:1")])
parts.append(f'<text x="{W / 2}" y="25" fill="#9A9AA2" font-size="12" text-anchor="middle" class="ui {idle}">Hieu.swift</text>')
parts.append(status("Building Hieu…", "#9A9AA2", 7.9, 8.5))
parts.append(status("✓ Build Succeeded", "#32D74B", 8.6, 9.6))
parts.append(status("Running Hieu on iPhone 18 Pro Max", "#9A9AA2", 9.7, 15.4))

# app launch splash
splash = animate([
    (8.9, "opacity:0;transform:scale(.3)"), (9.3, "opacity:1;transform:scale(1)"),
    (9.7, "opacity:1;transform:scale(1.05)"), (10.0, "opacity:0;transform:scale(2.2)"),
], "transform-box:fill-box;transform-origin:center")
parts.append(f'<g class="{splash}">' + avatar(CXP - 34, PY + PH / 2 - 34, 68, 16) + '</g>')

# push-style notification once the profile is on screen
nb = animate([
    (12.0, "opacity:0;transform:translateY(-70px)"), (12.45, "opacity:1;transform:translateY(0)"),
    (14.4, "opacity:1;transform:translateY(0)"), (14.8, "opacity:0;transform:translateY(-70px)"),
], "animation-timing-function:cubic-bezier(.2,.9,.25,1.1)")
NX, NY, NW = PX + 10, PY + 40, PW - 20
parts.append(f'''<clipPath id="scr"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="43"/></clipPath>
<g clip-path="url(#scr)"><g class="{nb}">
  <rect x="{NX}" y="{NY}" width="{NW}" height="56" rx="18" fill="#3A3A40" fill-opacity=".97" stroke="#fff" stroke-opacity=".08"/>
  {avatar(NX + 10, NY + 11, 34, 8)}
  {label(NX + 54, NY + 24, "Hieu", 12, "#fff", 600, "start")}
  {label(NX + NW - 12, NY + 24, "now", 10, "#A0A0A8", 400, "end")}
  {label(NX + 54, NY + 41, "Hello there! 👋", 11.5, "#E6E6EA", 400, "start")}
</g></g>''')


# fake pointer that travels to the play button and clicks
ptr = animate([
    (6.6, "opacity:0;transform:translate(560px,380px)"),
    (6.9, "opacity:1;transform:translate(560px,380px)"),
    (7.6, f"opacity:1;transform:translate({BX - 4}px,{BY - 2}px)"),
    (8.3, f"opacity:1;transform:translate({BX - 4}px,{BY - 2}px)"),
    (8.7, f"opacity:0;transform:translate({BX - 4}px,{BY - 2}px)"),
], "animation-timing-function:cubic-bezier(.4,0,.2,1)")
parts.append(f'<g class="{ptr}"><path d="M0 0 L0 17 L4.5 13 L7.5 20 L10 19 L7 12 L13 12 Z" fill="#fff" stroke="#000" stroke-width="1"/></g>')

style = f'''
.code text{{font-family:"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}}
.ln{{fill:#55555C}}
.mono{{font-family:"SF Mono",SFMono-Regular,Menlo,Consolas,monospace}}
.ui{{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Helvetica,Arial,sans-serif}}
{''.join(keyframes)}
{''.join(anim_rules)}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
'''

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Xcode-style animation: a Swift struct describing Hieu, an iOS developer in Hanoi, gets a SwiftUI ContentView and renders as a badge-style profile inside an iPhone.">
<style>{style}</style>
<defs><image id="avimg" href="{AVATAR_URI}" width="100" height="100" preserveAspectRatio="xMidYMid slice"/></defs>
<g clip-path="url(#win)">{''.join(parts)}</g>
</svg>
'''

out = Path(__file__).resolve().parent.parent / "assets" / "hero.svg"
out.parent.mkdir(exist_ok=True)
out.write_text(svg)
print(f"wrote {out} ({len(svg.encode()) / 1024:.1f} KB)")
