---
layout: default
title: "Recipes"
description: "Momo recipes and cooking guides"
---

## Recipes

<ul class="collection-list">
  {% for r in site.recipes %}
    <li>
      <a href="{{ r.url | relative_url }}">{{ r.title }}</a>
    </li>
  {% endfor %}
</ul>
