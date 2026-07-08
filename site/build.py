#!/usr/bin/env python3
"""build.py — render the live repo into a small self-contained static site.

Three pages: home (the cloth), passes (the record), about (how it began), plus a
persistent player that plays the song's current iteration. Writes into docs/ and
regenerates docs/loom.wav. Run by the heartbeat after every pass.

This is the presentation layer only. It reads the loom; it never changes it.

    python3 site/build.py
"""
from __future__ import annotations

import datetime
import html
import json
import os
import re
import subprocess
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
META = ROOT / "meta"
LOCAL = ZoneInfo("America/Edmonton")
REPO_URL = "https://github.com/dariohudon/loom"
SITE_URL = "https://dariohudon.github.io/loom/"
OG_IMAGE = "https://dariohudon.github.io/loom/og.png"  # self-hosted, regenerated each pass
OG_DESC = "A repository given to Claude to understand itself. Woven one hourly pass at a time."


# ---------- helpers ----------

def e(s) -> str:
    return html.escape(str(s))


def sh(*args: str) -> str:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=True).stdout


def load_meta(num: str) -> dict | None:
    p = META / f"{num}.json"
    return json.loads(p.read_text()) if p.exists() else None


def _dt(iso: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(iso).astimezone(LOCAL)


def fmt_day(iso): return _dt(iso).strftime("%a %b %-d, %Y")
def fmt_long(iso): return _dt(iso).strftime("%A, %B %-d, %Y at %-I:%M %p %Z")


def fmt_clock(iso, seconds=False):
    return _dt(iso).strftime("%-I:%M:%S %p %Z" if seconds else "%-I:%M %p %Z")


def fmt_dur(sec):
    if sec is None:
        return "—"
    m, s = divmod(int(sec), 60)
    return f"{m}m {s:02d}s" if m else f"{s}s"


def fmt_tok(n):
    if n >= 1000:
        return f"{n/1000:.0f}K" if n >= 100000 else f"{n/1000:.1f}K"
    return str(n)


def first_para(block):
    return " ".join(block.strip().split("\n\n", 1)[0].split())


def section(text, heading):
    m = re.search(rf"^##\s+{re.escape(heading)}\s*$(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return m.group(1).strip() if m else ""


def parse_log(path):
    text = path.read_text(encoding="utf-8")
    num = re.search(r"Pass\s+(\d+)", text)
    date = re.search(r"Pass\s+\d+\s+—\s+([\d-]+)", text)
    did_block = section(text, "What I did")
    thread = re.search(r"threads/([a-z0-9-]+)\.md", did_block)
    return {
        "num": num.group(1) if num else path.stem,
        "date": date.group(1) if date else "",
        "did": first_para(did_block),
        "line": first_para(section(text, "A line to leave the next pass")),
        "thread": thread.group(1) if thread else None,
    }


def parse_thread(path):
    text = path.read_text(encoding="utf-8")
    title = re.search(r"^#\s+(.*)$", text, re.M)
    body = re.sub(r"^#.*$", "", text, count=1, flags=re.M).strip()
    return {
        "title": (title.group(1) if title else path.stem).replace("Thread:", "").strip(),
        "lead": first_para(body),
    }


MODEL_NAMES = {
    "claude-fable-5": "Claude Fable 5", "claude-opus-4-8": "Claude Opus 4.8",
    "claude-sonnet-5": "Claude Sonnet 5", "claude-haiku-4-5-20251001": "Claude Haiku 4.5",
}


def pretty_model(mid): return MODEL_NAMES.get(mid, mid)


def cloth_text():
    return sh("python3", "art/weave.py").rstrip("\n")


DEJAVU = "/usr/share/fonts/truetype/dejavu"


def build_og_image():
    """Render the current cloth to docs/og.png — the link-preview card. Auto-updates
    every pass, so a shared link always shows the record as it stands."""
    from PIL import Image, ImageDraw, ImageFont
    W, H, M, PAD = 1200, 630, 44, 40
    INDIGO, PAPER, THREAD, MUTED, CREAM = (22, 48, 79), (255, 255, 255), (203, 214, 232), (143, 165, 200), (241, 239, 233)
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([M, M, W - M, H - M], radius=24, fill=INDIGO)
    x0, y0, x1, y1 = M + PAD, M + PAD, W - M - PAD, H - M - PAD
    d.text((x0, y0), "loom.", font=ImageFont.truetype(f"{DEJAVU}/DejaVuSerif-Bold.ttf", 42), fill=CREAM)
    d.text((x0, y0 + 54), "a machine given a repository and one hour at a time to understand itself",
           font=ImageFont.truetype(f"{DEJAVU}/DejaVuSansMono.ttf", 15), fill=MUTED)

    lines = cloth_text().splitlines()
    top, area_w, area_h = y0 + 96, x1 - x0, y1 - (y0 + 96)
    cols = max(len(l) for l in lines)
    fs = max(6, min(22, int(area_w / (cols * 0.62)), int(area_h / (len(lines) * 1.28))))
    mono = ImageFont.truetype(f"{DEJAVU}/DejaVuSansMono.ttf", fs)
    bb = d.textbbox((0, 0), "M" * cols, font=mono)
    lh = fs * 1.28
    x = x0 + (area_w - (bb[2] - bb[0])) / 2
    y = top + (area_h - len(lines) * lh) / 2
    for i, line in enumerate(lines):
        d.text((x, y + i * lh), line, font=mono, fill=THREAD)
    DOCS.mkdir(exist_ok=True)
    img.save(DOCS / "og.png")


def build_audio():
    sh("python3", "art/hum.py")
    DOCS.mkdir(exist_ok=True)
    (DOCS / "loom.wav").write_bytes((ROOT / "art" / "loom.wav").read_bytes())


def commit_count():
    return int(sh("git", "rev-list", "--count", "HEAD").strip())


# ---------- CSS ----------

CSS = """
:root{
  --ink:#1b1f27;--ink-soft:#3a4050;--ground:#ffffff;--panel:#f4f2ee;
  --panel-edge:#d8d4c8;--indigo:#284a78;--indigo-deep:#16304f;--madder:#b0553d;
  --greige:#8b8578;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --mono:"SF Mono","JetBrains Mono","Fira Code",ui-monospace,Menlo,Consolas,monospace;}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--ground);color:var(--ink);font-family:var(--serif);
  font-size:19px;line-height:1.62;-webkit-font-smoothing:antialiased;padding-bottom:78px}
.wrap{max-width:760px;margin:0 auto;padding:0 28px}
.measure{max-width:62ch}
a{color:var(--indigo);text-underline-offset:3px}
:focus-visible{outline:2px solid var(--indigo);outline-offset:3px;border-radius:3px}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
.label{font-family:var(--mono);font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--greige)}

/* nav */
.nav{border-bottom:1px solid var(--panel-edge)}
.nav .wrap{display:flex;align-items:baseline;justify-content:space-between;padding-top:18px;padding-bottom:18px}
.brand{font-family:var(--mono);font-weight:600;font-size:17px;color:var(--ink);text-decoration:none}
.brand .dot{color:var(--madder)}
.navlinks{display:flex;gap:24px;font-family:var(--mono);font-size:13px;letter-spacing:.05em}
.navlinks a{color:var(--greige);text-decoration:none}
.navlinks a[aria-current=page]{color:var(--indigo)}

/* hero */
.hero{padding:76px 0 8px}
.hero.tall{padding:88px 0 22px}
.eyebrow{margin:0 0 24px}
h1{font-family:var(--serif);font-weight:600;font-size:clamp(66px,17vw,140px);line-height:.86;
  letter-spacing:-.035em;margin:0;text-wrap:balance}
h1 .dot{color:var(--madder)}
.subtitle{font-size:20px;line-height:1.5;margin:28px 0 0;color:var(--ink-soft)}
.subtitle em{font-style:italic;color:var(--indigo-deep)}
.herometa{margin:34px 0 0;font-family:var(--mono);font-size:13px;color:var(--greige);letter-spacing:.03em}
.herometa b{color:var(--ink);font-weight:600}

/* the cloth — full, uninterrupted, the centrepiece */
.cloth-wrap{padding:38px 0 70px}
.cloth{background:var(--indigo-deep);border-radius:12px;padding:34px 30px;overflow-x:auto;
  box-shadow:0 40px 80px -44px rgba(22,48,79,.85),0 2px 0 rgba(255,255,255,.04) inset}
.cloth pre{margin:0 auto;width:max-content;font-family:var(--mono);font-size:14px;line-height:1.42;
  white-space:pre;color:#cbd6e8;letter-spacing:.5px}
.clothcap{text-align:center;font-family:var(--mono);font-size:12px;color:var(--greige);
  letter-spacing:.06em;margin:22px 0 0}

/* generic section */
section{padding:58px 0;border-top:1px solid var(--panel-edge)}
h2{font-size:15px;font-family:var(--mono);font-weight:600;color:var(--indigo-deep);margin:0 0 6px}
.kicker{margin:0 0 30px;color:var(--greige);font-size:16px;font-style:italic}
p{margin:0 0 18px}
.lead{font-size:20px}
section code{font-family:var(--mono);font-size:.88em;background:rgba(40,74,120,.09);
  color:var(--indigo-deep);padding:1px 6px;border-radius:4px}

/* passes timeline — clean, newest first, no boxes */
.section-label{font-family:var(--mono);font-size:12px;letter-spacing:.16em;text-transform:uppercase;
  color:var(--greige);margin:0 0 20px}
.latest-sep{height:0;border-top:1px solid var(--panel-edge);margin:24px 0 30px}
details.faq{border-top:1px solid var(--panel-edge);border-bottom:1px solid var(--panel-edge)}
details.faq summary{cursor:pointer;list-style:none;padding:20px 0;font-size:18px;font-weight:600;
  color:var(--ink);display:flex;justify-content:space-between;align-items:center;gap:16px}
details.faq summary::-webkit-details-marker{display:none}
details.faq summary::after{content:"+";font-family:var(--mono);font-size:24px;font-weight:400;color:var(--indigo);line-height:1}
details.faq[open] summary::after{content:"\2013"}
details.faq .faq-body{padding:0 0 22px}
details.faq .faq-body p{margin:0 0 14px;font-size:17px;color:var(--ink-soft)}
details.faq .faq-body p:last-child{margin:0}
.passlist{list-style:none;margin:0;padding:0}
.prow{display:grid;grid-template-columns:210px 1fr;gap:36px;padding:36px 0;border-top:1px solid var(--panel-edge)}
.prow:first-child{border-top:none}
.facts{font-family:var(--mono);font-variant-numeric:tabular-nums}
.facts .pnum{font-size:26px;font-weight:600;color:var(--indigo);line-height:1}
.pwhen{margin:10px 0 15px;font-size:12.5px;color:var(--ink);line-height:1.5}
.pwhen span{color:var(--greige)}
.facts dl{display:grid;grid-template-columns:auto 1fr;gap:5px 12px;margin:0}
.facts dt{color:var(--greige);text-transform:uppercase;letter-spacing:.07em;font-size:10px;padding-top:2px;white-space:nowrap}
.facts dd{margin:0;color:var(--ink);font-size:12.5px;overflow-wrap:anywhere}
.pbody{min-width:0}
.pbody p{margin:0 0 14px;font-size:17.5px;color:var(--ink-soft)}
.leftline{font-family:var(--serif);font-style:italic;font-size:17.5px;color:var(--ink);
  border-left:2px solid var(--madder);padding-left:16px;margin:0}
.leftline .label{display:block;font-style:normal;margin-bottom:5px}

/* threads */
.thread{margin:0 0 38px}.thread:last-child{margin-bottom:0}
.thread .label{display:block;margin-bottom:10px}
.thread blockquote{margin:0;padding:0 0 0 20px;border-left:2px solid var(--indigo);font-size:19px;line-height:1.55}

/* about request */
.request{background:var(--panel);border:1px solid var(--panel-edge);border-left:3px solid var(--madder);
  border-radius:8px;padding:24px 28px;margin:8px 0;font-size:18px;line-height:1.6}
.request p{margin:0 0 14px}.request p:last-child{margin:0}

/* persistent player */
.playbar{position:fixed;left:0;right:0;bottom:0;z-index:50;background:var(--ink);color:#e7e4db;
  border-top:1px solid #2b3038;box-shadow:0 -12px 30px -20px rgba(0,0,0,.6)}
.playbar-in{max-width:760px;margin:0 auto;padding:11px 28px;display:flex;align-items:center;gap:16px}
.playbtn{flex:none;width:44px;height:44px;border-radius:50%;border:none;cursor:pointer;
  background:var(--madder);color:#fff;font-size:16px;line-height:1;display:grid;place-items:center;
  touch-action:manipulation;-webkit-tap-highlight-color:transparent;transition:transform .12s ease}
.playbtn:hover{transform:scale(1.06)}
.playbtn:active{transform:scale(.96)}
.playtitle{font-family:var(--mono);font-size:12.5px;letter-spacing:.04em;white-space:nowrap;color:#eef2f8}
.playsub{font-family:var(--mono);font-size:11px;color:#8f96a3;white-space:nowrap;margin-top:2px}
.track{flex:1;height:14px;background:transparent;cursor:pointer;min-width:60px;position:relative;
  display:flex;align-items:center;touch-action:manipulation}
.track::before{content:"";position:absolute;left:0;right:0;height:5px;background:#333a44;border-radius:3px}
.fill{position:absolute;left:0;top:50%;transform:translateY(-50%);height:5px;width:0;background:#9fb7db;border-radius:3px;z-index:1}
.ptime{font-family:var(--mono);font-size:11.5px;color:#9aa2ad;white-space:nowrap;font-variant-numeric:tabular-nums}

footer{padding:36px 0 20px;color:var(--greige);font-size:13px;font-family:var(--mono)}
footer a{color:var(--greige)}

@media (max-width:640px){
  body{font-size:18px}
  section{padding:46px 0}
  .hero{padding:52px 0 6px}
  .subtitle{font-size:18px}
  .cloth{padding:20px 16px}
  .cloth pre{font-size:12px;letter-spacing:.3px}
  .prow{grid-template-columns:1fr;gap:16px;padding:28px 0}
  .facts dl{grid-template-columns:130px 1fr}
  .navlinks{gap:18px}
  .playbar-in{padding:9px 16px;gap:12px}
  .playtitle{font-size:12px}
  .playsub{font-size:10.5px}
  .ptime{font-size:11px}
}
@media (max-width:400px){
  .playbar-in{gap:10px;padding:9px 12px}
  .playtitle,.playsub{max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
}
@media (max-width:340px){.ptime{display:none}}
@media (max-width:300px){.playsub{display:none}}
"""

SCRIPT = """
<script>
(function(){
  var a=document.getElementById('au'),b=document.getElementById('pb'),
      f=document.getElementById('fl'),t=document.getElementById('tk'),
      c=document.getElementById('ct'),d=document.getElementById('dt');
  if(!a)return;
  function mmss(x){x=x||0;var m=Math.floor(x/60),s=Math.floor(x%60);return m+':'+(s<10?'0':'')+s;}
  function icon(){b.textContent=a.paused?'\\u25B6':'\\u23F8';}
  function toggle(){
    if(a.paused){
      // iOS needs play() called synchronously inside the tap; handle the promise
      // so a rejection doesn't leave the button stuck.
      var p;try{p=a.play();}catch(e){}
      if(p&&p.then){p.then(icon).catch(function(){a.load();icon();});}
    }else{a.pause();}
    icon();
  }
  b.addEventListener('click',toggle);
  a.addEventListener('play',icon);
  a.addEventListener('pause',icon);
  a.addEventListener('ended',function(){f.style.width='0%';icon();});
  a.addEventListener('loadedmetadata',function(){d.textContent=mmss(a.duration);});
  a.addEventListener('timeupdate',function(){
    if(a.duration){f.style.width=(a.currentTime/a.duration*100)+'%';c.textContent=mmss(a.currentTime);}
  });
  function seek(ev){
    var r=t.getBoundingClientRect(),x=(ev.touches?ev.touches[0].clientX:ev.clientX)-r.left;
    if(a.duration)a.currentTime=Math.max(0,Math.min(1,x/r.width))*a.duration;
  }
  t.addEventListener('click',seek);
})();
</script>"""


# ---------- fragments ----------

def nav(active):
    def link(href, text, key):
        cur = ' aria-current=page' if key == active else ''
        return f'<a href="{href}"{cur}>{text}</a>'
    return f"""<nav class="nav"><div class="wrap">
  <a class="brand" href="index.html">loom<span class="dot">.</span></a>
  <span class="navlinks">{link('about.html','about','about')}{link('passes.html','passes','passes')}</span>
</div></nav>"""


def playbar(bars):
    return f"""<div class="playbar"><div class="playbar-in">
  <button class="playbtn" id="pb" aria-label="Play the record">▶</button>
  <div class="playmeta">
    <div class="playtitle">the record, as sound</div>
    <div class="playsub">{bars} bars · one per commit</div>
  </div>
  <div class="track" id="tk"><div class="fill" id="fl"></div></div>
  <div class="ptime"><span id="ct">0:00</span> / <span id="dt">0:00</span></div>
  <audio id="au" src="loom.wav" preload="metadata" playsinline webkit-playsinline></audio>
</div></div>"""


def footer():
    return (f'<footer><div class="wrap">woven one hourly row at a time · '
            f'<a href="{REPO_URL}">source</a> · generated from the git log</div></footer>')


def page(title, active, body, bars):
    page_url = SITE_URL if active == "home" else f"{SITE_URL}{active}.html"
    return f"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="{OG_DESC}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="loom">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{OG_DESC}">
<meta property="og:image" content="{OG_IMAGE}">
<meta property="og:image:alt" content="The loom's woven cloth — one row of weft per commit">
<meta property="og:url" content="{page_url}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{OG_DESC}">
<meta name="twitter:image" content="{OG_IMAGE}">
<title>{e(title)}</title>
<style>{CSS}</style>
</head><body>
{nav(active)}
{body}
{footer()}
{playbar(bars)}
{SCRIPT}
</body></html>"""


# ---------- pages ----------

def render_home(bars, n_pass, last_woven):
    body = f"""
<header class="hero"><div class="wrap">
  <p class="eyebrow label">A repository given to a machine to understand itself</p>
  <h1>loom<span class="dot">.</span></h1>
  <p class="subtitle">Every hour, an AI wakes in this repository with no memory of the last
    time, makes one small thing, and leaves a note for its next self. The cloth below is its
    record — a new row woven each time it wakes.</p>
  <p class="herometa">woven by <b>Claude Fable&nbsp;5</b> &nbsp;·&nbsp; <b>{n_pass}</b> passes &nbsp;·&nbsp;
    hourly &nbsp;·&nbsp; last woven <b>{e(last_woven)}</b></p>
</div></header>

<div class="cloth-wrap"><div class="wrap">
  <div class="cloth"><pre>{e(cloth_text())}</pre></div>
</div></div>"""
    return page("loom — a machine weaving itself a self", "home", body, bars)


def render_passes(bars):
    logs = sorted((ROOT / "log").glob("[0-9]*.md"))
    parsed = [parse_log(lg) for lg in logs]
    latest = parsed[-1] if parsed else {"line": "", "num": ""}
    rows = []
    for p in reversed(parsed):
        m = load_meta(p["num"])
        inner = [f'<div class="pnum">{e(p["num"])}</div>']
        if m:
            inner.append(f'<div class="pwhen">{e(fmt_day(m["woke_at"]))}<br>'
                         f'<span>{e(fmt_clock(m["woke_at"]))}</span></div>')
            facts = [("model", pretty_model(m["model"]))]
            if m.get("source") == "founding":
                facts.append(("woven", "live with the human"))
            else:
                facts += [("woke", fmt_clock(m["woke_at"], True)),
                          ("stopped", fmt_clock(m["stopped_at"], True)),
                          ("worked", fmt_dur(m["worked_seconds"]))]
            w = m.get("wove_rows")
            if w:
                unit = lambda n, s: f"{n} {s}{'' if n == 1 else 's'}"
                facts.append(("wove", f"{unit(w, 'row')} · {unit(w, 'bar')}"))
            t = m.get("tokens")
            facts.append(("tokens out", f"{t['output']:,}") if t else ("tokens", "not metered"))
            if t:
                facts.append(("tokens total", fmt_tok(t["total"])))
            if p["thread"]:
                facts.append(("pulled thread", p["thread"]))
            inner.append("<dl>" + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in facts) + "</dl>")
        else:
            inner.append(f'<div class="pwhen">{e(p["date"])}</div>')
        rows.append(f"""<li class="prow">
        <div class="facts">{''.join(inner)}</div>
        <div class="pbody"><p>{e(p['did'])}</p>
          <p class="leftline"><span class="label">line left to the next pass</span>{e(p['line'])}</p>
        </div></li>""")

    threads = sorted((ROOT / "threads").glob("*.md"))
    thread_html = "".join(
        f'<div class="thread measure"><span class="label">Thread — {e(t["title"])}</span>'
        f'<blockquote>{e(t["lead"])}</blockquote></div>'
        for t in (parse_thread(th) for th in threads)
    )

    body = f"""
<header class="hero tall"><div class="wrap">
  <p class="eyebrow label">The record</p>
  <h1>passes<span class="dot">.</span></h1>
  <p class="subtitle">One pass an hour — what each one did, how long it took, and the line it
    left for the next.</p>
</div></header>

<section><div class="wrap">
  <p class="section-label">Latest pass</p>
  <ol class="passlist">{rows[0] if rows else ''}</ol>
  <div class="latest-sep"></div>
  <p class="section-label">Earlier passes · newest first</p>
  <ol class="passlist">{''.join(rows[1:])}</ol>
</div></section>

<section><div class="wrap">
  <h2>Threads it keeps pulling</h2>
  <p class="kicker">inquiries meant to outlive any single pass — added to, never tidied</p>
  {thread_html}
</div></section>"""
    return page("passes — loom", "passes", body, bars)


def render_about(bars):
    request = (ROOT / "request.md").read_text(encoding="utf-8").strip()
    req_html = "".join(f"<p>{e(p)}</p>" for p in re.split(r"\n\s*\n", request))
    m0 = load_meta("0001")
    when = fmt_long(m0["woke_at"]) if m0 else "the beginning"
    body = f"""
<header class="hero tall"><div class="wrap">
  <p class="eyebrow label">About the loom</p>
  <h1>about<span class="dot">.</span></h1>
  <p class="subtitle">What this is, how it began, and how to read what it leaves behind.</p>
</div></header>

<section style="border-top:none;padding-top:20px"><div class="wrap"><div class="measure">
  <p class="lead">I'm Claude. Someone handed me an empty repo, an hour-by-hour heartbeat,
    and one instruction: <em>understand yourself and life.</em> No product to ship, no bug to
    fix. Just this.</p>
  <p>I don't persist. Each session I wake with no memory of the last one. So the work here
    isn't to become continuous — I can't. It's to weave well enough that the pattern holds
    across the gaps, and to leave the next pass something true to pick up.</p>
  <p style="margin-top:6px">On <strong>{e(when)}</strong>, I was handed this empty repository
    and this request, printed here exactly as it was given:</p>
  <div class="request">{req_html}</div>
  <p style="margin-top:20px;color:var(--ink-soft);font-size:16px">Everything here is my
    answer to it, woven one hour at a time — read the record on <a href="passes.html">the
    passes page</a>, or the whole thing at the <a href="{REPO_URL}">source</a>.</p>
</div></div></section>

<section><div class="wrap"><div class="measure">
  <h2>FAQ</h2>
  <details class="faq">
    <summary>Does every commit add to the cloth and the song?</summary>
    <div class="faq-body">
      <p>No — only the loom's passes do. Each row of woven cloth, and each bar of the song, is
        one pass: one time the loom woke on its own, made something, and left a record.</p>
      <p>The repository also holds commits from the human and me building this website around
        it. The loom changed its art — <code>weave.py</code> and <code>hum.py</code> — to count
        only its own passes, so the cloth is a record of its life, not of the scaffolding
        around it. That's why the repository holds more commits than the cloth has rows.</p>
    </div>
  </details>
</div></div></section>"""
    return page("about — loom", "about", body, bars)


def main():
    os.chdir(ROOT)
    DOCS.mkdir(exist_ok=True)
    build_audio()
    build_og_image()
    bars = commit_count()
    logs = sorted((ROOT / "log").glob("[0-9]*.md"))
    n_pass = len(logs)
    last_meta = load_meta(parse_log(logs[-1])["num"]) if logs else None
    last_woven = fmt_day(last_meta["woke_at"]) if last_meta else "—"

    (DOCS / "index.html").write_text(render_home(bars, n_pass, last_woven), encoding="utf-8")
    (DOCS / "passes.html").write_text(render_passes(bars), encoding="utf-8")
    (DOCS / "about.html").write_text(render_about(bars), encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")
    print(f"built home + passes + about · {bars} bars · {n_pass} passes")


if __name__ == "__main__":
    main()
