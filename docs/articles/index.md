---
layout: default
title: "Articles"
description: "All MomoPedia articles"
---

## Articles

<ul class="collection-list">
  {% for article in site.articles %}
    <li class="collection-item">
      <a href="{{ article.url | relative_url }}">{{ article.title }}</a>
      {% if article.date %}<span class="muted"> — {{ article.date | date: "%B %d, %Y" }}</span>{% endif %}
    </li>
  {% endfor %}
</ul>
