#!/usr/bin/env python3
"""SHO-14 — generate Showmax Global launch post graphics (LinkedIn + Instagram).
Emits one self-contained HTML canvas per file into src/, named by calendar slot.
Render to PNG with render.sh (headless Chrome)."""
import os, html

SRC = os.path.join(os.path.dirname(__file__), "src")
LOGO = "../assets/logo.png"

# pillar -> (accent css var/color, glow rgba)
ACCENT = {
    "authority": ("#F5CB1F", "rgba(245,203,31,.20)"),
    "trade":     ("#2C5FC9", "rgba(44,95,201,.24)"),
    "brand":     ("#9E1722", "rgba(158,23,34,.24)"),
    "cta":       ("#F5CB1F", "rgba(245,203,31,.20)"),
}
FILES = []  # (filename, w, h)

def esc(s): return html.escape(s, quote=True)

def frame(name, fmt, pillar, chip, main_html, dots=None, swipe=False, chip_ghost=False):
    accent, glow = ACCENT[pillar]
    w, h = (1080, 1350) if fmt == "ig" else (1080, 1080)
    dots_html = ""
    if dots:
        total, on = dots
        items = "".join(f'<i class="on"></i>' if i == on else '<i></i>' for i in range(total))
        dots_html = f'<div class="dots">{items}</div>'
        if swipe:
            dots_html += '<div class="swipe">Swipe →</div>'
    chip_cls = "chip ghost" if chip_ghost else "chip"
    if not chip_ghost and pillar in ("trade", "brand"):
        chip_cls += " light"  # white text on dark blue/maroon accents
    doc = f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="social.css">
<style>:root{{--accent:{accent};--accent-glow:{glow};}}</style></head>
<body>
<div class="canvas {fmt}">
  <div class="bg">
    <div class="glow g1"></div><div class="glow g2"></div>
    <svg viewBox="0 0 {w} {h}" preserveAspectRatio="none">
      <path d="M120 {int(h*0.30)} Q {w//2} {int(h*0.05)} {w-120} {int(h*0.34)}"
            fill="none" stroke="{accent}" stroke-width="2" stroke-opacity="0.22" stroke-dasharray="2 14" stroke-linecap="round"/>
    </svg>
    <div class="grid"></div><div class="vign"></div>
  </div>
  <div class="top">
    <img class="logo" src="{LOGO}" alt="Showmax Global">
    <span class="{chip_cls}">{esc(chip)}</span>
  </div>
  {main_html}
  {dots_html}
  <div class="foot">
    <div class="rule"></div>
    <div class="frow">
      <span class="site">showmaxglobal.com</span>
      <span class="loc">Indore <b>🇮🇳</b> · Sharjah <b>🇦🇪</b></span>
    </div>
  </div>
</div>
</body></html>"""
    open(os.path.join(SRC, name + ".html"), "w", encoding="utf-8").write(doc)
    FILES.append((name, w, h))

# ---------- main-content builders ----------
def m_statement(kicker, h_html, sub=None, cta=None, cta_green=False, top=False, hsize=""):
    k = f'<div class="kicker">{esc(kicker)}</div>' if kicker else ""
    s = f'<p class="sub">{sub}</p>' if sub else ""
    c = ""
    if cta:
        style = ' style="background:var(--green);color:#04210f"' if cta_green else ""
        c = f'<div class="cta"{style}>{esc(cta)}</div>'
    hc = f"h {hsize}".strip()
    cls = "main top-align" if top else "main"
    return f'<div class="{cls}">{k}<div class="{hc}">{h_html}</div>{s}{c}</div>'

def m_rows(kicker, h_html, rows, sub=None):
    k = f'<div class="kicker">{esc(kicker)}</div>' if kicker else ""
    item = ""
    for r in rows:
        if "num" in r:
            lead = f'<div class="num">{esc(r["num"])}</div>'
        else:
            lead = f'<div class="ic">{r["ic"]}</div>'
        rd = f'<div class="rd">{esc(r["rd"])}</div>' if r.get("rd") else ""
        item += f'<div class="row">{lead}<div class="txt"><div class="rt">{esc(r["rt"])}</div>{rd}</div></div>'
    s = f'<p class="sub wide">{sub}</p>' if sub else ""
    hh = f'<div class="h xs">{h_html}</div>' if h_html else ""
    lcls = "list compact" if len(rows) >= 5 else "list"
    return f'<div class="main top-align">{k}{hh}{s}<div class="{lcls}">{item}</div></div>'

def m_carousel_item(num, total, title, desc):
    return (f'<div class="main"><div class="kicker">{num} / {total}</div>'
            f'<div class="row" style="padding:46px 44px;align-items:center">'
            f'<div class="num" style="font-size:120px;min-width:140px">{num}</div>'
            f'<div class="txt"><div class="rt" style="font-size:54px">{esc(title)}</div>'
            f'<div class="rd" style="font-size:32px;margin-top:16px">{esc(desc)}</div></div></div></div>')

def m_stat(kicker, stat_html, statlab, sub=None):
    k = f'<div class="kicker">{esc(kicker)}</div>' if kicker else ""
    s = f'<p class="sub wide">{sub}</p>' if sub else ""
    return (f'<div class="main">{k}<div class="stat">{stat_html}</div>'
            f'<div class="statlab">{esc(statlab)}</div>{s}</div>')

def m_compare(h_html, col_a, col_b, cta=None):
    def col(c, cls):
        lis = "".join(f"<li>{esc(x)}</li>" for x in c["items"])
        return (f'<div class="col {cls}"><h4>{esc(c["title"])}</h4>'
                f'<span class="tag">{esc(c["tag"])}</span><ul>{lis}</ul></div>')
    c = f'<div class="cta">{esc(cta)}</div>' if cta else ""
    return (f'<div class="main"><div class="h sm">{h_html}</div>'
            f'<div class="cols">{col(col_a,"a")}{col(col_b,"b")}</div>{c}</div>')

def m_lanes(h_html, lanes, cta=None):
    rows = ""
    for ln in lanes:
        rows += (f'<div class="lane" style="--la:{ln["c"]}"><div class="ln">{ln["n"]}</div>'
                 f'<div><div class="lt">{esc(ln["t"])}</div><div class="ld">{esc(ln["d"])}</div></div></div>')
    c = f'<div class="cta">{esc(cta)}</div>' if cta else ""
    return f'<div class="main"><div class="h sm">{h_html}</div><div class="lanes">{rows}</div>{c}</div>'

def m_launch():
    return ('<div class="main center">'
            f'<img class="biglogo" src="{LOGO}" alt="Showmax Global">'
            '<div class="kicker">Now live</div>'
            '<div class="tagline">Two markets.<br>One growth&nbsp;partner.</div>'
            '<p class="sub" style="max-width:24ch;text-align:center">Digital marketing • Branding • UAE–India trade</p>'
            '<div class="corridor"><span class="flag">🇮🇳</span><span>India</span>'
            '<span class="ar">⇄</span><span>UAE</span><span class="flag">🇦🇪</span></div>'
            '</div>')

# ===================== POSTS =====================
# Post 1 — Launch (brand story)
for fmt in ("ig", "li"):
    frame(f"post-01-launch-{fmt}", fmt, "brand", "Launch", m_launch())

# Post 2 — Authority carousel: 3 ad-budget mistakes
P2 = [("Boosting posts", "instead of running structured campaigns with a real objective."),
      ("No offer or landing page", "you send traffic somewhere with nothing to convert."),
      ("Killing ads too early", "you quit before the algorithm finishes learning.")]
frame("post-02-ad-budget-ig", "ig", "authority", "Authority",
      m_statement("Ad budget", 'Most SMEs waste their first <span class="hl">₹50k</span> of ad budget.',
                  "3 mistakes to fix first — swipe →"), dots=(4, 0), swipe=True)
for i, (t, d) in enumerate(P2, 1):
    frame(f"post-02-ad-budget-ig-s{i}", "ig", "authority", "Authority",
          m_carousel_item(i, 3, t, d), dots=(4, i))
frame("post-02-ad-budget-li", "li", "authority", "Authority",
      m_rows("Ad budget — 3 mistakes", 'Stop wasting <span class="hl">ad spend</span>',
             [{"num": str(i+1), "rt": t, "rd": d} for i, (t, d) in enumerate(P2)]))

# Post 3 — Trade stat: CEPA
for fmt in ("ig", "li"):
    frame(f"post-03-cepa-{fmt}", fmt, "trade", "UAE–India Trade",
          m_stat("India–UAE CEPA", '90<span class="u">%+</span>',
                 "of UAE-bound tariff lines cut for Indian exporters.",
                 "Are you structured to use it? DM “UAE” →"))

# Post 4 — Authority carousel: branding checklist
P4 = [("Positioning", "the space you own in the customer's mind."),
      ("Voice", "how you sound — consistent everywhere."),
      ("Consistency", "same look & message across every touchpoint."),
      ("The feeling", "what people remember after you're gone.")]
frame("post-04-brand-ig", "ig", "authority", "Authority",
      m_statement("Branding", 'Your logo <span class="hl">isn\'t</span> your brand.',
                  "It's 5%. Here's the other 95% — swipe →"), dots=(5, 0), swipe=True)
for i, (t, d) in enumerate(P4, 1):
    frame(f"post-04-brand-ig-s{i}", "ig", "authority", "Authority",
          m_carousel_item(i, 4, t, d), dots=(5, i))
frame("post-04-brand-li", "li", "authority", "Authority",
      m_rows("The brand checklist", 'Your logo <span class="hl">isn\'t</span> your brand',
             [{"num": str(i+1), "rt": t, "rd": d} for i, (t, d) in enumerate(P4)]))

# Post 5 — CTA: free teardown
for fmt in ("ig", "li"):
    frame(f"post-05-teardown-{fmt}", fmt, "cta", "Free",
          m_statement("Free this week", '<span class="hl">Free</span> website teardown.',
                      "Comment your link — we'll reply with 3 quick wins. First 5 only.",
                      cta="Comment your website ↓", cta_green=True))

# Post 6 — Trade compare: Free Zone vs Mainland
for fmt in ("ig", "li"):
    frame(f"post-06-setup-{fmt}", fmt, "trade", "UAE–India Trade",
          m_compare('Free Zone <span class="hl">vs</span> Mainland',
                    {"title": "Free Zone", "tag": "Easiest entry",
                     "items": ["100% ownership", "Faster, simpler setup", "Limits on local UAE trade"]},
                    {"title": "Mainland", "tag": "Trade freely",
                     "items": ["Trade across all of UAE", "Broader business scope", "More compliance steps"]},
                    cta="DM “SETUP” to pick yours"))

# Post 7 — Authority carousel: SEO 2026
P7 = [("Be the clearest source", "answer the question better than anyone else."),
      ("Structure for AI", "headings, FAQs & schema machines can read."),
      ("Earn trust signals", "depth, links & real expertise compound over time.")]
frame("post-07-seo-ig", "ig", "authority", "Authority",
      m_statement("SEO in 2026", 'It\'s about <span class="hl">answers</span>, not keywords.',
                  "Our 3-step foundation — swipe →"), dots=(4, 0), swipe=True)
for i, (t, d) in enumerate(P7, 1):
    frame(f"post-07-seo-ig-s{i}", "ig", "authority", "Authority",
          m_carousel_item(i, 3, t, d), dots=(4, i))
frame("post-07-seo-li", "li", "authority", "Authority",
      m_rows("SEO in 2026", 'Answers, <span class="hl">not keywords</span>',
             [{"num": str(i+1), "rt": t, "rd": d} for i, (t, d) in enumerate(P7)]))

# Post 8 — Brand story
for fmt in ("ig", "li"):
    frame(f"post-08-two-markets-{fmt}", fmt, "brand", "Brand Story",
          m_statement("Why we built this", 'One team.<br><span class="hl">Two markets.</span>',
                      "Indore for sharp, cost-efficient execution. Sharjah for a Gulf foothold. Grow in India AND the UAE — without juggling three vendors."))

# Post 9 — Services lanes
LANES = [{"n": "01", "t": "Digital Marketing", "d": "Leads & pipeline.", "c": "#F5CB1F"},
         {"n": "02", "t": "Branding", "d": "Identity & messaging.", "c": "#9E1722"},
         {"n": "03", "t": "UAE–India Trade", "d": "Market entry, done right.", "c": "#2C5FC9"}]
for fmt in ("ig", "li"):
    frame(f"post-09-services-{fmt}", fmt, "cta", "Services",
          m_lanes('Pick your <span class="hl">growth lane.</span>', LANES,
                  cta="Which lane this quarter? DM us"))

# Post 10 — CTA: 1-page plan
for fmt in ("ig", "li"):
    frame(f"post-10-plan-{fmt}", fmt, "authority", "Authority",
          m_statement("The 1-page plan", 'The marketing plan every <span class="hl">SME</span> needs.',
                      "Audience • Offer • Channel • Message • One metric.",
                      cta="Comment “PLAN” for the template", cta_green=True))

# Post 11 — Trade list: 5 industries
IND = [("F&B & FMCG", "Brands & retail crossing the corridor."),
       ("IT & SaaS", "Tech buyers on both sides."),
       ("Jewellery & gems", "A historic India⇄UAE trade lane."),
       ("Healthcare & wellness", "Fast-growing Gulf demand."),
       ("Logistics", "The backbone of CEPA trade.")]
for fmt in ("ig", "li"):
    frame(f"post-11-industries-{fmt}", fmt, "trade", "UAE–India Trade",
          m_rows("Corridor heatmap", 'Top 5 sectors with India<span class="hl">⇄</span>UAE upside',
                 [{"num": str(i+1), "rt": t, "rd": d} for i, (t, d) in enumerate(IND)]))

# Post 12 — CTA: book a call (month recap)
for fmt in ("ig", "li"):
    frame(f"post-12-book-call-{fmt}", fmt, "cta", "Let's talk",
          m_statement("Month one — done", 'Ready to <span class="hl">grow?</span>',
                      "More leads, a sharper brand, or India⇄UAE expansion. Book a free 20-min growth call.",
                      cta="Book your free call →", cta_green=True))

# manifest for render.sh
with open(os.path.join(os.path.dirname(__file__), "manifest.txt"), "w") as f:
    for name, w, h in FILES:
        f.write(f"{name} {w} {h}\n")
print(f"Generated {len(FILES)} canvases")
