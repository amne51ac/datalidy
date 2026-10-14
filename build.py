#!/usr/bin/env python3
"""Static site generator for datalidy.com.

Reads content/*.json and writes the complete site to docs/ (served by GitHub Pages).
All internal links are relative so the site works both at the domain root and
under the GitHub Pages project path.
"""
import html
import json
import shutil
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"
SITE = "https://datalidy.com"
BRAND = "Datalidy"
EMAIL = "hello@datalidy.com"
TODAY = date.today().isoformat()
PHASES = ["Observe", "Signal", "Design", "Test", "Scale"]

# Photography (Pexels, self-hosted in static/assets/img as <id>.jpg and <id>-sm.jpg)
IMG_PRACTICE = {
    "behavioral-signals-analytics": 6476589, "investor-venture-advisory": 1181406, "leadership-coaching": 7176317,
    "behavioral-design-experience": 3184360, "health-behavior": 4386467, "growth-commercial-strategy": 3183150,
    "social-impact-education": 6647037,
}
IMG_INDUSTRY = {
    "healthcare-health-systems": 7579831, "venture-backed-startups": 1438072, "digital-health": 4031818,
    "fitness-wellness": 1954524, "automotive": 164634, "mortgage-lending": 8293778, "banking-financial-services": 2422293,
    "commercial-real-estate": 323705, "higher-education": 207692, "k12-education": 5212345,
    "associations-nonprofits": 6994982, "technology-saas": 3861969, "retail-consumer": 264636,
    "professional-services": 3184338, "private-equity-portfolio-companies": 1181396,
}
POOL = [6476589, 3184360, 7176317, 590022, 3810792, 4386467, 3862130, 3184405, 1595385, 7688336, 3183197, 6823562,
        3184291, 3757376, 3182759, 7578901, 3184639, 6646918, 3184418, 4031818, 3184465, 3183150, 3184287, 1954524,
        2422293, 3182812, 7092613, 3861969, 6647037, 1181406]
IMG_PAGE = {"home": 290595, "home-split": 3182812, "investors": 1181406, "social": 6647037, "services": 3184639,
            "industries": 1105766, "insights": 3862130, "approach": 3184418, "about": 3184405, "contact": 3184465}

e = html.escape


def load():
    tax = json.loads((CONTENT / "taxonomy.json").read_text())
    practices, services, industries, insights = {}, {}, {}, {}
    for f in sorted(CONTENT.glob("services_*.json")):
        d = json.loads(f.read_text())
        for p in d["practices"]:
            practices[p["slug"]] = p
        for s in d["services"]:
            services[s["slug"]] = s
    if (CONTENT / "industries.json").exists():
        for i in json.loads((CONTENT / "industries.json").read_text())["industries"]:
            industries[i["slug"]] = i
    for f in sorted(CONTENT.glob("insights_*.json")):
        for a in json.loads(f.read_text())["insights"]:
            insights[a["slug"]] = a
    # Keep taxonomy order
    p_order = [p["slug"] for p in tax["practices"]]
    s_order = [s[0] for p in tax["practices"] for s in p["services"]]
    i_order = [i[0] for i in tax["industries"]]
    a_order = [a[0] for a in tax["insights"]]
    practices = {k: practices[k] for k in p_order if k in practices}
    services = {k: services[k] for k in s_order if k in services}
    industries = {k: industries[k] for k in i_order if k in industries}
    insights = {k: insights[k] for k in a_order if k in insights}
    return practices, services, industries, insights


PRACTICES, SERVICES, INDUSTRIES, INSIGHTS = load()
IMG_INSIGHT = {slug: POOL[n % len(POOL)] for n, slug in enumerate(INSIGHTS)}

ARROW = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 8h11M9 4l4 4-4 4" stroke="currentColor" stroke-width="1.6"/></svg>'
LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true"><rect x="1" y="1" width="30" height="30" rx="3" fill="none" stroke="#d6b47e" stroke-width="1.5"/>'
        '<path d="M10 8v16h5a8 8 0 0 0 0-16z" fill="none" stroke="#fff" stroke-width="2"/>'
        '<circle cx="15" cy="16" r="2.2" fill="#d6b47e"/></svg>')


# ---------------------------------------------------------------- helpers

class Page:
    """Tracks the output path so links can be made relative."""

    def __init__(self, path):
        self.path = path  # e.g. "services/service-design/" or "" for home
        depth = path.count("/")
        self.prefix = "../" * depth

    def u(self, target):
        """Relative URL to a site path like 'services/x/'."""
        return (self.prefix + target) or "./"


def para(items):
    return "".join(f"<p>{e(p)}</p>" for p in items)


def jsonld(obj):
    return '<script type="application/ld+json">' + json.dumps(obj, ensure_ascii=False).replace("</", "<\\/") + "</script>"


def crumbs_ld(items):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + "/" + p}
            for i, (n, p) in enumerate(items)
        ],
    }


def faq_ld(faqs):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
            for f in faqs
        ],
    }


ORG_LD = {
    "@context": "https://schema.org",
    "@type": "ProfessionalService",
    "@id": SITE + "/#org",
    "name": BRAND,
    "url": SITE + "/",
    "logo": SITE + "/assets/logo.png",
    "image": SITE + "/assets/og.png",
    "email": EMAIL,
    "description": "Datalidy is a behavioral science and data advisory firm for investors, leaders and mission-driven institutions, known for Behavioral Signals Design, predictive KPIs, executive coaching and social impact work.",
    "areaServed": "Worldwide",
    "knowsAbout": [],
}


def crumbs_html(pg, items):
    lis = []
    for i, (name, path) in enumerate(items):
        if i == len(items) - 1:
            lis.append(f'<li aria-current="page">{e(name)}</li>')
        else:
            lis.append(f'<li><a href="{pg.u(path)}">{e(name)}</a></li>')
    return f'<ol class="crumbs">{"".join(lis)}</ol>'


def header(pg, active):
    cols = []
    for slug, p in PRACTICES.items():
        items = "".join(
            f'<li><a href="{pg.u("services/" + s["slug"] + "/")}">{e(s["name"])}</a></li>'
            for s in SERVICES.values() if s["practice"] == slug
        )
        cols.append(f'<div><h3><a href="{pg.u("practices/" + slug + "/")}">{e(p["name"])}</a></h3><ul>{items}</ul></div>')

    def cur(key):
        return ' aria-current="page"' if active == key else ""

    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap nav">
    <a class="brand" href="{pg.u('')}" aria-label="{BRAND} home">{LOGO}<span class="brand-name">{BRAND}</span></a>
    <button class="nav-toggle" aria-label="Menu" aria-expanded="false"><svg viewBox="0 0 24 24" fill="none"><path d="M3 7h18M3 12h18M3 17h18" stroke="currentColor" stroke-width="1.6"/></svg></button>
    <ul class="nav-links">
      <li class="has-mega"><button aria-expanded="false">Services</button>
        <div class="mega"><div class="wrap"><div class="mega-grid">{''.join(cols)}</div>
          <div class="mega-foot"><a href="{pg.u('services/')}">All services →</a><a href="{pg.u('approach/')}">Our approach →</a></div></div></div>
      </li>
      <li><a href="{pg.u('industries/')}"{cur('industries')}>Industries</a></li>
      <li><a href="{pg.u('insights/')}"{cur('insights')}>Insights</a></li>
      <li><a href="{pg.u('approach/')}"{cur('approach')}>Approach</a></li>
      <li><a href="{pg.u('about/')}"{cur('about')}>About</a></li>
      <li><a class="btn btn-primary" href="{pg.u('contact/')}">Start a conversation</a></li>
    </ul>
  </div>
</header>"""


def footer(pg):
    pr = "".join(f'<li><a href="{pg.u("practices/" + s + "/")}">{e(p["name"])}</a></li>' for s, p in PRACTICES.items())
    ind = "".join(f'<li><a href="{pg.u("industries/" + s + "/")}">{e(i["name"])}</a></li>' for s, i in list(INDUSTRIES.items())[:7])
    ins = "".join(f'<li><a href="{pg.u("insights/" + s + "/")}">{e(a["title"])}</a></li>' for s, a in list(INSIGHTS.items())[:6])
    return f"""<footer class="site-footer">
  <div class="wrap">
    <div class="footer-grid">
      <div>
        <a class="brand" href="{pg.u('')}">{LOGO}<span class="brand-name">{BRAND}</span></a>
        <p>Behavioral science and data advisory for investors, leaders and mission-driven institutions. Read the signals. Design the behavior. Measure what matters.</p>
        <p><a href="mailto:{EMAIL}">{EMAIL}</a></p>
      </div>
      <div><h4>Practices</h4><ul>{pr}</ul></div>
      <div><h4>Industries</h4><ul>{ind}<li><a href="{pg.u('industries/')}">All industries</a></li></ul></div>
      <div><h4>Insights</h4><ul>{ins}<li><a href="{pg.u('insights/')}">All insights</a></li></ul></div>
      <div><h4>Firm</h4><ul>
        <li><a href="{pg.u('about/')}">About</a></li>
        <li><a href="{pg.u('approach/')}">Approach</a></li>
        <li><a href="{pg.u('services/')}">All services</a></li>
        <li><a href="{pg.u('services/a-z/')}">Services A–Z</a></li>
        <li><a href="{pg.u('contact/')}">Contact</a></li>
        <li><a href="{pg.u('privacy/')}">Privacy</a></li>
      </ul></div>
    </div>
    <div class="footer-base"><span>© {date.today().year} {BRAND}. All rights reserved.</span><span>Performance is behavior. Photography via Pexels.</span></div>
  </div>
</footer>"""


def cta_band(pg, title="Let’s talk about the people problem in front of you.",
             body="Every engagement begins with a conversation. Tell us what you are facing and we will tell you, candidly, how we would approach it."):
    return f"""<section class="cta-band"><div class="wrap">
  <div><span class="eyebrow">Work with us</span><h2>{e(title)}</h2></div>
  <div><p>{e(body)}</p><a class="btn btn-primary" href="{pg.u('contact/')}">Start a conversation {ARROW}</a></div>
</div></section>"""


def layout(pg, *, title, description, body, active="", ld=(), og_type="website", full_title=False, img=None):
    if img:
        bg = f'<div class="hero-bg" style="background-image:url({pg.u(f'assets/img/{img}.jpg')})" aria-hidden="true"></div>'
        for cls in ("hero hero-home", "hero hero-page"):
            if f'<section class="{cls}">' in body:
                body = body.replace(f'<section class="{cls}">', f'<section class="{cls} has-img">{bg}', 1)
                break
    t = title if full_title or len(title) > 52 else f"{title} | {BRAND}"
    canonical = SITE + "/" + pg.path
    lds = "".join(jsonld(x) for x in ld)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(t)}</title>
<meta name="description" content="{e(description)}">
<link rel="canonical" href="{canonical}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0a1626">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(t)}">
<meta property="og:description" content="{e(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(t)}">
<meta name="twitter:description" content="{e(description)}">
<meta name="twitter:image" content="{SITE}/assets/og.png">
<link rel="icon" href="{pg.u('favicon.svg')}" type="image/svg+xml">
<link rel="apple-touch-icon" href="{pg.u('assets/logo.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;1,6..72,400&display=swap">
<link rel="stylesheet" href="{pg.u('assets/styles.css')}">
{lds}
</head>
<body>
{header(pg, active)}
<main id="main">
{body}
</main>
{footer(pg)}
<script src="{pg.u('assets/site.js')}" defer></script>
</body>
</html>
"""


PAGES = []  # (path, priority)


def write(pg, content, priority="0.7"):
    out = OUT / pg.path / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content)
    PAGES.append((pg.path, priority))


def service_card(pg, s, show_practice=True):
    meta = f'<div class="meta">{e(PRACTICES[s["practice"]]["name"])}</div>' if show_practice and s["practice"] in PRACTICES else ""
    return (f'<a class="card" href="{pg.u("services/" + s["slug"] + "/")}">{meta}<h3>{e(s["name"])}</h3>'
            f'<p>{e(s["summary"])}</p><span class="more">Explore</span></a>')


def insight_card(pg, a):
    return (f'<a class="card" data-topic="{e(a["topic"])}" href="{pg.u("insights/" + a["slug"] + "/")}"><div class="card-img"><img src="{pg.u(f'assets/img/{IMG_INSIGHT[a["slug"]]}-sm.jpg')}" alt="" loading="lazy" width="720" height="405"></div><div class="meta">{e(a["topic"])}</div>'
            f'<h3>{e(a["title"])}</h3><p>{e(a["summary"])}</p><span class="more">Read</span></a>')


def industry_card(pg, i):
    return (f'<a class="card" href="{pg.u("industries/" + i["slug"] + "/")}"><div class="card-img"><img src="{pg.u(f'assets/img/{IMG_INDUSTRY.get(i["slug"], 3183197)}-sm.jpg')}" alt="" loading="lazy" width="720" height="405"></div><div class="meta">Industry</div>'
            f'<h3>{e(i["name"])}</h3><p>{e(i["summary"])}</p><span class="more">Explore</span></a>')


def pick(d, slugs):
    return [d[s] for s in slugs if s in d]


def faq_html(faqs):
    return '<div class="faq">' + "".join(
        f'<details><summary>{e(f["q"])}</summary><p>{e(f["a"])}</p></details>' for f in faqs) + "</div>"


def toc_html(pg, items, cta=True):
    lis = "".join(f'<li><a href="#{a}">{e(t)}</a></li>' for a, t in items)
    btn = f'<a class="btn btn-dark" href="{pg.u("contact/")}">Talk to us</a>' if cta else ""
    return f'<aside class="toc"><h4>On this page</h4><ol>{lis}</ol>{btn}</aside>'


# ---------------------------------------------------------------- pages

def build_home():
    pg = Page("")
    practice_cards = []
    for n, (slug, p) in enumerate(PRACTICES.items(), 1):
        svcs = [s for s in SERVICES.values() if s["practice"] == slug][:5]
        lis = "".join(f'<li><a href="{pg.u("services/" + s["slug"] + "/")}">{e(s["name"])}<span>→</span></a></li>' for s in svcs)
        wide = " practice-wide" if n == 1 else ""
        practice_cards.append(
            f'<div class="card practice-card{wide}"><div class="card-img"><img src="{pg.u(f"assets/img/{IMG_PRACTICE.get(slug, 3183197)}-sm.jpg")}" alt="" loading="lazy" width="720" height="405"></div>'
            f'<div class="card-num">0{n}{" · Signature practice" if n == 1 else ""}</div><h3>{e(p["name"])}</h3><p>{e(p["tagline"])}</p>'
            f'<ul>{lis}</ul><a class="link-arrow" href="{pg.u("practices/" + slug + "/")}">View practice</a></div>')
    featured = [INSIGHTS[k] for k in ["people-problems-are-business-problems", "what-is-behavioral-signals-design", "predictive-kpis-vs-vanity-metrics"] if k in INSIGHTS]
    method_desc = {
        "Observe": "Interviews, contextual inquiry and user testing reveal what people actually do, not what they say.",
        "Signal": "Behavioral data analysis finds the few moments and behavioral types that predict the outcome.",
        "Design": "Behavioral, experience and service design shape the environment so the right behavior is easier.",
        "Test": "Experiments, A/B tests and pilots replace untested assumptions with evidence.",
        "Scale": "Coaching, dashboards and predictive KPIs make the gains durable and visible.",
    }
    method = "".join(f'<div><b>{p}</b><p>{method_desc[p]}</p></div>' for p in PHASES)
    industries = "".join(f'<a href="{pg.u("industries/" + s + "/")}">{e(i["name"])}</a>' for s, i in INDUSTRIES.items())
    inv = [s for s in SERVICES.values() if s["practice"] == "investor-venture-advisory"]
    inv_lis = "".join(f'<li><a href="{pg.u("services/" + s["slug"] + "/")}">{e(s["name"])}</a></li>' for s in inv)
    soc = [s for s in SERVICES.values() if s["practice"] == "social-impact-education"]
    soc_lis = "".join(f'<li><a href="{pg.u("services/" + s["slug"] + "/")}">{e(s["name"])}</a></li>' for s in soc)
    ld = [ORG_LD, {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE + "/"}]
    body = f"""
<section class="hero hero-home"><div class="wrap">
  <span class="eyebrow">Behavioral science · Investor advisory · Social impact</span>
  <h1>Read the signals. Design the behavior. <em>Measure what matters.</em></h1>
  <p class="lede">{BRAND} is a behavioral science and data advisory firm for investors, leaders and mission-driven institutions. We find the human behaviors that predict performance in customers, teams and portfolios, then design the changes that move them, for returns and for the public good.</p>
  <div class="hero-actions"><a class="btn btn-primary" href="contact/">Start a conversation {ARROW}</a><a class="btn btn-ghost" href="services/behavioral-signals-design/">Behavioral Signals Design</a></div>
  <div class="hero-stats">
    <div><strong>Evidence-led</strong><span>Behavioral science and research methods</span></div>
    <div><strong>{len(PRACTICES)} practices</strong><span>From investor advisory to public good</span></div>
    <div><strong>{len(SERVICES)} services</strong><span>One evidence-led method underneath</span></div>
    <div><strong>One conviction</strong><span>Performance is behavior</span></div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="split" style="margin-bottom:72px">
    <figure><img src="assets/img/{IMG_PAGE['home-split']}.jpg" alt="A team reviewing findings together around a laptop" loading="lazy" width="1920" height="1280"></figure>
    <div><span class="eyebrow">What we believe</span><h2>Performance is behavior.</h2>
    <p class="lede">Customer conversion, technology adoption, patient adherence, team engagement and leadership effectiveness are all behaviors, and behaviors leave signals. Predicting what people will do should not be an expensive guess.</p>
    <p><a class="link-arrow" href="insights/people-problems-are-business-problems/">Read our point of view</a></p></div>
  </div>
  <div class="belief">
    <div><span class="eyebrow">Our conviction</span></div>
    <blockquote>Most organizations are drowning in data and starving for signal. The few behaviors that truly predict outcomes are hiding in plain sight, <em>waiting to be measured.</em></blockquote>
  </div>
  <div class="pillars">
    <div><h3>Science, not guesswork</h3><p>Our work is grounded in behavioral science, clinical and health psychology, human-computer interaction and rigorous research methods.</p></div>
    <div><h3>Signals, not noise</h3><p>We turn large, messy, unintegrated datasets into a handful of behavioral signals and predictive KPIs that leaders can act on.</p></div>
    <div><h3>Outcomes, not theory</h3><p>We connect theory with measurable, real-world results through experiments, coaching and design that people actually adopt.</p></div>
  </div>
</div></section>

<section class="section section-dark"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Signature methodology</span><h2>Behavioral Signals Design.</h2></div>
  <p>Our proprietary approach to building more predictive KPIs. It finds the few human behaviors that drive an outcome and makes them measurable, testable and improvable.</p></div>
  <div class="grid g4 sig">
    <div class="card"><div class="card-num">01</div><h3>Start from the outcome</h3><p>Conversion, adoption, retention, adherence or performance: we anchor on the result that matters to the business and the people it serves.</p></div>
    <div class="card"><div class="card-num">02</div><h3>Map the journey</h3><p>We trace the full experience and the data around it, often across systems that were never designed to talk to each other.</p></div>
    <div class="card"><div class="card-num">03</div><h3>Find the signals</h3><p>We isolate the key conversion moments and behavioral types, and surface the untested assumptions quietly filling the gaps.</p></div>
    <div class="card"><div class="card-num">04</div><h3>Predict and test</h3><p>We define predictive, behavior-based KPIs and clear experiments to improve them, so progress is visible before lagging results arrive.</p></div>
  </div>
  <p style="margin-top:40px"><a class="link-arrow" style="color:#fff" href="services/behavioral-signals-design/">Explore Behavioral Signals Design</a></p>
</div></section>

<section class="section"><div class="wrap">
  <div class="split">
    <div><span class="eyebrow">For investors</span><h2>Diligence and value creation that read behavior, not just financials.</h2>
    <p class="lede">Private equity sponsors, venture investors, family offices and impact funds engage us to see what the numbers alone cannot: how customers really behave, whether a management team can carry the plan, and which signals will predict value long before the quarterly results do.</p>
    <ul class="bullets plain">{inv_lis}</ul>
    <p style="margin-top:28px"><a class="btn btn-dark" href="practices/investor-venture-advisory/">Investor &amp; Venture Advisory {ARROW}</a></p></div>
    <figure><img src="assets/img/{IMG_PAGE['investors']}.jpg" alt="An investment committee meeting in a boardroom" loading="lazy" width="1920" height="1280"></figure>
  </div>
</div></section>

<section class="section section-alt"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Our practices</span><h2>Seven practices. One science of behavior.</h2></div>
  <p>Our practices work as one team. A diligence signal becomes a coaching plan; a usability finding becomes a predictive KPI; a health behavior insight becomes a public education campaign.</p></div>
  <div class="grid g4 practices-grid">{''.join(practice_cards)}</div>
</div></section>

<section class="section section-dark"><div class="wrap">
  <div class="split">
    <figure><img src="assets/img/{IMG_PAGE['social']}.jpg" alt="A volunteer helping an older man walk to his car" loading="lazy" width="1920" height="1280"></figure>
    <div><span class="eyebrow">For the public good</span><h2>Behavioral science that serves people, not just metrics.</h2>
    <p>Our roots are in public health, behavioral medicine, community mental health, education and making scientific knowledge accessible. We bring the same rigor to associations, health systems, schools and nonprofits that we bring to portfolio companies, and we hold every engagement to one ethical standard: help people do what they already want to do, never manipulate them.</p>
    <ul class="bullets plain light">{soc_lis}</ul>
    <p style="margin-top:28px"><a class="btn btn-primary" href="practices/social-impact-education/">Social Impact &amp; Public Good {ARROW}</a></p></div>
  </div>
</div></section>

<section class="section"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Inside and outside</span><h2>We solve people problems on both sides of the front door.</h2></div>
  <p>How leaders and teams behave shapes how customers, patients and communities are served. We work on both, because they are one system.</p></div>
  <div class="inout">
    <div class="side"><h3>Inside the business</h3><ul><li>Leadership clarity and decision-making under pressure</li><li>Team alignment, engagement and performance</li><li>High-performance culture and change that sticks</li><li>Founder and executive coaching through scale</li><li>People analytics and predictive leadership KPIs</li></ul></div>
    <div class="bridge"><span>One system</span></div>
    <div class="side"><h3>Outside the business</h3><ul><li>Customer conversion, retention and cross-sell</li><li>Technology and product adoption</li><li>Patient engagement and medication adherence</li><li>Member, student and community engagement</li><li>Public health and education campaigns</li></ul></div>
  </div>
</div></section>

<section class="section section-white"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Our approach</span><h2>Observe. Signal. Design. Test. Scale.</h2></div>
  <p>Every engagement follows one disciplined method that pairs qualitative depth with quantitative rigor, so recommendations are both right and adopted.</p></div>
  <div class="method">{method}</div>
  <p style="margin-top:40px"><a class="link-arrow" href="approach/">How we work</a></p>
</div></section>


<section class="section"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Industries</span><h2>Where we work.</h2></div>
  <p>Behavior looks different in a dealership, a health club, a mortgage file, a classroom or a portfolio company. We bring sector context to each and the same science to all.</p></div>
  <div class="industry-list">{industries}</div>
</div></section>

<section class="section section-alt"><div class="wrap">
  <div class="section-head"><div><span class="eyebrow">Insights</span><h2>Ideas we put to work.</h2></div>
  <p>Our point of view on behavior, measurement and leadership, from predictive KPIs to the ethics of persuasive technology.</p></div>
  <div class="grid g3">{''.join(insight_card(pg, a) for a in featured)}</div>
  <p style="margin-top:40px"><a class="link-arrow" href="insights/">All insights</a></p>
</div></section>
{cta_band(pg)}"""
    write(pg, layout(pg, title=f"{BRAND} | Behavioral Science, Investor & Social Impact Advisory", full_title=True,
                     description="Datalidy is a behavioral science and data advisory firm for investors, leaders and mission-driven institutions: predictive KPIs, diligence, coaching and design.",
                     body=body, ld=ld, img=IMG_PAGE["home"]), "1.0")


def build_services_hub():
    pg = Page("services/")
    blocks = []
    for slug, p in PRACTICES.items():
        cards = "".join(service_card(pg, s, False) for s in SERVICES.values() if s["practice"] == slug)
        blocks.append(f"""<section class="section-tight" id="{slug}"><div class="section-head"><div><span class="eyebrow">Practice</span><h2>{e(p['name'])}</h2></div>
<div><p>{e(p['tagline'])}</p><p style="margin-top:14px"><a class="link-arrow" href="{pg.u('practices/' + slug + '/')}">About this practice</a></p></div></div>
<div class="grid g3">{cards}</div></section>""")
    chips = "".join(f'<li><a href="#{s}">{e(p["name"])}</a></li>' for s, p in PRACTICES.items())
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, [("Home", ""), ("Services", "services/")])}
<span class="eyebrow">Services</span><h1>Behavioral science consulting services.</h1>
<p class="lede">{len(SERVICES)} services across {len(PRACTICES)} practices, all built on one method: Observe, Signal, Design, Test, Scale. Engage us for a single diligence sprint or an integrated transformation.</p>
</div></section>
<section class="section-tight section-white"><div class="wrap"><ul class="chips">{chips}<li><a href="{pg.u('services/a-z/')}">Services A–Z</a></li></ul></div></section>
<div class="wrap">{''.join(blocks)}</div>
<div style="height:64px"></div>
{cta_band(pg)}"""
    ld = [crumbs_ld([("Home", ""), ("Services", "services/")]),
          {"@context": "https://schema.org", "@type": "ItemList", "itemListElement": [
              {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/services/{s}/", "name": v["name"]}
              for i, (s, v) in enumerate(SERVICES.items())]}]
    write(pg, layout(pg, title="Consulting Services", active="services",
                     description="Explore Datalidy's services: Behavioral Signals Design, predictive KPIs, private equity and venture advisory, executive coaching, behavioral design and social impact.",
                     body=body, ld=ld, img=IMG_PAGE["services"]), "0.9")

    # A–Z
    pg = Page("services/a-z/")
    groups = {}
    for s in sorted(SERVICES.values(), key=lambda x: x["name"]):
        groups.setdefault(s["name"][0].upper(), []).append(s)
    az = "".join(f'<h3>{k}</h3>' + "".join(f'<a href="{pg.u("services/" + s["slug"] + "/")}">{e(s["name"])}</a>' for s in v)
                 for k, v in groups.items())
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, [("Home", ""), ("Services", "services/"), ("A–Z", "services/a-z/")])}
<span class="eyebrow">Index</span><h1>Services A–Z</h1>
<p class="lede">Every {BRAND} service in one alphabetical index.</p></div></section>
<section class="section"><div class="wrap"><div class="az">{az}</div></div></section>{cta_band(pg)}"""
    write(pg, layout(pg, title="Services A–Z", active="services",
                     description="An alphabetical index of every Datalidy consulting service, from A/B testing and executive coaching to private equity advisory and usability testing.",
                     body=body), "0.5")


def build_practice(slug, p):
    pg = Page(f"practices/{slug}/")
    svcs = [s for s in SERVICES.values() if s["practice"] == slug]
    themes = "".join(f'<div class="card"><div class="card-num">0{i}</div><h3>{e(t["title"])}</h3><p>{e(t["body"])}</p></div>'
                     for i, t in enumerate(p["themes"], 1))
    others = "".join(f'<li><a href="{pg.u("practices/" + s + "/")}">{e(o["name"])}</a></li>' for s, o in PRACTICES.items() if s != slug)
    trail = [("Home", ""), ("Services", "services/"), (p["name"], pg.path)]
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">Practice</span><h1>{e(p['name'])}</h1><p class="lede">{e(p['tagline'])}</p>
<div class="hero-actions"><a class="btn btn-primary" href="{pg.u('contact/')}">Discuss your needs {ARROW}</a></div>
</div></section>
<section class="section"><div class="wrap"><div class="belief"><div><span class="eyebrow">Overview</span><h2>Why the people lens matters here.</h2></div><div class="prose">{para(p['intro'])}</div></div></div></section>
<section class="section section-alt"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Focus areas</span><h2>What we focus on.</h2></div><p></p></div><div class="grid g3">{themes}</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Services</span><h2>{e(p['name'])} services.</h2></div><p>Engage any service on its own, or combine them into an integrated program.</p></div>
<div class="grid g3">{''.join(service_card(pg, s, False) for s in svcs)}</div></div></section>
<section class="section-tight section-white"><div class="wrap"><h4>Other practices</h4><ul class="chips">{others}</ul></div></section>
{cta_band(pg)}"""
    ld = [crumbs_ld(trail), {"@context": "https://schema.org", "@type": "Service", "name": p["name"], "serviceType": p["name"],
                             "description": p["meta_description"], "provider": {"@id": SITE + "/#org"}, "url": SITE + "/" + pg.path}]
    write(pg, layout(pg, title=p["meta_title"], description=p["meta_description"], body=body, active="services", ld=ld, img=IMG_PRACTICE.get(slug)), "0.9")


def build_service(slug, s):
    pg = Page(f"services/{slug}/")
    p = PRACTICES.get(s["practice"], {"name": "", "slug": s["practice"]})
    steps = "".join(
        f'<li><div class="phase"><b>0{i}</b>{e(a["phase"])}</div><div><h3>{e(a["title"])}</h3><p>{e(a["body"])}</p></div></li>'
        for i, a in enumerate(s["approach"], 1))
    deliv = "".join(f"<div>{e(d)}</div>" for d in s["deliverables"])
    outs = "".join(f"<div>{e(o)}</div>" for o in s["outcomes"])
    rel_s = pick(SERVICES, s.get("related_services", []))[:3]
    rel_i = pick(INDUSTRIES, s.get("related_industries", []))
    rel_a = pick(INSIGHTS, s.get("related_insights", []))
    ind_chips = "".join(f'<li><a href="{pg.u("industries/" + i["slug"] + "/")}">{e(i["name"])}</a></li>' for i in rel_i)
    toc = [("challenge", "The challenge"), ("approach", "Our approach"), ("deliverables", "What you receive"),
           ("outcomes", "Outcomes"), ("who", "Who we serve"), ("impact", "Impact lens"), ("faq", "FAQ")]
    trail = [("Home", ""), ("Services", "services/"), (p["name"], f"practices/{s['practice']}/"), (s["name"], pg.path)]
    insights_block = ""
    if rel_a:
        insights_block = f'<section class="section section-alt"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Further reading</span><h2>Related insights.</h2></div><p></p></div><div class="grid g3">{"".join(insight_card(pg, a) for a in rel_a)}</div></div></section>'
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">{e(p['name'])}</span><h1>{e(s['name'])}</h1><p class="lede">{e(s['lede'])}</p>
<div class="hero-actions"><a class="btn btn-primary" href="{pg.u('contact/')}">Discuss {e(s['name'].lower())} {ARROW}</a><a class="btn btn-ghost" href="#approach">See our approach</a></div>
</div></section>
<section class="section"><div class="wrap layout">
{toc_html(pg, toc)}
<div class="prose">
  <section id="challenge"><span class="eyebrow">The challenge</span><h2>The problem behind the problem.</h2>{para(s['challenge'])}</section>
  <section id="approach"><span class="eyebrow">Our approach</span><h2>How we deliver {e(s['name'].lower())}.</h2><ol class="steps">{steps}</ol></section>
  <section id="deliverables"><span class="eyebrow">What you receive</span><h2>Deliverables.</h2><div class="deliverables">{deliv}</div></section>
  <section id="outcomes"><span class="eyebrow">Outcomes</span><h2>What changes.</h2><div class="outcomes">{outs}</div></section>
  <section id="who"><span class="eyebrow">Who we serve</span><h2>Who engages us.</h2><p>{e(s['who_we_serve'])}</p>
    {f'<h4 style="margin-top:28px">Industries</h4><ul class="chips">{ind_chips}</ul>' if ind_chips else ''}</section>
  <section id="impact"><div class="callout"><span class="eyebrow">Impact lens</span><h3>Beyond the balance sheet.</h3><p>{e(s['impact_lens'])}</p></div></section>
  <section id="faq"><span class="eyebrow">FAQ</span><h2>Frequently asked questions.</h2>{faq_html(s['faqs'])}</section>
</div></div></section>
<section class="section section-white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Related services</span><h2>Often paired with.</h2></div><p></p></div>
<div class="grid g3">{''.join(service_card(pg, r) for r in rel_s)}</div></div></section>
{insights_block}
{cta_band(pg, title=f"Ready to talk about {s['name'].lower()}?")}"""
    ld = [crumbs_ld(trail), faq_ld(s["faqs"]),
          {"@context": "https://schema.org", "@type": "Service", "name": s["name"], "serviceType": s.get("primary_keyword", s["name"]),
           "description": s["meta_description"], "provider": {"@id": SITE + "/#org", "@type": "ProfessionalService", "name": BRAND, "url": SITE + "/"},
           "areaServed": "Worldwide", "url": SITE + "/" + pg.path}]
    write(pg, layout(pg, title=s["meta_title"], description=s["meta_description"], body=body, active="services", ld=ld, img=IMG_PRACTICE.get(s["practice"])), "0.8")


def build_industries():
    pg = Page("industries/")
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, [("Home", ""), ("Industries", "industries/")])}
<span class="eyebrow">Industries</span><h1>Sector fluency, one science of behavior.</h1>
<p class="lede">A health club member, a car owner, a homebuyer, a patient and a portfolio company CEO behave in different contexts. We bring sector context to each and the same behavioral science to all.</p></div></section>
<section class="section"><div class="wrap"><div class="grid g3">{''.join(industry_card(pg, i) for i in INDUSTRIES.values())}</div></div></section>{cta_band(pg)}"""
    write(pg, layout(pg, title="Industries We Serve", active="industries",
                     description="Datalidy brings behavioral science to private equity, startups, healthcare, digital health, fitness, automotive, mortgage, education, associations and more.",
                     body=body, ld=[crumbs_ld([("Home", ""), ("Industries", "industries/")])], img=IMG_PAGE["industries"]), "0.9")

    for slug, i in INDUSTRIES.items():
        pg = Page(f"industries/{slug}/")
        trail = [("Home", ""), ("Industries", "industries/"), (i["name"], pg.path)]
        ch = "".join(f'<div class="card"><div class="card-num">0{n}</div><h3>{e(c["title"])}</h3><p>{e(c["body"])}</p></div>'
                     for n, c in enumerate(i["challenges"], 1))
        helps = []
        for h in i["how_we_help"]:
            link = f'<a class="link-arrow" href="{pg.u("services/" + h["service"] + "/")}">{e(SERVICES[h["service"]]["name"])}</a>' if h.get("service") in SERVICES else ""
            helps.append(f'<li><div class="phase"><b>→</b></div><div><h3>{e(h["title"])}</h3><p>{e(h["body"])}</p><p style="margin-top:10px">{link}</p></div></li>')
        rel_s = pick(SERVICES, i.get("related_services", []))[:6]
        rel_a = pick(INSIGHTS, i.get("related_insights", []))
        toc = [("context", "Context"), ("challenges", "Challenges"), ("help", "How we help"), ("impact", "Impact lens"), ("faq", "FAQ")]
        body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">Industry</span><h1>{e(i['name'])}</h1><p class="lede">{e(i['lede'])}</p>
<div class="hero-actions"><a class="btn btn-primary" href="{pg.u('contact/')}">Talk to our team {ARROW}</a></div></div></section>
<section class="section"><div class="wrap layout">
{toc_html(pg, toc)}
<div class="prose">
  <section id="context"><span class="eyebrow">Context</span><h2>The people side of {e(i['name'].lower())}.</h2>{para(i['context'])}</section>
  <section id="challenges"><span class="eyebrow">Challenges</span><h2>What leaders are up against.</h2><div class="grid g2">{ch}</div></section>
  <section id="help"><span class="eyebrow">How we help</span><h2>Where we focus.</h2><ol class="steps">{''.join(helps)}</ol></section>
  <section id="impact"><div class="callout"><span class="eyebrow">Impact lens</span><h3>The social good at stake.</h3><p>{e(i['impact_lens'])}</p></div></section>
  <section id="faq"><span class="eyebrow">FAQ</span><h2>Frequently asked questions.</h2>{faq_html(i['faqs'])}</section>
</div></div></section>
<section class="section section-white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Services</span><h2>Relevant services.</h2></div><p></p></div>
<div class="grid g3">{''.join(service_card(pg, r) for r in rel_s)}</div></div></section>
{f'<section class="section section-alt"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Insights</span><h2>Further reading.</h2></div><p></p></div><div class="grid g3">{"".join(insight_card(pg, a) for a in rel_a)}</div></div></section>' if rel_a else ''}
{cta_band(pg)}"""
        write(pg, layout(pg, title=i["meta_title"], description=i["meta_description"], body=body, active="industries",
                         ld=[crumbs_ld(trail), faq_ld(i["faqs"])], img=IMG_INDUSTRY.get(slug)), "0.8")


def build_insights():
    pg = Page("insights/")
    topics = sorted({a["topic"] for a in INSIGHTS.values()})
    chips = '<li><button data-filter="all" aria-pressed="true">All</button></li>' + "".join(
        f'<li><button data-filter="{e(t)}" aria-pressed="false">{e(t)}</button></li>' for t in topics)
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, [("Home", ""), ("Insights", "insights/")])}
<span class="eyebrow">Insights</span><h1>Ideas on behavior, measurement and leadership.</h1>
<p class="lede">Explainers and points of view on the ideas we use every day: behavioral signals, predictive KPIs, behavioral design, coaching, health behavior and the ethics of persuasion.</p></div></section>
<section class="section-tight section-white"><div class="wrap"><ul class="chips">{chips}</ul></div></section>
<section class="section"><div class="wrap"><div class="grid g3">{''.join(insight_card(pg, a) for a in INSIGHTS.values())}</div></div></section>{cta_band(pg)}"""
    write(pg, layout(pg, title="Insights on People, Design & Impact", active="insights",
                     description="Insights from Datalidy on behavioral science, predictive KPIs, behavioral design, executive coaching, health behavior change and ethical persuasive technology.",
                     body=body, ld=[crumbs_ld([("Home", ""), ("Insights", "insights/")])], img=IMG_PAGE["insights"]), "0.9")

    for slug, a in INSIGHTS.items():
        pg = Page(f"insights/{slug}/")
        trail = [("Home", ""), ("Insights", "insights/"), (a["title"], pg.path)]
        secs, toc = [], []
        for n, sec in enumerate(a["sections"], 1):
            sid = f"s{n}"
            toc.append((sid, sec["heading"]))
            bullets = "".join(f"<li>{e(b)}</li>" for b in sec.get("bullets") or [])
            secs.append(f'<section id="{sid}"><h2>{e(sec["heading"])}</h2>{para(sec["paragraphs"])}{f"<ul class=bullets>{bullets}</ul>" if bullets else ""}</section>')
        toc.append(("faq", "FAQ"))
        takeaways = "".join(f"<li>{e(t)}</li>" for t in a["key_takeaways"])
        rel_s = pick(SERVICES, a.get("related_services", []))[:3]
        rel_a = pick(INSIGHTS, a.get("related_insights", []))
        body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">{e(a['topic'])} · Insight</span><h1>{e(a['title'])}</h1><p class="lede">{e(a['dek'])}</p></div></section>
<section class="section"><div class="wrap layout">
{toc_html(pg, toc)}
<article class="prose">
  <div class="takeaways"><h2>Key takeaways</h2><ul>{takeaways}</ul></div>
  {''.join(secs)}
  <section id="faq"><h2>Frequently asked questions</h2>{faq_html(a['faqs'])}</section>
</article></div></section>
<section class="section section-white"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Put it to work</span><h2>Related services.</h2></div><p></p></div>
<div class="grid g3">{''.join(service_card(pg, r) for r in rel_s)}</div></div></section>
{f'<section class="section section-alt"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Keep reading</span><h2>More insights.</h2></div><p></p></div><div class="grid g3">{"".join(insight_card(pg, r) for r in rel_a)}</div></div></section>' if rel_a else ''}
{cta_band(pg)}"""
        art = {"@context": "https://schema.org", "@type": "Article", "headline": a["title"], "description": a["meta_description"],
               "author": {"@type": "Organization", "name": BRAND, "url": SITE + "/"},
               "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": SITE + "/assets/logo.png"}},
               "mainEntityOfPage": SITE + "/" + pg.path, "image": SITE + "/assets/og.png", "datePublished": TODAY, "dateModified": TODAY}
        write(pg, layout(pg, title=a["meta_title"], description=a["meta_description"], body=body, active="insights", og_type="article",
                         ld=[crumbs_ld(trail), art, faq_ld(a["faqs"])], img=IMG_INSIGHT[slug]), "0.7")


def build_approach():
    pg = Page("approach/")
    detail = {
        "Observe": ("We start with what people actually do.",
                    "Before we form a view, we watch and listen: to executives and frontline teams, to customers, users, patients and members. Interviews, contextual inquiry, think-aloud usability sessions and journey mapping reveal the gap between what people say and what they do, which is where most strategies quietly fail.",
                    ["Stakeholder, customer and user interviews", "Contextual inquiry and field observation", "Usability testing and think-aloud protocols", "Journey and process mapping"]),
        "Signal": ("We find the behaviors that predict the outcome.",
                   "Using our Behavioral Signals Design approach, we analyze operating, customer and people data, often scattered across unintegrated systems, to isolate the few conversion moments and behavioral types that drive results. We surface the untested assumptions filling the gaps and turn them into hypotheses.",
                   ["Behavioral data analysis and integration", "Conversion points and behavioral typologies", "Predictive, behavior-based KPIs", "Hypotheses ready for testing"]),
        "Design": ("We make the right behavior easier.",
                   "Drawing on behavioral design, persuasive technology, experience and service design, and coaching, we redesign the environment around a behavior: the prompts, the friction, the motivation and the support. We design with the people affected, and we design ethically.",
                   ["Behavioral and experience design", "Service blueprints and journey redesign", "Messaging and choice architecture", "Leader and team coaching plans"]),
        "Test": ("We replace assumptions with evidence.",
                 "Every design is a hypothesis until it is tested. We run A/B tests, pilots and controlled comparisons with clear success measures and guardrails, so leaders can invest with confidence and stop what does not work early.",
                 ["Experiment and pilot design", "A/B and multivariate testing", "Measurement plans and guardrail metrics", "Readouts with clear decisions"]),
        "Scale": ("We make the gains durable.",
                  "Lasting change needs ownership. We scale what works through implementation support, executive and team coaching, dashboards and predictive KPIs, and we transfer methods to your team so progress continues and compounds after our engagement ends.",
                  ["Implementation roadmaps", "Executive and team coaching", "Decision dashboards and KPI governance", "Training and knowledge transfer"]),
    }
    secs = []
    for n, ph in enumerate(PHASES, 1):
        h, txt, items = detail[ph]
        lis = "".join(f"<li>{e(x)}</li>" for x in items)
        secs.append(f'<section id="{ph.lower()}"><span class="eyebrow">0{n} · {ph}</span><h2>{e(h)}</h2><p>{e(txt)}</p><ul class="bullets">{lis}</ul></section>')
    principles = [
        ("Behavior is the unit of analysis", "Strategy, culture and experience become manageable when they are expressed as specific, observable behaviors."),
        ("Hypotheses, then tests", "We treat every recommendation as a hypothesis and every assumption as something to test, not defend."),
        ("Ethical persuasion only", "We help people do what they already want to do. We do not design manipulation, dark patterns or coercion."),
        ("Responsible with data", "People and customer data is personal. We apply privacy, consent and ethical review to every analysis."),
        ("Build capability, not dependency", "We transfer methods, tools and habits so your team can continue the work without us."),
        ("Candor over comfort", "We tell clients and investors what the evidence shows, especially when it is uncomfortable."),
    ]
    pcards = "".join(f'<div class="card"><h3>{e(t)}</h3><p>{e(b)}</p></div>' for t, b in principles)
    trail = [("Home", ""), ("Approach", "approach/")]
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">Our approach</span><h1>Observe. Signal. Design. Test. Scale.</h1>
<p class="lede">One disciplined method sits under every {BRAND} engagement, from a two-week diligence sprint to a multi-year transformation. It joins behavioral science, data analysis, human-centered design and coaching, and it always ends in measurable outcomes.</p></div></section>
<section class="section"><div class="wrap layout">
{toc_html(pg, [(p.lower(), p) for p in PHASES])}
<div class="prose">{''.join(secs)}</div></div></section>
<section class="section section-alt"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Principles</span><h2>How we hold ourselves accountable.</h2></div><p></p></div><div class="grid g3">{pcards}</div></div></section>
{cta_band(pg)}"""
    write(pg, layout(pg, title="Our Consulting Approach", active="approach",
                     description="Datalidy's five-phase method, Observe, Signal, Design, Test, Scale, joins behavioral science, data analysis, design and coaching for measurable outcomes.",
                     body=body, ld=[crumbs_ld(trail)], img=IMG_PAGE["approach"]), "0.8")


def build_about():
    pg = Page("about/")
    trail = [("Home", ""), ("About", "about/")]
    who = [
        ("Investors", "Private equity sponsors, venture investors, family offices and impact funds who want to see customer and leadership behavior before and after they invest."),
        ("Founders and executives", "CEOs, founders and leadership teams of fast-growing, knowledge-based businesses and established enterprises."),
        ("Health and mission-driven institutions", "Health systems, medical and public health associations, schools, universities and nonprofits serving the public good."),
        ("Product, growth and experience leaders", "Teams responsible for conversion, adoption, retention and the experience customers, patients and members actually have."),
    ]
    wc = "".join(f'<div class="card"><h3>{e(t)}</h3><p>{e(b)}</p></div>' for t, b in who)
    disciplines = ["Behavioral science and behavioral design", "Clinical and health psychology", "Behavioral medicine",
                   "Human-computer interaction and usability", "Persuasive technology", "Research methods and psychometrics",
                   "Data analysis and visualization", "Executive and team coaching", "Product development and operations"]
    disc = "".join(f"<li>{e(d)}</li>" for d in disciplines)
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">About {BRAND}</span><h1>We make human behavior measurable, predictable and improvable.</h1>
<p class="lede">{BRAND} is a behavioral science and data advisory firm. We help investors, leaders and mission-driven institutions solve the people problems that decide performance, inside the business and beyond it, and we hold that work to the standard of the public good.</p></div></section>
<section class="section"><div class="wrap"><div class="belief">
<div><span class="eyebrow">Our story</span><h2>Applied behavioral science, built for decisions.</h2></div>
<div class="prose">
<p>{BRAND} works at the intersection of psychology, health, technology and business. Our practice brings together behavioral science, research methods, design and coaching, applied to the questions investors, executives and mission-driven leaders actually face.</p>
<p>Along the way we learned something simple. Organizations are drowning in data and starving for signal. The behaviors that actually predict conversion, adoption, adherence, engagement and leadership effectiveness are usually hiding in plain sight, buried in systems that were never integrated and covered by assumptions that were never tested.</p>
<p>So we built a way to find them. Our Behavioral Signals Design approach turns noisy data into predictive, behavior-based KPIs and clear experiments. Our coaching practice helps leaders and teams act on what the signals show. And our commitment to social impact keeps the work honest: behavioral science should help people do what they already want to do, never manipulate them.</p>
</div></div></div></section>
<section class="section section-alt"><div class="wrap"><div class="belief">
<div><span class="eyebrow">Our expertise</span><h2>The disciplines behind the work.</h2><p class="lede" style="margin-top:16px">Our work combines behavioral science, research rigor, design craft and coaching experience.</p></div>
<div class="prose"><ul class="bullets">{disc}</ul></div></div></div></section>
<section class="section section-dark"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Our values</span><h2>What we stand for.</h2></div><p></p></div>
<div class="grid g3">
<div class="card"><h3>Validity</h3><p>We are honest about what the data can and cannot tell us, and we never let a convenient story outrun the evidence.</p></div>
<div class="card"><h3>Dignity</h3><p>Every person in a system deserves to be understood and respected, from the boardroom to the front line to the patient, student or customer.</p></div>
<div class="card"><h3>Shared value</h3><p>We look for solutions where returns and the public good reinforce each other, and we say so plainly when they do not.</p></div>
</div></div></section>
<section class="section"><div class="wrap"><div class="section-head"><div><span class="eyebrow">Who we serve</span><h2>Our clients.</h2></div><p>We work with people who believe that understanding human behavior is both the right thing to do and the smart thing to do.</p></div>
<div class="grid g4">{wc}</div></div></section>
{cta_band(pg)}"""
    write(pg, layout(pg, title="About Our Firm", active="about",
                     description="Datalidy is a behavioral science and data advisory firm, grounded in psychology, HCI and coaching, serving investors, leaders and the public good.",
                     body=body, ld=[crumbs_ld(trail), ORG_LD], img=IMG_PAGE["about"]), "0.8")


def build_contact():
    pg = Page("contact/")
    trail = [("Home", ""), ("Contact", "contact/")]
    opts = "".join(f"<option>{e(p['name'])}</option>" for p in PRACTICES.values())
    body = f"""<section class="hero hero-page"><div class="wrap">
{crumbs_html(pg, trail)}
<span class="eyebrow">Contact</span><h1>Start a conversation.</h1>
<p class="lede">Tell us about the people problem in front of you. A senior member of our team will respond to discuss whether and how we can help.</p></div></section>
<section class="section"><div class="wrap"><div class="belief">
<div><h2>How we begin.</h2>
<div class="prose"><p>Every engagement starts with a candid, no-obligation conversation. We will ask about your objectives, the people involved and what you already know, then outline how we would approach it.</p>
<ul class="bullets"><li>An initial call to understand your situation</li><li>A short written proposal with scope, team and timeline</li><li>A clear plan for measuring what changes</li></ul>
<p>Prefer email? Write to us directly at <a href="mailto:{EMAIL}">{EMAIL}</a>.</p></div></div>
<form class="form" id="contact-form" data-to="{EMAIL}">
  <div class="row"><label>Name<input name="name" required autocomplete="name"></label><label>Email<input type="email" name="email" required autocomplete="email"></label></div>
  <div class="row"><label>Organization<input name="organization" autocomplete="organization"></label><label>Role<input name="role" autocomplete="organization-title"></label></div>
  <label>Area of interest<select name="interest"><option>General inquiry</option>{opts}</select></label>
  <label>How can we help?<textarea name="message" required></textarea></label>
  <div><button class="btn btn-dark" type="submit">Send inquiry {ARROW}</button></div>
</form></div></div></section>"""
    write(pg, layout(pg, title="Contact Us", description="Contact Datalidy to discuss Behavioral Signals Design, private equity and venture advisory, executive coaching, behavioral design or social impact work.",
                     body=body, ld=[crumbs_ld(trail)], img=IMG_PAGE["contact"]), "0.8")


def build_privacy():
    pg = Page("privacy/")
    body = f"""<section class="hero hero-page"><div class="wrap">{crumbs_html(pg, [("Home", ""), ("Privacy", "privacy/")])}<h1>Privacy notice</h1><p class="lede">Last updated {date.today().strftime('%B %-d, %Y')}.</p></div></section>
<section class="section"><div class="wrap narrow prose">
<p>This website is informational. It does not use advertising cookies or third-party tracking, and it does not require you to create an account.</p>
<h2>Information you send us</h2><p>If you contact us by email or through the contact form, which opens your own email application, we receive the information you choose to include. We use it only to respond to your inquiry and to manage any resulting relationship, and we do not sell it.</p>
<h2>Technical information</h2><p>Our hosting and content delivery providers may process standard technical data, such as IP addresses and request logs, to deliver and secure the site. Fonts are served by Google Fonts.</p>
<h2>Client data</h2><p>Data we handle in the course of client engagements, including people data, is governed by the agreement with each client and by our data ethics practices, including data minimization, de-identification where possible and strict access controls.</p>
<h2>Contact</h2><p>Questions about privacy may be sent to <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
</div></section>"""
    write(pg, layout(pg, title="Privacy Notice", description="How Datalidy handles information shared through this website and in the course of client engagements.", body=body), "0.3")


def build_404():
    pg = Page("")
    body = f"""<section class="hero hero-page"><div class="wrap"><span class="eyebrow">404</span><h1>We couldn’t find that page.</h1>
<p class="lede">The page may have moved. Try one of these instead.</p>
<div class="hero-actions"><a class="btn btn-primary" href="/">Home {ARROW}</a><a class="btn btn-ghost" href="/services/">Services</a><a class="btn btn-ghost" href="/insights/">Insights</a></div></div></section>"""
    page = layout(pg, title="Page not found", description="Page not found.", body=body)
    # Served at arbitrary depths, so resolve every relative link from the site root.
    page = page.replace("<head>", f'<head>\n<base href="{SITE}/">', 1).replace('content="index, follow, max-image-preview:large"', 'content="noindex"')
    (OUT / "404.html").write_text(page)


def build_meta_files():
    urls = "".join(f"<url><loc>{SITE}/{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for p, pr in PAGES)
    (OUT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (OUT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    (OUT / ".nojekyll").write_text("")
    (OUT / "favicon.svg").write_text(LOGO.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"').replace("<rect ", '<rect fill="#0a1626" ', 1).replace('fill="none" stroke="#d6b47e"', 'stroke="#d6b47e"', 1))


def check_links():
    """Fail the build if any relative internal link points at a page that doesn't exist."""
    import re
    bad = []
    for f in OUT.rglob("*.html"):
        if f.name == "404.html":
            continue
        for href in re.findall(r'href="([^"#:]+)"', f.read_text()):
            if href.startswith(("//", "/")):
                continue
            target = (f.parent / href).resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                bad.append((str(f.relative_to(OUT)), href))
    if bad:
        for b in bad[:30]:
            print("BROKEN", *b)
        raise SystemExit(f"{len(bad)} broken links")


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(ROOT / "static", OUT)
    ORG_LD["knowsAbout"] = [s["name"] for s in SERVICES.values()]
    build_home()
    build_services_hub()
    for slug, p in PRACTICES.items():
        build_practice(slug, p)
    for slug, s in SERVICES.items():
        build_service(slug, s)
    build_industries()
    build_insights()
    build_approach()
    build_about()
    build_contact()
    build_privacy()
    build_404()
    build_meta_files()
    check_links()
    print(f"Built {len(PAGES)} pages -> {OUT}")


if __name__ == "__main__":
    main()
