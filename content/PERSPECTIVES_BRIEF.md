# Perspectives brief: news analysis articles

Read content/BRIEF.md first for the firm's positioning, voice and rules. This brief adds rules for **Perspectives**: objective analysis of real, major news events through Datalidy's lens (behavior, people problems inside and outside organizations, leadership, measurement and predictive signals, investor implications, and the public good).

## Story selection
- Each month gets exactly 2 stories. Pick **major, widely reported** events whose core lesson is about people and behavior: operational failures and outages, safety incidents, leadership crises and successions, layoffs and restructurings, strikes and labor relations, product launches or adoption failures, public health, AI adoption and governance, data breaches caused by human factors, culture and conduct failures, customer backlash, notable acquisitions and integrations, and similar.
- The event must have occurred (or broken) in that calendar month. Prefer variety across sectors: technology, health care, aviation and transport, finance and investing, retail and consumer, energy, public sector, education, sports and media.
- Avoid stories whose main frame is partisan politics, war, or mass-casualty violence. Where a story involves deaths or injuries, treat it with restraint and respect, and focus on systems, not blame.

## Accuracy rules (non-negotiable)
- Use web search to research each story. Every factual claim (dates, numbers, quotes, causes, names of organizations and officials) must come from a source you actually found, and be attributed in the text ("according to the FAA", "Reuters reported").
- Cite 2–4 sources per article: prefer primary sources (agency statements, company filings and statements, regulator reports) and major outlets (AP, Reuters, BBC, NYT, WSJ, FT, Bloomberg, NPR, trade press). Only include URLs that appeared in your search results or that you fetched. Never construct or guess a URL.
- Where causes are disputed or investigations are ongoing, say so plainly. Never speculate about individuals' motives or assign blame beyond what authoritative sources state. Name organizations; avoid naming private individuals; public officials and executives may be named only as quoted or reported in sources.
- Numbers are allowed only when attributed to a cited source. No invented statistics.
- Analysis must be objective and fair: no mockery, no hindsight smugness, acknowledge constraints the organization faced.

## Datalidy framing (without self-promotion)
Each article explains: what happened (facts only); the human and behavioral dimension (decisions, incentives, handoffs, culture, communication, customer or public behavior); what signals could have been visible earlier (leading indicators, predictive KPIs); lessons for leaders, boards and investors; and the public-good dimension. Mention Datalidy at most once, near the end, naturally. Never claim Datalidy was involved.

## Output schema
Write a JSON file `{ "perspectives": [ ... ] }` where each item is:
{
  "slug": "kebab-case, unique, descriptive, <= 70 chars, no dates",
  "title": "headline, <= 80 chars, factual and neutral",
  "event_month": "YYYY-MM",
  "meta_title": "<= 60 chars, no 'Datalidy'",
  "meta_description": "140-160 chars",
  "topic": "one of: Behavior, Analytics, Design, Leadership, Health, Strategy",
  "sector": "short label, e.g. Aviation, Technology, Health Care, Finance, Retail, Energy, Public Sector, Education, Media, Transportation, Labor",
  "organizations": ["organizations central to the story"],
  "summary": "card blurb, 20-30 words",
  "dek": "25-45 words",
  "key_takeaways": ["4 items, 12-25 words each"],
  "sections": [   // exactly these 5 headings in this order
    {"heading": "What happened", "paragraphs": ["2-3 paragraphs, 60-120 words each, facts only, attributed"], "bullets": []},
    {"heading": "The human dimension", "paragraphs": ["2 paragraphs"], "bullets": []},
    {"heading": "The signals that mattered", "paragraphs": ["1-2 paragraphs"], "bullets": ["3-5 leading indicators, 6-20 words each"]},
    {"heading": "Lessons for leaders and investors", "paragraphs": ["1-2 paragraphs"], "bullets": ["3-4 items"]},
    {"heading": "The public-good dimension", "paragraphs": ["1 paragraph"], "bullets": []}
  ],
  "sources": [ {"title": "article or document title", "publisher": "outlet or agency", "url": "https://...", "date": "YYYY-MM-DD"} ],
  "related_services": ["2-3 service slugs from content/taxonomy.json"],
  "related_insights": ["1-2 insight slugs from content/taxonomy.json"]
}
Body length 650-950 words per article. Plain text only, American English, no em dashes. Validate JSON with python3 before finishing.
