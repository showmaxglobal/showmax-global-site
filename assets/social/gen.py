#!/usr/bin/env python3
"""Showmax Global — social visual asset generator (SHO-8).
Emits one self-contained HTML file per asset into html/ and a manifest.csv
(name,width,height) consumed by render.sh (headless Chrome -> png/).
Brand kit (from SHO-5 / live site): Archivo+Inter, ink #0A0A0B, gold #F5CB1F,
corridor blue #1B4090, corridor maroon #9E1722. Voice: "Two markets. One growth partner."
"""
import os, csv

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = os.path.join(HERE, "html")
os.makedirs(HTML, exist_ok=True)

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
:root{
 --ink:#0A0A0B;--ink2:#141417;--ink3:#1C1C21;
 --gold:#F5CB1F;--gold-soft:#FFE08A;--gold-deep:#B2871B;
 --blue:#1B4090;--blue2:#2C5FC9;--blue-soft:#9DBDF2;
 --red:#9E1722;--red-deep:#6B0C14;
 --mut:#9A9AA2;--mut2:#67676E;--white:#FFFFFF;
}
html,body{background:var(--ink)}
.canvas{position:relative;overflow:hidden;background:var(--ink);color:#fff;
 font-family:'Inter',sans-serif;-webkit-font-smoothing:antialiased}
.h{font-family:'Archivo',sans-serif;font-weight:900;line-height:.96;letter-spacing:-.015em}
.h8{font-family:'Archivo',sans-serif;font-weight:800;letter-spacing:-.01em}
.up{text-transform:uppercase}
.gold{color:var(--gold)}.blue{color:var(--blue-soft)}.red{color:#E06A74}.mut{color:var(--mut)}
.eyebrow{font-family:'Archivo',sans-serif;font-weight:800;letter-spacing:.18em;text-transform:uppercase}
.grain{position:absolute;inset:0;background:
 radial-gradient(120% 80% at 78% -10%, rgba(245,203,31,.16), transparent 55%),
 radial-gradient(90% 70% at -10% 110%, rgba(27,64,144,.20), transparent 55%)}
.ring{border:1px solid rgba(245,203,31,.30);border-radius:999px}
.dot{width:8px;height:8px;border-radius:999px;background:var(--gold);display:inline-block}
"""

def mark(size, ring=True):
    """Globe + play brand mark as inline SVG, square `size` px."""
    return f"""<svg width="{size}" height="{size}" viewBox="0 0 120 120" fill="none" xmlns="http://www.w3.org/2000/svg">
<defs><clipPath id="cg"><circle cx="60" cy="60" r="54"/></clipPath></defs>
<circle cx="60" cy="60" r="54" fill="#F5CB1F" stroke="#B2871B" stroke-width="4"/>
<g clip-path="url(#cg)" stroke="#9E1722" stroke-width="3" fill="none" opacity=".9">
 <ellipse cx="60" cy="60" rx="22" ry="54"/><ellipse cx="60" cy="60" rx="42" ry="54"/>
 <line x1="4" y1="60" x2="116" y2="60"/><line x1="12" y1="33" x2="108" y2="33"/>
 <line x1="12" y1="87" x2="108" y2="87"/></g>
<circle cx="60" cy="60" r="29" fill="#9E1722"/>
<path d="M52 45 L52 75 L80 60 Z" fill="#F5CB1F"/>
</svg>"""

def lockup(markpx, fs, sub=True, color="#fff"):
    s = f"""<div style="display:flex;align-items:center;gap:{markpx*0.28:.0f}px">
 {mark(markpx)}
 <div style="line-height:1">
  <div class="h up" style="font-size:{fs}px;color:{color}">SHOWMAX</div>
  {'<div class="eyebrow" style="font-size:'+str(fs*0.34)+'px;color:var(--gold);margin-top:'+str(fs*0.06)+'px">GLOBAL</div>' if sub else ''}
 </div></div>"""
    return s

def brandbar(w, accent="--gold"):
    """Footer strip for posts."""
    return f"""<div style="position:absolute;left:0;right:0;bottom:0;height:{int(w*0.082)}px;
 background:#08080A;border-top:1px solid rgba(245,203,31,.22);
 display:flex;align-items:center;justify-content:space-between;padding:0 {int(w*0.066)}px">
 <div style="display:flex;align-items:center;gap:{int(w*0.018)}px">{mark(int(w*0.045))}
  <span class="h8 up" style="font-size:{int(w*0.026)}px;letter-spacing:.02em">Showmax Global</span></div>
 <span class="mut" style="font-size:{int(w*0.0205)}px;letter-spacing:.04em">showmaxglobal.com · Indore · Sharjah</span>
</div>"""

def page(name, w, h, inner, body_style=""):
    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>{CSS}</style></head>
<body><div class="canvas" style="width:{w}px;height:{h}px;{body_style}">{inner}</div></body></html>"""
    with open(os.path.join(HTML, name + ".html"), "w") as f:
        f.write(doc)
    return (name, w, h)

ASSETS = []
def A(*a): ASSETS.append(page(*a))

# ----- shared building blocks for posts (1080x1350) -----
PW, PH = 1080, 1350
def post_shell(inner, accent="--gold", pad=84, top=""):
    return f"""<div class="grain"></div>{top}
 <div style="position:absolute;left:{pad}px;right:{pad}px;top:96px;bottom:{int(PW*0.082)+70}px;
  display:flex;flex-direction:column">{inner}</div>{brandbar(PW, accent)}"""

def eyebrow_row(pillar, tag, color="var(--gold)"):
    return f"""<div style="display:flex;align-items:center;gap:18px;margin-bottom:34px">
 <span style="display:inline-block;width:46px;height:6px;border-radius:9px;background:{color}"></span>
 <span class="eyebrow" style="font-size:24px;color:{color}">{pillar}</span>
 <span class="eyebrow mut" style="font-size:20px;letter-spacing:.14em">· {tag}</span></div>"""

def chip(num, title, body, color="var(--gold)"):
    return f"""<div style="display:flex;gap:26px;align-items:flex-start;padding:30px 0;border-top:1px solid rgba(255,255,255,.10)">
 <div class="h" style="font-size:54px;color:{color};min-width:62px">{num}</div>
 <div><div class="h8" style="font-size:38px;margin-bottom:8px">{title}</div>
  <div style="font-size:27px;line-height:1.4;color:var(--mut)">{body}</div></div></div>"""

def cta_pill(text, color="var(--gold)", fg="#0A0A0B"):
    return f"""<div style="display:inline-flex;align-items:center;gap:16px;background:{color};color:{fg};
 font-family:'Archivo';font-weight:800;font-size:30px;padding:22px 40px;border-radius:999px;width:fit-content">
 {text}</div>"""

# =========================================================
# 1. PROFILE LOGO 400x400
# =========================================================
A("01_profile_logo_400", 400, 400, f"""
<div class="grain"></div>
<div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:18px">
 {mark(150)}
 <div class="h up" style="font-size:50px">SHOWMAX</div>
 <div class="eyebrow gold" style="font-size:19px;letter-spacing:.42em;margin-top:-6px">GLOBAL</div>
 <div style="width:60px;height:4px;background:var(--gold);border-radius:9px;margin-top:6px"></div>
</div>""")

# =========================================================
# 2. LINKEDIN BANNER 1128x191
# =========================================================
A("02_linkedin_banner_1128x191", 1128, 191, f"""
<div class="grain"></div>
<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:space-between;padding:0 60px">
 <div style="display:flex;align-items:center;gap:26px">{mark(108)}
  <div><div class="h up" style="font-size:48px;line-height:1">Showmax Global</div>
   <div class="eyebrow gold" style="font-size:17px;letter-spacing:.16em;margin-top:6px">DIGITAL MARKETING · BRANDING · UAE–INDIA TRADE</div></div></div>
 <div style="text-align:right">
  <div class="h" style="font-size:34px;color:var(--gold);line-height:1.05">Two markets.<br>One growth partner.</div>
  <div class="mut" style="font-size:18px;margin-top:8px;letter-spacing:.04em">📍 Indore 🇮🇳 · Sharjah 🇦🇪</div></div>
</div>
<div style="position:absolute;left:0;bottom:0;height:7px;width:100%;background:linear-gradient(90deg,var(--gold),var(--gold-deep) 45%,var(--blue) 75%,var(--red))"></div>""")

# =========================================================
# 3. IG TEMPLATE SET (3 styles, one per pillar family) 1080x1350
# =========================================================
A("03_template_A_authority", PW, PH, post_shell(f"""
 {eyebrow_row("① Authority · Education", "TEMPLATE")}
 <div class="h" style="font-size:120px;color:var(--gold);margin-top:6px">[ STAT ]</div>
 <div class="h" style="font-size:78px;margin-top:6px;max-width:880px">Headline goes<br>right here.</div>
 <div style="font-size:30px;color:var(--mut);margin-top:30px;max-width:820px;line-height:1.45">
  Sub-line for context — concrete, plain-spoken, one idea per post.</div>
 <div style="margin-top:auto">{cta_pill("Save this →")}</div>
""", top=f'<div style="position:absolute;right:84px;top:90px">{mark(70)}</div>'))

A("03_template_B_trade", PW, PH, f"""
<div style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1430,#0A0A0B 60%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column">
 {eyebrow_row("② UAE–India Trade", "TEMPLATE", "var(--blue-soft)")}
 <div class="h" style="font-size:84px;margin-top:6px;max-width:880px">India <span class="gold">⇄</span> UAE<br>headline.</div>
 <div style="display:flex;gap:18px;margin-top:34px">
  <span style="font-size:64px">🇮🇳</span><span class="h gold" style="font-size:60px;align-self:center">⇄</span><span style="font-size:64px">🇦🇪</span></div>
 <div style="font-size:30px;color:var(--blue-soft);margin-top:30px;max-width:820px;line-height:1.45">
  CEPA · market entry · partner discovery — supporting line.</div>
 <div style="margin-top:auto">{cta_pill('DM "UAE" →', "var(--blue2)", "#fff")}</div>
</div>{brandbar(PW, "--blue")}""")

A("03_template_C_brand", PW, PH, f"""
<div style="position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 0%,#26200A,#0A0A0B 58%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column;justify-content:center;text-align:center;align-items:center">
 {mark(120)}
 <div class="eyebrow gold" style="font-size:24px;letter-spacing:.2em;margin-top:30px">③ ④ BRAND · ENGAGEMENT</div>
 <div class="h" style="font-size:96px;margin-top:24px;max-width:900px">Big brand<br>statement.</div>
 <div style="font-size:30px;color:var(--mut);margin-top:28px;max-width:760px;line-height:1.45">Reusable hero template for story & lead-gen posts.</div>
 <div style="margin-top:40px">{cta_pill("Follow along →")}</div>
</div>{brandbar(PW)}""")

# =========================================================
# 4. STORY HIGHLIGHT COVERS (4) 1080x1920
# =========================================================
HW, HH = 1080, 1920
def highlight(name, icon_html, label, icon_fs=300):
    return page(name, HW, HH, f"""
 <div class="grain"></div>
 <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:60px">
  <div class="ring" style="width:520px;height:520px;display:flex;align-items:center;justify-content:center;overflow:hidden;
   border-width:3px;background:radial-gradient(circle,#15131B,#0A0A0B)">
    <div style="font-size:{icon_fs}px;line-height:1;white-space:nowrap">{icon_html}</div></div>
  <div class="h up" style="font-size:80px;color:var(--gold);letter-spacing:.04em">{label}</div>
  <div style="width:90px;height:6px;background:#fff;border-radius:9px;opacity:.85"></div>
 </div>""")
ASSETS.append(highlight("04_highlight_services", "🧩", "Services"))
ASSETS.append(highlight("04_highlight_uae_india",
   '<div style="display:flex;flex-direction:column;align-items:center;gap:6px"><span style="font-size:120px">🇮🇳</span>'
   '<span class="h gold" style="font-size:120px;line-height:.7">⇅</span><span style="font-size:120px">🇦🇪</span></div>',
   "UAE–India", icon_fs=120))
ASSETS.append(highlight("04_highlight_results", "📈", "Results"))
ASSETS.append(highlight("04_highlight_about", "🌐", "About"))

# =========================================================
# 5. TWELVE LAUNCH POSTS (1080x1350; carousels expanded)
# =========================================================
# Post 1 — Launch brand card (Pillar 3)
A("post01_launch", PW, PH, f"""
<div style="position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 8%,#2A2207,#0A0A0B 56%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column;align-items:center;text-align:center;justify-content:center">
 {mark(168)}
 <div class="eyebrow gold" style="font-size:26px;letter-spacing:.22em;margin-top:34px">NOW LIVE · SHOWMAX GLOBAL</div>
 <div class="h" style="font-size:118px;margin-top:26px">Two markets.<br><span class="gold">One growth partner.</span></div>
 <div style="font-size:31px;color:var(--mut);margin-top:32px;max-width:820px;line-height:1.45">
  Digital marketing, branding & UAE–India trade facilitation — built across Indore 🇮🇳 & Sharjah 🇦🇪.</div>
 <div style="margin-top:42px">{cta_pill("Follow along →")}</div>
</div>{brandbar(PW)}""")

# Post 2 — CAROUSEL (3 slides): ad-budget mistakes (Pillar 1)
mistakes = [
 ("01","Boosting, not campaigns","You hit “Boost post” instead of running a structured campaign with proper objectives & audiences."),
 ("02","No offer, no landing page","Traffic with nowhere to convert. No clear offer and no dedicated landing page = wasted clicks."),
 ("03","Killing ads too early","You switch ads off before the algorithm exits its learning phase — right when it starts working."),
]
for i,(n,t,b) in enumerate(mistakes, start=1):
    cover = i==1
    A(f"post02_carousel_{i}of3", PW, PH, post_shell(f"""
     {eyebrow_row("① Authority · Carousel "+str(i)+"/3", "SWIPE →")}
     {('<div class="h" style="font-size:74px;max-width:900px;margin-bottom:18px">Most SMEs waste their first <span class=gold>₹50k</span> of ad budget.</div>'+
       '<div style="font-size:30px;color:var(--mut);margin-bottom:34px">3 mistakes we see early advertisers make 👇</div>') if cover else ''}
     <div style="display:flex;flex-direction:column;justify-content:center;flex:1">
       <div class="h" style="font-size:200px;color:rgba(245,203,31,.18)">{n}</div>
       <div class="h" style="font-size:72px;margin-top:-30px;max-width:880px">{t}</div>
       <div style="font-size:31px;color:var(--mut);margin-top:26px;max-width:860px;line-height:1.45">{b}</div>
     </div>
     {('<div style="margin-top:auto">'+cta_pill("Save + share →")+'</div>') if i==3 else '<div style="margin-top:auto" class="mut h8" style="font-size:26px">→ keep swiping</div>'}
    """))

# Post 3 — Stat card + corridor (Pillar 2)
A("post03_cepa_stat", PW, PH, f"""
<div style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1430,#0A0A0B 62%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column">
 {eyebrow_row("② UAE–India Trade · CEPA", "FOR EXPORTERS","var(--blue-soft)")}
 <div class="h" style="font-size:230px;color:var(--gold);line-height:.9">90%+</div>
 <div class="h" style="font-size:60px;margin-top:6px;max-width:900px">of UAE-bound goods now<br>have <span class="blue">cut tariffs</span> under CEPA.</div>
 <div style="display:flex;align-items:center;gap:26px;margin-top:40px">
  <span style="font-size:70px">🇮🇳</span>
  <div style="flex:1;height:4px;background:linear-gradient(90deg,var(--gold),var(--blue));position:relative;border-radius:9px">
   <span class="gold h" style="position:absolute;right:-6px;top:-34px;font-size:40px">→</span></div>
  <span style="font-size:70px">🇦🇪</span></div>
 <div style="font-size:30px;color:var(--blue-soft);margin-top:34px;max-width:880px;line-height:1.4">
  90%+ tariff lines. 0 excuses. We help you enter the UAE the right way.</div>
 <div style="margin-top:auto">{cta_pill('DM "UAE" →',"var(--blue2)","#fff")}</div>
</div>{brandbar(PW,"--blue")}""")

# Post 4 — CAROUSEL (4 slides): brand checklist (Pillar 1)
checklist = [
 ("Positioning","The space you own in the customer’s mind. Who you’re for, and what you’re against."),
 ("Voice","How you sound everywhere — consistent, human, unmistakably you."),
 ("Consistency","Same look, same promise, every touchpoint. Repetition builds recall."),
 ("The feeling","The emotion people walk away with. That’s the 95% a logo can’t do."),
]
for i,(t,b) in enumerate(checklist, start=1):
    cover = i==1
    A(f"post04_carousel_{i}of4", PW, PH, post_shell(f"""
     {eyebrow_row("① Authority · Carousel "+str(i)+"/4", "SWIPE →")}
     {('<div class="h" style="font-size:84px;max-width:900px;margin-bottom:16px">Branding isn’t your logo.</div>'+
       '<div style="font-size:31px;color:var(--mut);margin-bottom:30px">It’s the promise people remember. Our 4-part checklist 👇</div>') if cover else ''}
     <div style="display:flex;flex-direction:column;justify-content:center;flex:1">
       <div class="eyebrow gold" style="font-size:26px;letter-spacing:.2em">PART {i} OF 4</div>
       <div class="h" style="font-size:96px;margin-top:18px;max-width:880px">{t}</div>
       <div style="font-size:32px;color:var(--mut);margin-top:28px;max-width:860px;line-height:1.45">{b}</div>
     </div>
     {('<div style="margin-top:auto">'+cta_pill("Save the checklist →")+'</div>') if i==4 else '<div style="margin-top:auto" class="mut h8">→ keep swiping</div>'}
    """))

# Post 5 — Free teardown (Pillar 4)
A("post05_free_teardown", PW, PH, f"""
<div style="position:absolute;inset:0;background:radial-gradient(120% 90% at 50% 100%,#2A2207,#0A0A0B 56%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column;justify-content:center;text-align:center;align-items:center">
 <div class="eyebrow" style="font-size:28px;letter-spacing:.24em;color:#0A0A0B;background:var(--gold);padding:14px 30px;border-radius:999px">LIMITED · 5 SPOTS</div>
 <div class="h" style="font-size:150px;margin-top:40px;line-height:.92">FREE<br><span class="gold">TEARDOWN</span></div>
 <div style="font-size:34px;color:#fff;margin-top:34px;max-width:840px;line-height:1.4">
  Comment your website 👇 We’ll reply with <span class="gold">3 quick wins</span> to get more leads.</div>
 <div style="font-size:28px;color:var(--mut);margin-top:22px">First 5 only.</div>
 <div style="margin-top:44px">{cta_pill("Drop your link in the comments")}</div>
</div>{brandbar(PW)}""")

# Post 6 — Free Zone vs Mainland comparison (Pillar 2)
A("post06_freezone_mainland", PW, PH, f"""
<div style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1430,#0A0A0B 64%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column">
 {eyebrow_row("② UAE–India Trade · Setup", "60-SECOND GUIDE","var(--blue-soft)")}
 <div class="h" style="font-size:78px;max-width:900px">Free Zone <span class="mut">vs</span> Mainland</div>
 <div style="display:flex;gap:26px;margin-top:40px;flex:1">
  <div style="flex:1;background:rgba(245,203,31,.07);border:1px solid rgba(245,203,31,.3);border-radius:26px;padding:38px">
    <div class="h8 gold" style="font-size:42px">Free Zone</div>
    <div style="margin-top:24px;font-size:28px;line-height:1.7;color:#EDEDF0">✓ 100% ownership<br>✓ Easier, faster setup<br>✗ Limits on local UAE trade</div></div>
  <div style="flex:1;background:rgba(45,95,201,.12);border:1px solid rgba(157,189,242,.35);border-radius:26px;padding:38px">
    <div class="h8 blue" style="font-size:42px">Mainland</div>
    <div style="margin-top:24px;font-size:28px;line-height:1.7;color:#EDEDF0">✓ Trade freely across UAE<br>✓ Broader scope<br>✗ More setup steps</div></div>
 </div>
 <div style="font-size:28px;color:var(--blue-soft);margin-top:30px">Your business model decides. We help you pick + execute.</div>
 <div style="margin-top:26px">{cta_pill('DM "SETUP" →',"var(--blue2)","#fff")}</div>
</div>{brandbar(PW,"--blue")}""")

# Post 7 — SEO 3-step (Pillar 1)
A("post07_seo_3step", PW, PH, post_shell(f"""
 {eyebrow_row("① Authority · SEO 2026", "INFOGRAPHIC")}
 <div class="h" style="font-size:84px;max-width:900px">SEO is about <span class="gold">answers</span>,<br>not keywords.</div>
 <div style="margin-top:30px">
  {chip("1","Own a topic","Be the clearest, most useful source on one subject — not 50 thin pages.")}
  {chip("2","Structure for AI","Headings, FAQs & schema so AI search can quote you as the answer.")}
  {chip("3","Refresh & link","Keep it current and interlinked. Authority compounds over time.")}
 </div>
 <div style="margin-top:auto">{cta_pill("Save this →")}</div>
"""))

# Post 8 — Brand story two countries (Pillar 3)
A("post08_two_countries", PW, PH, f"""
<div style="position:absolute;inset:0;display:flex"><div style="flex:1;background:linear-gradient(180deg,#1A0E0F,#0A0A0B)"></div><div style="flex:1;background:linear-gradient(180deg,#0A1430,#0A0A0B)"></div></div>
<div class="grain"></div>
<div style="position:absolute;left:0;right:0;top:140px;display:flex;justify-content:center;gap:50px;font-size:96px">🇮🇳 <span class="h gold" style="font-size:80px;align-self:center">⇄</span> 🇦🇪</div>
<div style="position:absolute;left:84px;right:84px;top:340px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column">
 {eyebrow_row("③ Brand story", "BEHIND THE SCENES")}
 <div class="h" style="font-size:80px;max-width:920px">Why we built an agency across <span class="gold">two countries.</span></div>
 <div style="display:flex;gap:30px;margin-top:40px">
  <div style="flex:1"><div class="h8" style="font-size:40px">Indore 🇮🇳</div><div style="font-size:27px;color:var(--mut);margin-top:12px;line-height:1.5">Cost-efficient, high-quality execution.</div></div>
  <div style="flex:1"><div class="h8 blue" style="font-size:40px">Sharjah 🇦🇪</div><div style="font-size:27px;color:var(--mut);margin-top:12px;line-height:1.5">A Gulf foothold on the ground.</div></div>
 </div>
 <div style="font-size:30px;color:#EDEDF0;margin-top:38px;max-width:900px;line-height:1.45">One team that helps you grow in India <span class="gold">and</span> the UAE — without juggling 3 vendors.</div>
 <div style="margin-top:auto">{cta_pill("Follow our story →")}</div>
</div>{brandbar(PW)}""")

# Post 9 — 3 services (Pillar 4)
A("post09_three_services", PW, PH, post_shell(f"""
 {eyebrow_row("④ Engagement · Services", "PICK YOUR LANE")}
 <div class="h" style="font-size:84px;max-width:900px">3 services. <span class="gold">1 retainer.</span></div>
 <div style="margin-top:32px">
  {chip("①","Digital Marketing","SEO, paid media & content that drive measurable pipeline.")}
  {chip("②","Branding","Identity, messaging & creative that make you memorable.","var(--gold)")}
  {chip("③","UAE–India Trade","CEPA-aware market entry, partner discovery & GTM.","var(--blue-soft)")}
 </div>
 <div style="font-size:27px;color:var(--mut);margin-top:8px">Senior-led monthly retainers · ad spend billed at cost.</div>
 <div style="margin-top:auto">{cta_pill("Which lane? DM us →")}</div>
"""))

# Post 10 — 1-page plan (Pillar 1)
A("post10_one_page_plan", PW, PH, post_shell(f"""
 {eyebrow_row("① Authority · Template", 'COMMENT "PLAN"')}
 <div class="h" style="font-size:80px;max-width:900px">The 1-page marketing plan every SME should have.</div>
 <div style="display:flex;flex-wrap:wrap;gap:18px;margin-top:42px">
  {''.join(f'<div style="flex:1 1 30%;min-width:240px;background:#141417;border:1px solid rgba(245,203,31,.22);border-radius:20px;padding:30px"><div class="h gold" style="font-size:40px">{i+1}</div><div class="h8" style="font-size:34px;margin-top:8px">{x}</div></div>' for i,x in enumerate(["Audience","Offer","Channel","Message","One metric"]))}
 </div>
 <div style="font-size:29px;color:var(--mut);margin-top:36px;max-width:880px;line-height:1.45">Define these five before you spend a rupee on ads. Want the template?</div>
 <div style="margin-top:auto">{cta_pill('Comment "PLAN" →')}</div>
"""))

# Post 11 — 5 industries (Pillar 2)
A("post11_five_industries", PW, PH, f"""
<div style="position:absolute;inset:0;background:linear-gradient(160deg,#0A1430,#0A0A0B 64%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column">
 {eyebrow_row("② UAE–India Trade", "CORRIDOR HOTLIST","var(--blue-soft)")}
 <div class="h" style="font-size:80px;max-width:900px">5 industries with the<br>biggest <span class="gold">India⇄UAE</span> upside.</div>
 <div style="margin-top:34px">
  {''.join(f'<div style="display:flex;align-items:center;gap:24px;padding:22px 0;border-top:1px solid rgba(255,255,255,.10)"><span style="font-size:50px">{ic}</span><span class="h8" style="font-size:42px">{nm}</span></div>' for ic,nm in [("🍱","F&B & FMCG"),("💻","IT / SaaS"),("💎","Jewellery & gems"),("🩺","Healthcare & wellness"),("📦","Logistics")])}
 </div>
 <div style="margin-top:auto">{cta_pill('DM "MAP" →',"var(--blue2)","#fff")}</div>
</div>{brandbar(PW,"--blue")}""")

# Post 12 — Book a call (Pillar 4, recap)
A("post12_book_call", PW, PH, f"""
<div style="position:absolute;inset:0;background:radial-gradient(120% 95% at 50% 4%,#2A2207,#0A0A0B 55%)"></div>
<div class="grain"></div>
<div style="position:absolute;left:84px;right:84px;top:96px;bottom:{int(PW*0.082)+70}px;display:flex;flex-direction:column;justify-content:center;text-align:center;align-items:center">
 <div class="eyebrow gold" style="font-size:26px;letter-spacing:.22em">MONTH ONE · DONE 🚀</div>
 <div class="h" style="font-size:118px;margin-top:26px">Ready to<br><span class="gold">grow?</span></div>
 <div style="font-size:33px;color:#EDEDF0;margin-top:34px;max-width:840px;line-height:1.45">
  More leads · a sharper brand · India⇄UAE expansion.<br>Book a free 20-min growth call.</div>
 <div style="margin-top:44px">{cta_pill("Book your free call →")}</div>
 <div style="font-size:25px;color:var(--mut);margin-top:24px">Limited slots this month · link in bio</div>
</div>{brandbar(PW)}""")

# ---- write manifest ----
with open(os.path.join(HERE, "manifest.csv"), "w", newline="") as f:
    w = csv.writer(f)
    for name, ww, hh in ASSETS:
        w.writerow([name, ww, hh])
print(f"generated {len(ASSETS)} html assets -> {HTML}")
