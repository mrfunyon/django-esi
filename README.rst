Django ESI
=============
Django application for handling `edge side include (ESI)`_

When to use
-------------

Use this tag when you need to render a single object and would like to take
advantage of varnish's caching to speed up the rendering of the page.


Hows and Whys
-------------

ESI allows you to specify sections of the site that require different caching
strategies and can be sent to a smart caching layer for rendering.

For example, your site have duplicate content you are using frequently through
your site and you would like to make these items easier to render in templates,
leveraging varnish to cache these pieces of your site, possibly even at different
cache intervals.

Here is an example before::

    <html>
        <body>
            {% for tag in tag_list %}
                {% render_template_for object in 'includes/list' %}
            {% endfor %}
            {% get_latest_blog_entry as blog_entry %}
            {% with blog_entry as object %}
                {% include 'blog/entry_detail.html'}
            {% endwith %}
        </body>
    </html>

To change this to use esi's you would do something like this::

    <html>
        <body>
        {% for tag in tag_list %}
            {% esi for tag list 'includes/lists' timeout 900 %}
        {% endfor %}
        {% get_latest_blog_entry as blog_entry %}
        {% esi for blog_entry template 'blog/entry_detail.html' timeout 1200 %}
        </body>
    </html>


Loading without ESI
"""""""""""""""""""

The template tag reads the ``DEBUG`` settings value  and if set to ``True``
renders the view with the current request rather than including the
``<esi:include>`` tag.