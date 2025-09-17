---
layout: home
title: CV Tailor AI Blog
---

Welcome to my blog documenting the development of my resume tailoring tool using Python, Playwright, and AI!
Alongside this project, I’ve been actively upskilling in relevant technologies and preparing for upcoming technical interviews — with a focus on Computer Science fundamentals, automation, and practical AI integration.

---

## Posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a> — {{ post.date | date: "%B %d, %Y" }}
    </li>
  {% endfor %}
</ul>