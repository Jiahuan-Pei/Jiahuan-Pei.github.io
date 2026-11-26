---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% include base_path %}

{% if author.googlescholar %}
<p>You can also find my articles on <u><a href="{{ author.googlescholar }}" target="_blank">my Google Scholar profile</a></u>.</p>
{% endif %}

{% assign proceedings = site.publications | where: "pubsource", "proceeding" | sort: "date" | reverse %}
{% assign journals    = site.publications | where: "pubsource", "journal"    | sort: "date" | reverse %}
{% assign arxivs      = site.publications | where: "pubsource", "arxiv"      | sort: "date" | reverse %}
{% assign books       = site.publications | where: "pubsource", "book"       | sort: "date" | reverse %}

{% if proceedings.size > 0 %}
## Conference Papers

<ul class="pub-list">
{% for pub in proceedings %}
  <li>{{ pub.citation }}</li>
{% endfor %}
</ul>
{% endif %}

{% if journals.size > 0 %}
## Journal Articles

<ul class="pub-list">
{% for pub in journals %}
  <li>{{ pub.citation }}</li>
{% endfor %}
</ul>
{% endif %}

{% if arxivs.size > 0 %}
## arXiv Preprints

<ul class="pub-list">
{% for pub in arxivs %}
  <li>{{ pub.citation }}</li>
{% endfor %}
</ul>
{% endif %}

{% if books.size > 0 %}
## Theses & Books

<ul class="pub-list">
{% for pub in books %}
  <li>{{ pub.citation }}</li>
{% endfor %}
</ul>
{% endif %}

<style>
.pub-list { list-style: none; padding: 0; margin: 0 0 8px; }
.pub-list li { margin-bottom: 8px; line-height: 1.5; }
.pub-list li .pub-title { font-style: italic; }
</style>
