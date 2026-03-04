---
layout: default
title: "Chutneys & Achars"
description: "Every great momo deserves a great chutney. Explore our collection of dipping sauces."
---

## Chutneys & Achars

No momo is complete without its partner — the chutney. From smoky tomato-sesame achar to fiery Szechuan chilli oil, these condiments transform a good momo into a great one.

<div class="collection-grid">
{% for recipe in site.recipes %}
  {% if recipe.tags contains 'chutney' %}
  <div class="collection-card">
    <h3><a href="{{ recipe.url | relative_url }}">{{ recipe.title }}</a></h3>
    <p>{{ recipe.description }}</p>
    <div class="recipe-quick-meta">
      {% if recipe.prep_time %}<span>Prep: {{ recipe.prep_time }}</span>{% endif %}
      {% if recipe.cook_time %}<span>Cook: {{ recipe.cook_time }}</span>{% endif %}
    </div>
  </div>
  {% endif %}
{% endfor %}
</div>

### All Recipes

Looking for momo recipes too? Check out our full [Recipes](/MomoPedia/recipes/) page.
