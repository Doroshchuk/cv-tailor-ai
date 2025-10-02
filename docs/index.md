---
layout: home
title: CV Tailor AI Blog
---

Welcome to my blog documenting the development of **CV Tailor AI** — a resume tailoring tool built with **Python, Playwright, and AI**.  
This project combines automation, scraping, and AI prompt engineering to streamline the job application process and maximize resume–job match rates.

Alongside CV Tailor AI, I’ve been actively upskilling in:
- **Computer Science fundamentals** (AlgoExpert crash courses, algorithm practice)
- **Automation frameworks** (Python + Playwright for UI/API testing)
- **Practical AI integration**

🚀 **Note:** To keep updates clear and focused, all **SDET upskilling progress** (AlgoExpert practice, test framework design, SQL drills) has been moved to a dedicated repo:  
👉 [SDET Framework Lab](https://github.com/Doroshchuk/sdet-framework-lab)

---

## Posts

<ul>
  {% for post in site.posts %}
    <li>
      <a href="{{ site.baseurl }}{{ post.url }}">{{ post.title }}</a> — {{ post.date | date: "%B %d, %Y" }}
    </li>
  {% endfor %}
</ul>