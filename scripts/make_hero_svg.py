"""Generate assets/hero.svg — a looping "Claude Code builds my profile app" story:

  1. full-window terminal: `claude`, welcome screen, `/ios-project-bootstrap …`
  2. terminal shrinks into a left sidebar log; the Claude mascot walks into the
     main pane and works through: plan → UI → code
  3. a bug crawls onto the code; the mascot leaves its spot, chases and whacks it
  4. build ▶ → Simulator iPhone shows the profile + a push notification

GitHub strips JS from READMEs, so everything is CSS animation inside one SVG.
Run: python3 scripts/make_hero_svg.py [--theme auto|normal|tet] [--date YYYY-MM-DD] [--out PATH]
"auto" switches to the Tết theme from 23 tháng Chạp to mùng 10, computed from the lunar calendar.
"""
from pathlib import Path
from html import escape
from datetime import date
import argparse
import base64

import themes

ap = argparse.ArgumentParser()
ap.add_argument("--theme", choices=["auto", "normal", "tet"], default="auto")
ap.add_argument("--date", type=date.fromisoformat, default=date.today(),
                help="pretend today is this date (to preview a season)")
ap.add_argument("--out", default=None)
args = ap.parse_args()

TET_INFO = themes.tet_for(args.date)
if args.theme == "tet" and not TET_INFO:
    TET_INFO = themes.next_tet(args.date)
if args.theme == "normal":
    TET_INFO = None

ROOT = Path(__file__).resolve().parent.parent
AVATAR_URI = "data:image/jpeg;base64," + base64.b64encode((ROOT / "assets/src/avatar-ig.jpg").read_bytes()).decode()

T = 26.4                 # loop length, seconds
W, H = 880, 660
SIDE_W = 300             # terminal sidebar once the window splits
MAIN_X = SIDE_W          # main pane starts here
MAIN_CX = MAIN_X + (W - MAIN_X) / 2

# ---------------------------------------------------------------- timeline (seconds)
SPLIT = 4.0              # full terminal -> sidebar + main pane
PLAN = (4.4, 7.6)
UI = (7.8, 10.6)
CODE = (10.8, 14.2)
BUG = (14.4, 18.8)
BUILD = 19.1             # ▶ pressed
SIM = 20.0               # phone slides in
END = 25.8               # everything fades back to the terminal

C = {
    "kw": "#FC5FA3", "str": "#FC6A5D", "num": "#D0BF69", "type": "#5DD8FF",
    "decl": "#67B7A4", "prop": "#A167E6", "txt": "#DFDFE0", "dim": "#6C7986",
}
ORANGE = "#D97757"
MONO = '"SF Mono",SFMono-Regular,Menlo,Consolas,monospace'

# ---------------------------------------------------------------- animation helpers
keyframes, anim_rules = [], []
_n = 0


def pct(sec):
    return f"{max(0, min(sec, T)) / T * 100:.2f}%"


def animate(states, extra=""):
    """states: [(second, css)], held flat before the first / after the last. Returns a class."""
    global _n
    _n += 1
    name = f"a{_n}"
    frames = [f"{pct(s)}{{{css}}}" for s, css in states]
    if states[0][0] > 0:
        frames.insert(0, f"0%{{{states[0][1]}}}")
    if states[-1][0] < T:
        frames.append(f"100%{{{states[-1][1]}}}")
    keyframes.append(f"@keyframes {name}{{{''.join(frames)}}}")
    anim_rules.append(f".{name}{{animation:{name} {T}s infinite;{extra}}}")
    return name


def show(start, end=END, dur=0.35, dy=6, dx=0):
    """Visible from `start` to `end`, sliding in by (dx, dy)."""
    hidden = f"opacity:0;transform:translate({dx}px,{dy}px)"
    shown = "opacity:1;transform:translate(0,0)"
    return animate([(start, hidden), (start + dur, shown), (end, shown), (end + 0.4, hidden)])


def g(cls, inner):
    return f'<g class="{cls}">{inner}</g>'


def text(x, y, s, size=12.5, fill="#DFDFE0", weight=400, anchor="start", mono=True, extra=""):
    fam = "mono" if mono else "ui"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}" class="{fam}" xml:space="preserve"{extra}>{escape(s)}</text>')


def typed(x, y, s, start, dur, bg, **kw):
    """Text revealed left-to-right by shrinking a background-coloured cover."""
    size = kw.get("size", 12.5)
    w = len(s) * size * 0.61 + 6
    steps = max(len(s), 1)
    cover = animate([(start, "transform:scaleX(1)"), (start + dur, "transform:scaleX(0)")],
                    f"transform-box:fill-box;transform-origin:right;animation-timing-function:steps({steps})")
    return text(x, y, s, **kw) + f'<rect x="{x - 1}" y="{y - size}" width="{w:.0f}" height="{size + 5}" fill="{bg}" class="{cover}"/>'


def code_line(tokens, x, y):
    spans = "".join(f'<tspan fill="{C[c]}">{escape(t)}</tspan>' for t, c in tokens)
    return f'<text x="{x}" y="{y}" class="mono code" xml:space="preserve">{spans}</text>'


_clip_n = 0


def avatar(x, y, size, rx):
    global _clip_n
    _clip_n += 1
    cid = f"av{_clip_n}"
    return (f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{rx}"/></clipPath>'
            f'<g clip-path="url(#{cid})"><use href="#avimg" transform="translate({x},{y}) scale({size / 100})"/></g>')


parts = []
extra_css = []

# ---------------------------------------------------------------- window chrome
TERM_BG, MAIN_BG = "#141418", "#1F1F24"
parts.append(f'''
<rect width="{W}" height="{H}" rx="14" fill="{TERM_BG}"/>
<rect width="{W}" height="40" rx="14" fill="#2A2A30"/><rect y="26" width="{W}" height="14" fill="#2A2A30"/>
<circle cx="22" cy="20" r="6" fill="#FF5F57"/><circle cx="42" cy="20" r="6" fill="#FEBC2E"/><circle cx="62" cy="20" r="6" fill="#28C840"/>
''')

# ---------------------------------------------------------------- 1. full-window terminal
TX = 28
full = []
full.append(text(TX, 74, "~/apps $", fill="#32D74B"))
full.append(typed(TX + 72, 74, "claude", 0.3, 0.5, TERM_BG))
welcome = (f'<rect x="{TX - 6}" y="94" width="470" height="84" rx="10" fill="none" stroke="{ORANGE}" stroke-width="1.5"/>'
           + text(TX + 80, 128, "✻ Welcome to Claude Code", 15, "#F2F2F4", 700)
           + text(TX + 80, 152, "/help for help · cwd: ~/apps", 12, "#8B8B93"))
full.append(g(show(0.9, SPLIT - 0.2, dy=4), welcome))
full.append(g(show(1.3, SPLIT - 0.2, dy=0), text(TX, 214, ">", fill=ORANGE, weight=700)))
full.append(g(show(1.3, SPLIT - 0.2, dy=0), typed(TX + 18, 214, "/ios-project-bootstrap Hieu's profile app", 1.5, 1.4, TERM_BG)))
hint = (f'<rect x="{TX + 12}" y="226" width="430" height="26" rx="6" fill="#26262C"/>'
        + text(TX + 22, 244, "/ios-project-bootstrap", 12, ORANGE, 600)
        + text(TX + 196, 244, "Bootstrap a SwiftUI iOS app", 12, "#8B8B93"))
full.append(g(show(1.8, 2.9, dy=-4), hint))
full.append(g(show(3.0, SPLIT - 0.2, dy=0), text(TX + 18, 240, "⎿  Running skill ios-project-bootstrap…", 12, "#8B8B93")))
parts.append(g(animate([(0, "opacity:1"), (SPLIT - 0.1, "opacity:1"), (SPLIT + 0.3, "opacity:0"),
                        (T - 0.4, "opacity:0"), (T, "opacity:1")]), "".join(full)))

# ---------------------------------------------------------------- 2. split: main pane + sidebar log
main_in = animate([(SPLIT, "transform:translateX(620px)"), (SPLIT + 0.5, "transform:translateX(0)"),
                   (END, "transform:translateX(0)"), (END + 0.5, "transform:translateX(620px)")],
                  "animation-timing-function:cubic-bezier(.2,.8,.2,1)")
parts.append(f'<g class="{main_in}"><rect x="{MAIN_X}" y="40" width="{W - MAIN_X}" height="{H - 40}" fill="{MAIN_BG}"/>'
             f'<line x1="{MAIN_X}" y1="40" x2="{MAIN_X}" y2="{H}" stroke="#34343B"/></g>')

SX = 20
side = [text(SX, 78, "~/apps $ claude", 12, "#6C6C74"),
        text(SX, 106, "> /ios-project-bootstrap", 12, ORANGE, 600),
        text(SX + 14, 126, "Hieu's profile app", 12, "#C8C8CE")]
STEPS = [("Plan the project", PLAN), ("Design the UI", UI), ("Write ContentView.swift", CODE),
         ("Hunt down the bug", BUG), ("Build & run", (BUILD, SIM))]
for i, (name, (a, b)) in enumerate(STEPS):
    y = 170 + i * 36
    dot = animate([(a, "opacity:0"), (a + 0.2, "opacity:1"), (b, "opacity:1"), (b + 0.1, "opacity:0")])
    tick = animate([(b, "opacity:0"), (b + 0.15, "opacity:1"), (END, "opacity:1"), (END + 0.3, "opacity:0")])
    row = show(a, dy=0, dx=-8)
    side.append(f'<g class="{row}">'
                + f'<text x="{SX}" y="{y}" font-size="12" fill="{ORANGE}" class="mono {dot}">●</text>'
                + f'<text x="{SX}" y="{y}" font-size="12" fill="#32D74B" class="mono {tick}">✓</text>'
                + text(SX + 18, y, name, 12, "#DFDFE0") + '</g>')
side.append(g(show(SIM + 0.4, dy=0, dx=-8),
              text(SX, 170 + 5 * 36 + 4, "⎿  Running on iPhone 18 Pro Max", 12, "#32D74B")))
for label_, (a, b) in [("✻ Planning…", PLAN), ("✻ Designing UI…", UI), ("✻ Writing code…", CODE),
                       ("✻ Hunting a bug…", BUG), ("✻ Building…", (BUILD, SIM))]:
    side.append(g(animate([(a, "opacity:0"), (a + 0.2, "opacity:1"), (b, "opacity:1"), (b + 0.2, "opacity:0")]),
                  text(SX, H - 70, label_, 12, ORANGE)))
side.append(f'<rect x="{SX - 4}" y="{H - 50}" width="{SIDE_W - 2 * SX + 8}" height="30" rx="8" fill="none" stroke="#3A3A42"/>'
            + text(SX + 6, H - 30, ">", 12, "#6C6C74"))
parts.append(g(show(SPLIT + 0.2, dy=0, dx=-10), "".join(side)))

# ---------------------------------------------------------------- 2a. plan board
PX0 = MAIN_X + 40
plan = [text(PX0, 96, "📋 Plan · Hieu's profile app", 15, "#F2F2F4", 700, mono=False)]
for i, item in enumerate(["Scaffold SwiftUI project", "Design profile screen", "Write ContentView",
                          "Fix bugs", "Build & run on iPhone"]):
    y = 146 + i * 44
    t0 = PLAN[0] + 0.6 + i * 0.5
    tick = animate([(t0, "stroke-dashoffset:14"), (t0 + 0.25, "stroke-dashoffset:0")], "stroke-dasharray:14")
    plan.append(f'<rect x="{PX0}" y="{y - 13}" width="16" height="16" rx="4" fill="none" stroke="#5A5A64"/>'
                f'<path d="M{PX0 + 3} {y - 5} l3.5 3.5 l6 -7" fill="none" stroke="#32D74B" stroke-width="2.2" class="{tick}"/>'
                + text(PX0 + 28, y, item, 13.5, "#DFDFE0", mono=False))
parts.append(g(show(PLAN[0], PLAN[1], dx=12, dy=0), "".join(plan)))

# ---------------------------------------------------------------- 2b. UI wireframe being painted
FX, FY, FW, FH = MAIN_X + 310, 120, 170, 350
ui = [f'<rect x="{FX}" y="{FY}" width="{FW}" height="{FH}" rx="26" fill="#0D1117" stroke="#3A3A42" stroke-width="2"/>',
      f'<rect x="{FX + FW / 2 - 26}" y="{FY + 8}" width="52" height="14" rx="7" fill="#000"/>',
      text(MAIN_X + 40, 96, "🎨 Designing the profile screen", 15, "#F2F2F4", 700, mono=False)]
pieces = [
    f'<circle cx="{FX + FW / 2}" cy="{FY + 72}" r="24" fill="#F05138"/>',
    f'<rect x="{FX + 35}" y="{FY + 108}" width="{FW - 70}" height="12" rx="6" fill="#E6EDF3"/>',
    f'<rect x="{FX + 50}" y="{FY + 128}" width="{FW - 100}" height="8" rx="4" fill="#8B949E"/>',
    "".join(f'<rect x="{FX + 16 + j * 48}" y="{FY + 156}" width="42" height="16" rx="4" fill="{c}"/>'
            for j, c in enumerate(["#F05138", "#0A84FF", "#00599C"])),
    "".join(f'<rect x="{FX + 16 + j * 48}" y="{FY + 178}" width="42" height="16" rx="4" fill="{c}"/>'
            for j, c in enumerate(["#777BB4", "#FF2D20", "#4479A1"])),
    "".join(f'<rect x="{FX + 16 + j * 72}" y="{FY + 214}" width="66" height="14" rx="7" fill="{c}"/>'
            for j, c in enumerate(["#D97757", "#E6EDF3"])),
    f'<rect x="{FX + 16}" y="{FY + 290}" width="{FW - 32}" height="26" rx="9" fill="#26A5E4"/>',
]
for i, p in enumerate(pieces):
    ui.append(g(animate([(UI[0] + 0.5 + i * 0.3, "opacity:0;transform:scale(.6)"),
                         (UI[0] + 0.75 + i * 0.3, "opacity:1;transform:scale(1)")],
                        "transform-box:fill-box;transform-origin:center"), p))
parts.append(g(show(UI[0], UI[1], dx=12, dy=0), "".join(ui)))

# ---------------------------------------------------------------- 2c. code
LINES = [
    [("import", "kw"), (" SwiftUI", "txt")],
    [],
    [("struct", "kw"), (" Hieu", "decl"), (" {", "txt")],
    [("    let", "kw"), (" role     = ", "txt"), ('"iOS Developer"', "str")],
    [("    let", "kw"), (" location = ", "txt"), ('"Hanoi, Vietnam"', "str")],
    [("    let", "kw"), (" since    = ", "txt"), ("2021", "num")],
    [("    let", "kw"), (" stack    = [", "txt"), ('"Swift"', "str"), (", ", "txt"), ('"SwiftUI"', "str"), (", ", "txt"), ('"C++"', "str"), (",", "txt")],
    [("                    ", "txt"), ('"PHP / Laravel"', "str"), (", ", "txt"), ('"MySQL"', "str"), ("]", "txt")],
    [("    let", "kw"), (" curious  = [", "txt"), ('"Rust"', "str"), (", ", "txt"), ('"RxSwift"', "str"), (", ", "txt"), ('"Claude"', "str"), (", ", "txt"), ('"GitHub"', "str"), ("]", "txt")],
    [("    let", "kw"), (" telegram = ", "txt"), ('"t.me/Hieeus1012"', "str")],
    [("}", "txt")],
    [],
    [("struct", "kw"), (" ContentView", "decl"), (": ", "txt"), ("View", "type"), (" {", "txt")],
    [("    let", "kw"), (" me = ", "txt"), ("Hieu", "decl"), ("()", "txt")],
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
CX0, CY0, LH = MAIN_X + 50, 84, 20
CW = 12.5 * 0.6  # mono char width
code = []
per = (CODE[1] - CODE[0] - 0.4) / len(LINES)
for i, toks in enumerate(LINES):
    y = CY0 + i * LH
    ln = text(CX0 - 12, y, str(i + 1), 11, "#55555C", anchor="end")
    code.append(g(show(CODE[0] + 0.2 + i * per, dur=0.15, dx=-6, dy=0), ln + code_line(toks, CX0, y)))

# ---- the bug hops between three spots, leaving an error at each; Claude chases it,
# misses twice (fixing the error the bug left behind), then squashes it on the third.
SPOTS = [(6, 20, 44, "✕ Syntax error"), (17, 17, 46, "✕ Unknown 'me'"), (19, 12, 46, "✕ Type mismatch")]
ARRIVE = [BUG[0], BUG[0] + 1.35, BUG[0] + 2.6]   # bug lands on spot i
HIT = [BUG[0] + 0.85, BUG[0] + 2.1, BUG[0] + 3.45]  # hammer comes down on spot i
MSG_X = CX0 + 50 * CW


def cx(c):
    return CX0 + c * CW


def bug_pos(i):
    line, c0, c1, _ = SPOTS[i]
    y = CY0 + line * LH - 17
    return cx(c1) - 8, cx((c0 + c1) / 2), y


for i, (line, c0, c1, msg) in enumerate(SPOTS):
    uy = CY0 + line * LH + 4
    n = int((cx(c1) - cx(c0)) / 6)
    squiggle = f'<path d="M{cx(c0):.0f} {uy} q3 -3 6 0' + " t6 0" * (n - 1) + '" fill="none" stroke="#FF453A" stroke-width="1.5"/>'
    fixed_at = HIT[i] + (0.25 if i < len(SPOTS) - 1 else 0.35)
    fixed_until = BUILD + 0.5 if i == len(SPOTS) - 1 else fixed_at + 1.4
    code.append(g(animate([(ARRIVE[i], "opacity:0"), (ARRIVE[i] + 0.12, "opacity:1"), (fixed_at, "opacity:1"), (fixed_at + 0.1, "opacity:0")]),
                  squiggle + text(MSG_X, uy - 2, msg, 10.5, "#FF453A", 600)))
    code.append(g(animate([(fixed_at, "opacity:0"), (fixed_at + 0.15, "opacity:1"), (fixed_until, "opacity:1"), (fixed_until + 0.3, "opacity:0")]),
                  text(MSG_X, uy - 2, "✓ fixed", 10.5, "#32D74B", 600)))
parts.append(g(show(CODE[0], dx=0, dy=0), "".join(code)))


def at(x, y, sx=1, sy=1, o=1):
    return f"opacity:{o};transform:translate({x:.0f}px,{y:.0f}px) scale({sx},{sy})"


x_in, x_mid, y0_ = bug_pos(0)
kf = [(BUG[0] - 0.05, at(x_in, y0_, o=0))]
for i in range(len(SPOTS)):
    x_in, x_mid, y = bug_pos(i)
    kf += [(ARRIVE[i], at(x_in, y)), (HIT[i] - 0.06, at(x_mid, y))]
    if i < len(SPOTS) - 1:  # dodge: jump away in an arc to the next spot
        nx, _, ny = bug_pos(i + 1)
        kf += [(HIT[i] - 0.02, at(x_mid, y - 10)),
               ((HIT[i] + ARRIVE[i + 1]) / 2, at((x_mid + nx) / 2, min(y, ny) - 46))]
    else:                   # squashed
        kf += [(HIT[i] + 0.02, at(x_mid, y + 5, 1.3, .3)), (HIT[i] + 0.45, at(x_mid, y + 5, 1.3, .3, 0))]
bug = animate(kf)
yikes = animate(sum([[(HIT[i] - 0.04, "opacity:0"), (HIT[i], "opacity:1"), (HIT[i] + 0.35, "opacity:1"), (HIT[i] + 0.45, "opacity:0")]
                     for i in range(len(SPOTS) - 1)], []))
parts.append(f'<g class="{bug}"><g class="wiggle">'
             '<rect x="0" y="0" width="16" height="10" rx="4" fill="#32D74B"/><rect x="12" y="1" width="7" height="8" rx="3" fill="#1E9E3A"/>'
             '<line x1="3" y1="10" x2="0" y2="14" stroke="#32D74B" stroke-width="1.6"/><line x1="8" y1="10" x2="8" y2="15" stroke="#32D74B" stroke-width="1.6"/>'
             '<line x1="13" y1="10" x2="16" y2="14" stroke="#32D74B" stroke-width="1.6"/></g>'
             f'<text x="8" y="-6" font-size="13" font-weight="800" fill="#FFD60A" text-anchor="middle" class="ui {yikes}">!</text></g>')
# a dust puff where the hammer misses, a star where it lands
for i in range(len(SPOTS)):
    _, x_mid, y = bug_pos(i)
    last = i == len(SPOTS) - 1
    fx = animate([(HIT[i] - 0.02, "opacity:0;transform:scale(.4)"), (HIT[i] + 0.1, "opacity:1;transform:scale(1.3)"),
                  (HIT[i] + 0.5, "opacity:0;transform:scale(1.6)")], "transform-box:fill-box;transform-origin:center")
    sym, col, size = ("✦", "#FFD60A", 24) if last else ("💨", "#C8C8CE", 14)
    parts.append(f'<text x="{x_mid + 8:.0f}" y="{y + 12:.0f}" font-size="{size}" fill="{col}" text-anchor="middle" class="ui {fx}">{sym}</text>')

# ---------------------------------------------------------------- 3. the Claude mascot (moves through every phase)
SPR = 4  # sprite pixel size -> 48x32


def px(x, y, w=1, h=1, fill=ORANGE):
    return f'<rect x="{x * SPR}" y="{y * SPR}" width="{w * SPR}" height="{h * SPR}" fill="{fill}"/>'


sprite = (px(1, 0, 10, 6) + px(0, 2, 1, 2) + px(11, 2, 1, 2) + px(3, 2, 1, 2, "#1F1F24") + px(8, 2, 1, 2, "#1F1F24")
          + f'<g class="legA">{px(2, 6, 1, 2)}{px(7, 6, 1, 2)}</g><g class="legB">{px(4, 6, 1, 2)}{px(9, 6, 1, 2)}</g>')

P_WELCOME = (TX + 12, 112)
P_PLAN = (MAIN_X + 420, 400)
P_UI = (MAIN_X + 210, 360)
P_CODE = (W - 80, H - 76)
P_SIM = (W - 92, H - 110)
moves = [
    (0, P_WELCOME), (SPLIT + 0.1, P_WELCOME), (PLAN[0] + 0.3, P_PLAN), (PLAN[1], P_PLAN),
    (UI[0] + 0.2, P_UI), (UI[1], P_UI), (CODE[0] + 0.3, P_CODE), (BUG[0] + 0.15, P_CODE),
]
for i in range(len(SPOTS)):          # chase: arrive just as the hammer drops, linger, run on
    _, x_mid, y = bug_pos(i)
    spot = (round(x_mid - 50), round(y - 18))
    moves += [(HIT[i] - 0.12, spot), (HIT[i] + (0.22 if i < len(SPOTS) - 1 else BUG[1] - HIT[i] - 0.1), spot)]
moves += [(BUILD + 0.2, P_SIM), (END, P_SIM)]
mv = animate([(t, f"transform:translate({x}px,{y}px)") for t, (x, y) in moves]
             , "animation-timing-function:cubic-bezier(.45,0,.3,1)")
fade = animate([(0, "opacity:1"), (END, "opacity:1"), (END + 0.3, "opacity:0"), (T - 0.3, "opacity:0"), (T, "opacity:1")])


def prop(a, b, inner, extra_cls=""):
    return f'<g class="{animate([(a, "opacity:0"), (a + 0.15, "opacity:1"), (b, "opacity:1"), (b + 0.15, "opacity:0")])}">' \
           f'<g class="{extra_cls}">{inner}</g></g>'


clipboard = ('<rect x="50" y="10" width="16" height="20" rx="2" fill="#E6EDF3"/><rect x="54" y="7" width="8" height="5" rx="1" fill="#9A9AA2"/>'
             '<rect x="53" y="16" width="10" height="2" fill="#9A9AA2"/><rect x="53" y="21" width="8" height="2" fill="#9A9AA2"/>')
brush = '<line x1="50" y1="22" x2="80" y2="4" stroke="#C8C8CE" stroke-width="3" stroke-linecap="round"/><circle cx="82" cy="3" r="4" fill="#FF9F0A"/>'
keyboard = '<rect x="-8" y="34" width="64" height="8" rx="2" fill="#3A3A42"/>' + "".join(
    f'<rect x="{-5 + k * 8}" y="36" width="6" height="4" rx="1" fill="#55555C"/>' for k in range(8))
hammer = '<rect x="54" y="2" width="4" height="26" rx="2" fill="#A07050"/><rect x="47" y="-2" width="18" height="9" rx="2" fill="#9A9AA2"/>'
swing = animate(sum([[(h - 0.32, "transform:rotate(-30deg)"), (h - 0.1, "transform:rotate(-60deg)"),
                      (h, "transform:rotate(35deg)"), (h + 0.18, "transform:rotate(-20deg)")] for h in HIT], []),
                "transform-box:fill-box;transform-origin:50% 100%")
cheer = animate([(SIM + 1.5, "transform:translateY(0)"), (SIM + 1.7, "transform:translateY(-10px)"),
                 (SIM + 1.9, "transform:translateY(0)"), (SIM + 2.1, "transform:translateY(-10px)"), (SIM + 2.3, "transform:translateY(0)")])
mascot = (f'<g class="{mv}"><g class="{fade}"><g class="{cheer}"><g class="bob">{sprite}</g>'
          + prop(PLAN[0], PLAN[1], clipboard)
          + prop(UI[0], UI[1], brush, "brushmove")
          + prop(CODE[0] + 0.3, BUG[0], keyboard)
          + prop(BUG[0], BUG[1], hammer, swing)
          + '</g></g></g>')
extra_css.append("""
.legA{animation:legA .36s steps(1) infinite}.legB{animation:legB .36s steps(1) infinite}
@keyframes legA{0%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes legB{0%{transform:translateY(-3px)}50%{transform:translateY(0)}}
.bob{animation:bob .36s steps(1) infinite}@keyframes bob{0%{translate:0 0}50%{translate:0 -2px}}
.brushmove{transform-box:fill-box;transform-origin:0 100%;animation:brush .5s ease-in-out infinite alternate}
@keyframes brush{0%{transform:rotate(-12deg)}100%{transform:rotate(14deg)}}
.wiggle{animation:wig .18s steps(1) infinite}@keyframes wig{0%{translate:0 0}50%{translate:0 -1px}}
""")

# ---------------------------------------------------------------- 4. build + simulator
BX, BY = W - 30, 20
press = animate([(BUILD - 0.1, "transform:scale(1)"), (BUILD + 0.05, "transform:scale(.8)"), (BUILD + 0.25, "transform:scale(1)")],
                "transform-box:fill-box;transform-origin:center")
glow = animate([(BUILD, "opacity:0"), (BUILD + 0.1, "opacity:1"), (BUILD + 0.8, "opacity:0")])
parts.append(f'<g class="{press}"><circle cx="{BX}" cy="{BY}" r="11" fill="#3A3A42"/>'
             f'<path d="M{BX - 3.5} {BY - 6} L{BX + 6} {BY} L{BX - 3.5} {BY + 6} Z" fill="#DFDFE0"/></g>'
             f'<circle cx="{BX}" cy="{BY}" r="15" fill="none" stroke="#0A84FF" stroke-width="2" class="{glow}"/>')
bar = animate([(BUILD + 0.1, "transform:scaleX(0);opacity:1"), (SIM - 0.1, "transform:scaleX(1);opacity:1"),
               (SIM + 0.1, "transform:scaleX(1);opacity:0")], "transform-box:fill-box;transform-origin:left")
parts.append(f'<rect x="0" y="40" width="{W}" height="2" fill="#0A84FF" class="{bar}"/>')

PW, PH = 236, 496
PX, PY = MAIN_CX - PW / 2, 40 + (H - 40 - PH) / 2
IX, IW = PX + 18, PW - 36
CXP = PX + PW / 2
dim = animate([(SIM - 0.2, "opacity:0"), (SIM + 0.2, "opacity:.75"), (END, "opacity:.75"), (END + 0.4, "opacity:0")])
phone = animate([(SIM, f"opacity:0;transform:translateY({H}px)"), (SIM + 0.6, "opacity:1;transform:translateY(0)"),
                 (END, "opacity:1;transform:translateY(0)"), (END + 0.5, "opacity:0;transform:translateY(40px)")],
                "animation-timing-function:cubic-bezier(.2,.9,.25,1.05)")
APP = SIM + 1.6  # app content after the launch splash


def ui_in(el, k):
    return g(show(APP + k * 0.18, dur=0.35, dy=8), el)


def label(x, y, s, size, color, weight=400, anchor="middle", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x:.1f}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}"{ls} class="ui">{escape(s)}</text>')


def fill_row(items, y, h, gap, rx, size, weight=700, upper=False, spacing=0):
    """Badges stretched to the full inner width, shared by label length so text never overflows."""
    weights = [len(t) + 4 for t, *_ in items]
    free = IW - gap * (len(items) - 1)
    out, x = [], IX
    for (t, bg, fg), wt in zip(items, weights):
        w = free * wt / sum(weights)
        out.append(f'<rect x="{x:.1f}" y="{y}" width="{w:.1f}" height="{h}" rx="{rx}" fill="{bg}"/>'
                   + label(x + w / 2, y + h / 2 + size * 0.36, t.upper() if upper else t, size, fg, weight, spacing=spacing))
        x += w + gap
    return "".join(out)


def section(y, title):
    return label(IX, y, title.upper(), 9.5, "#8B949E", 600, "start", 1.2)


top = PY + 50
parts.append(f'<rect x="{MAIN_X}" y="42" width="{W - MAIN_X}" height="{H - 42}" fill="#000" class="{dim}"/>')
sim = [f'<rect x="{PX - 5}" y="{PY - 5}" width="{PW + 10}" height="{PH + 10}" rx="48" fill="#3A3A40"/>',
       f'<rect x="{PX - 2}" y="{PY - 2}" width="{PW + 4}" height="{PH + 4}" rx="45" fill="#000"/>',
       f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="43" fill="#0D1117"/>',
       f'<rect x="{CXP - 38}" y="{PY + 10}" width="76" height="22" rx="11" fill="#000"/>',
       label(PX + 36, PY + 26, "9:41", 11, "#E6EDF3", 600),
       f'<rect x="{PX + PW - 44}" y="{PY + 17}" width="20" height="9" rx="2.5" fill="none" stroke="#E6EDF3" stroke-opacity=".6"/>',
       f'<rect x="{PX + PW - 42}" y="{PY + 19}" width="14" height="5" rx="1" fill="#E6EDF3"/>',
       f'<rect x="{CXP - 48}" y="{PY + PH - 12}" width="96" height="4" rx="2" fill="#E6EDF3" fill-opacity=".7"/>',
       ui_in(f'<circle cx="{CXP}" cy="{top + 30}" r="32" fill="url(#av)"/>' + avatar(CXP - 30, top, 60, 30), 0),
       ui_in(label(CXP, top + 92, "Hieu Nguyen", 22, "#E6EDF3", 700) + label(CXP, top + 112, "iOS Developer", 12.5, "#C9D1D9", 500)
             + label(CXP, top + 130, "Hanoi, Vietnam · since 2021", 11, "#8B949E"), 1),
       ui_in(f'<rect x="{IX}" y="{top + 146}" width="{IW}" height="1" fill="#30363D"/>', 2),
       ui_in(section(top + 172, "Stack")
             + fill_row([("Swift", "#F05138", "#fff"), ("SwiftUI", "#0A84FF", "#fff"), ("C++", "#00599C", "#fff")], top + 182, 26, 6, 5, 9.5, upper=True, spacing=1)
             + fill_row([("PHP", "#777BB4", "#fff"), ("Laravel", "#FF2D20", "#fff"), ("MySQL", "#4479A1", "#fff")], top + 214, 26, 6, 5, 9.5, upper=True, spacing=1), 3),
       ui_in(section(top + 270, "Curious about")
             + fill_row([("Rust", "#30363D", "#E6EDF3"), ("RxSwift", "#30363D", "#E6EDF3")], top + 280, 24, 6, 12, 11, 500)
             + fill_row([("Claude", "#D97757", "#fff"), ("GitHub", "#E6EDF3", "#0D1117")], top + 310, 24, 6, 12, 11, 600), 4),
       ui_in(section(top + 366, "Contact") + f'<rect x="{IX}" y="{top + 376}" width="{IW}" height="36" rx="12" fill="#26A5E4"/>'
             + label(CXP, top + 399, "Telegram  @Hieeus1012", 12.5, "#fff", 600), 5)]
parts.append(f'<g class="{phone}">{"".join(sim)}</g>')
parts.append('<defs><linearGradient id="av" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#F05138"/><stop offset="1" stop-color="#FF9F0A"/></linearGradient></defs>')

splash = animate([(SIM + 0.5, "opacity:0;transform:scale(.3)"), (SIM + 0.9, "opacity:1;transform:scale(1)"),
                  (SIM + 1.3, "opacity:1;transform:scale(1.05)"), (SIM + 1.6, "opacity:0;transform:scale(2.2)")],
                 "transform-box:fill-box;transform-origin:center")
parts.append(f'<g class="{splash}">{avatar(CXP - 34, PY + PH / 2 - 34, 68, 16)}</g>')

NOTE = "Chúc mừng năm mới! 🧧" if TET_INFO else "Hello there! 👋"
NT = SIM + 3.4
nb = animate([(NT, "opacity:0;transform:translateY(-70px)"), (NT + 0.45, "opacity:1;transform:translateY(0)"),
              (END - 0.4, "opacity:1;transform:translateY(0)"), (END, "opacity:0;transform:translateY(-70px)")],
             "animation-timing-function:cubic-bezier(.2,.9,.25,1.1)")
NX, NY, NW = PX + 10, PY + 40, PW - 20
parts.append(f'<clipPath id="scr"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" rx="43"/></clipPath>'
             f'<g clip-path="url(#scr)"><g class="{nb}">'
             f'<rect x="{NX}" y="{NY}" width="{NW}" height="56" rx="18" fill="#3A3A40" fill-opacity=".97" stroke="#fff" stroke-opacity=".08"/>'
             f'{avatar(NX + 10, NY + 11, 34, 8)}'
             f'{label(NX + 54, NY + 24, "Hieu", 12, "#fff", 600, "start")}{label(NX + NW - 12, NY + 24, "now", 10, "#A0A0A8", 400, "end")}'
             f'{label(NX + 54, NY + 41, NOTE, 11.5, "#E6E6EA", 400, "start")}</g></g>')

# Tết fireworks sit around the phone, above the dim layer
if TET_INFO:
    fw_phase = animate([(SIM + 0.2, "opacity:0"), (SIM + 0.6, "opacity:1"), (END, "opacity:1"), (END + 0.4, "opacity:0")])
    fw, css = themes.fireworks([
        (MAIN_X + 78, 150, 52, 0.0, ("#FFD60A", "#FF453A")),
        (W - 66, 130, 46, 0.9, ("#FF6FAE", "#FFFFFF")),
        (MAIN_X + 70, 390, 44, 1.6, ("#64D2FF", "#FFD60A")),
        (W - 74, 360, 40, 2.2, ("#FF9F0A", "#BF5AF2")),
    ])
    parts.append(g(fw_phase, fw))
    extra_css.append(css)

parts.append(mascot)

# ---------------------------------------------------------------- title-bar status
def status(s, color, a, b):
    cls = animate([(a, "opacity:0"), (a + 0.15, "opacity:1"), (b, "opacity:1"), (b + 0.15, "opacity:0")])
    return f'<text x="{W / 2}" y="25" fill="{color}" font-size="12" text-anchor="middle" class="ui {cls}">{escape(s)}</text>'


run_label = (f"🧧 Chúc mừng năm mới · {TET_INFO[1]} {TET_INFO[0]} {TET_INFO[3]}", "#FFD60A") if TET_INFO \
    else ("Running Hieu on iPhone 18 Pro Max", "#9A9AA2")
for s, color, a, b in [
    ("Terminal — claude", "#9A9AA2", -0.2, SPLIT), ("Plan.md", "#9A9AA2", SPLIT, PLAN[1]),
    ("ProfileScreen.design", "#9A9AA2", UI[0], UI[1]), ("ContentView.swift", "#9A9AA2", CODE[0], BUG[0]),
    ("ContentView.swift — bug on the loose 🐛", "#FF453A", BUG[0], BUG[1] - 0.2), ("ContentView.swift", "#9A9AA2", BUG[1] - 0.1, BUILD),
    ("Building Hieu…", "#9A9AA2", BUILD + 0.05, SIM - 0.1), ("✓ Build Succeeded", "#32D74B", SIM, SIM + 1.2),
    (*run_label, SIM + 1.3, END), ("Terminal — claude", "#9A9AA2", END + 0.2, T + 1),
]:
    parts.append(status(s, color, a, b))

if TET_INFO:
    parts.append(themes.peach_branch())
    petals, css = themes.falling_petals(W, H)
    parts.append(petals)
    extra_css.append(css)

# ---------------------------------------------------------------- assemble
style = f'''
.mono{{font-family:{MONO}}}
.code{{font-size:12.5px}}
.ui{{font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",Helvetica,Arial,sans-serif}}
{''.join(keyframes)}
{''.join(anim_rules)}
{''.join(extra_css)}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important}}}}
'''
aria = ("Animated story: Claude Code is launched in a terminal, runs the ios-project-bootstrap skill, plans, "
        "designs and codes a SwiftUI profile app, squashes a bug, then runs it in an iPhone simulator showing "
        "Hieu Nguyen, iOS developer in Hanoi.")
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{aria}">
<style>{style}</style>
<defs><image id="avimg" href="{AVATAR_URI}" width="100" height="100" preserveAspectRatio="xMidYMid slice"/>
<clipPath id="win"><rect width="{W}" height="{H}" rx="14"/></clipPath></defs>
<g clip-path="url(#win)">{''.join(parts)}</g>
</svg>
'''
out = Path(args.out) if args.out else ROOT / "assets" / "hero.svg"
out.parent.mkdir(exist_ok=True)
out.write_text(svg)
print(f"wrote {out} ({len(svg.encode()) / 1024:.1f} KB){' · Tết ' + str(TET_INFO[0]) if TET_INFO else ''}")
