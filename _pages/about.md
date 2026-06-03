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
- **Aug. 01, 2024**, I joined Vrije Universiteit Amsterdam as an asssistant professor with [Social AI Group](https://socialai.nl/).
- **Apr. 03, 2023**, I joined [CWI](https://www.dis.cwi.nl/people/) as a researcher.
- **Dec. 01, 2021**, I joined Amazon as an applied scientist.


News
======
{% for update in site.data.updates %}
- **{{ update.date }}** — {% if update.url and update.url != '' %}<a href="{{ update.url }}" target="_blank">{{ update.text }}</a>{% else %}{{ update.text }}{% endif %}
{% endfor %}

