---
title: Blog 
layout: template
---

Blog
-----------------------------------------------------------------------

{% for post in site.posts limit: 25 %}
<p>
    <h4>{{ post.title }}<span class="floatright">{{ post.date | date_to_long_string }}</span></h4>
    <p>
      {{ post.content | markdownify  |	truncatewords: 50 }}
    </p>
    <a href="{{ post.url }}">Read More</a>
    <hr>
</p>
{% endfor %}

{% if site.posts.size > 25 %}
	<ul>
	{% for post in site.posts offset:25 %}
		<li><a href="{{post.url}}">{{post.title}}</a></li>
	{% endfor %}
	</ul>
{% endif %}




