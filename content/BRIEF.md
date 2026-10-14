# Datalidy content brief

## The firm
Datalidy (website: datalidy.com) is a data-driven, social-impact-oriented advising and consulting firm. Its services range from private equity advising to leadership and management consulting. Everything it does centers on the **people problems of a business**: it solves people problems inside the business (leadership, culture, talent, organization, employee experience) and outside it (customers, communities, stakeholders) using evidence, analytics, service design, experience design and human-centered design. The firm's belief is that serving people well inside an organization is how a business better serves its customers, its communities and the social good it exists for, and that this also drives durable financial performance.

Positioning line options: "Data-driven advisory for the people side of business." / "Where evidence meets empathy."

Methodology (use these names consistently when referencing the approach): **Listen → Measure → Design → Deliver → Sustain**.
- Listen: qualitative research, interviews, ethnography, community listening.
- Measure: people analytics, baselines, quantitative diagnostics.
- Design: service design, experience design, co-design with the people affected.
- Deliver: implementation, change management, capability building.
- Sustain: dashboards, governance, impact measurement, handover.

## Voice
Formal, confident, precise, warm but not casual. Like a top-tier strategy firm writing for executives, boards, investors, foundation leaders and public officials. Concrete and specific, no filler, no hype words ("revolutionary", "synergy", "cutting-edge", "unlock", "leverage" as a verb, "in today's fast-paced world", "delve"). American English. Use plain verbs. Don't use em dashes; use commas, colons, or periods instead.

## Hard rules
- NO invented statistics, percentages, dollar figures, client names, case studies, testimonials, awards, team member names, years in business, or office locations. Do not cite specific studies by name with numbers. You may describe well-established concepts (e.g., "research on psychological safety", "Amy Edmondson's work") qualitatively.
- No promises of guaranteed results.
- Every page must be genuinely useful and distinct, written for search intent (someone searching e.g. "service design consulting" or "human capital due diligence"). Naturally include the primary keyword in the lede and a few times in body. No keyword stuffing.
- Plain text only in strings (no Markdown, no HTML). Paragraph arrays are arrays of plain strings.
- meta_title: max 60 characters, should NOT include "Datalidy" (the site appends " | Datalidy").
- meta_description: 140–160 characters.
- Output must be valid JSON (UTF-8, straight quotes inside strings escaped). Validate with `python3 -c "import json;json.load(open('FILE'))"` before finishing.
- Only use slugs from content/taxonomy.json in `related_*` fields.
