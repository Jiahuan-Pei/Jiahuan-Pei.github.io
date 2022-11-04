---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---

{% if author.googlescholar %}
  You can also find my articles on <u><a href="{{author.googlescholar}}">my Google Scholar profile</a>.</u>
{% endif %}

{% include base_path %}

<h2>Conference Papers</h2>
{% for post in site.publications reversed %}
  {% include archive-single.html pubsource="proceeding" %}
{% endfor %}

<h2>Journal Articles</h2>
{% for post in site.publications reversed %}
  {% include archive-single.html pubsource="journal" %}
{% endfor %}

<h2>Books</h2>
{% for post in site.publications reversed %}
  {% include archive-single.html pubsource="book" %}
{% endfor %}
