---
layout: default
title: "Regions"
description: "Discover regional momo varieties"
---

## Regions

<ul class="collection-list">
  {% for r in site.regions %}
    <li>
      <a href="{{ r.url | relative_url }}">{{ r.title }}</a>
    </li>
  {% endfor %}
</ul>
