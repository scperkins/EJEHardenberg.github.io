---
title: Blog 
layout: template
---

Blog
-----------------------------------------------------------------------

{% for post in site.posts limit: 10 %}
<p>
	<h2>{{ post.title }}</h2>
    <h4>{{ post.date | date_to_long_string }}</h4>
    <p>
      {{ post.content |	truncatewords: 50 }}
    </p>
    <a href="{{ post.url }}">Read More</a>
</p>
{% endfor %}

