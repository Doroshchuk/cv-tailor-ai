---
layout: home
title: CV Tailor AI Blog
---

Welcome to my blog documenting the development of my resume tailoring tool using Python, Playwright, and AI!

---

## Posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a> — {{ post.date | date: "%B %d, %Y" }}
    </li>
  {% endfor %}
</ul>