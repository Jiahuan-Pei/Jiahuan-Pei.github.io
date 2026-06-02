---
permalink: /
title: ""
excerpt: "About me"
author_profile: true
redirect_from: 
  - /about/
  - /about.html
---

About me
======
I am working as an assistant professor with the [Social AI Group](https://socialai.nl/) at Vrije Universiteit Amsterdam, focusing on multimodal agents for conversational AI. 
Formerly, I worked with [DIS Group](https://www.dis.cwi.nl/) at Centrum Wiskunde & Informatica (CWI) and Amazon, focusing on core NLP/IR problems in both industry and academia.
I have pursued my Ph.D. with the [IRLab](https://irlab.science.uva.nl/) at University of Amsterdam, supervised by [Prof. dr. Maarten de Rijke](https://staff.fnwi.uva.nl/m.derijke/) and
[Prof. dr. Pengjie Ren](https://pengjieren.github.io/). 
My interest includes natural language processing (dialogue systems, word embedding,
parsing, summarization) and information retrieval (query understanding, recommender system, matcher
embedding).

Work Experience
======
- **Aug. 01, 2024**, I join Vrije Universiteit Amsterdam as an asssistant professor.
- **Apr. 03, 2023**, I join [CWI](https://www.dis.cwi.nl/people/) on-site as a researcher.
- **Dec. 01, 2021**, I join Amazon as an applied scientist.

Latest LinkedIn Post
======
{% if site.data.linkedin_embed.url and site.data.linkedin_embed.url != '' %}
<iframe src="{{ site.data.linkedin_embed.url }}" height="400" width="100%" frameborder="0" allowfullscreen title="Latest LinkedIn post" style="max-width:504px; display:block;"></iframe>
<p><small><a href="https://www.linkedin.com/in/jiahuan-joanne-pei-b4b507b4/" target="_blank">View LinkedIn profile →</a></small></p>
{% else %}
<p><a href="https://www.linkedin.com/in/jiahuan-joanne-pei-b4b507b4/" target="_blank">View my LinkedIn profile →</a></p>
{% endif %}

News
======
{% for update in site.data.updates %}
- **{{ update.date }}** — {% if update.url and update.url != '' %}<a href="{{ update.url }}" target="_blank">{{ update.text }}</a>{% else %}{{ update.text }}{% endif %}
{% endfor %}

