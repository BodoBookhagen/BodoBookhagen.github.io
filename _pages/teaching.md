---
layout: archive
title: "Teaching"
permalink: /teaching/
author_profile: true
---

At the undergraduate level, I am teachin and introductory class to GIS and Remote Sensing.


At the graduate level, I am teaching the following classes:
- Remote Sensing of the Environment [GEW-RCM01]
- Earth System Sciences [GEW-RCM02]
- Terrestrial and Airborne Lidar and Photogrammetry Systems [GEW-RSM02]
- Big Data Analytics [GEW-DAP03]

{% include base_path %}

{% for post in site.teaching reversed %}
  {% include archive-single.html %}
{% endfor %}
