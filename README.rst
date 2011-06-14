Django ESI
=============
Django application for handling `edge side include (ESI)`_

When to use
-------------

Use this tag when you need to render a single object and would like to take
advantage of `Varnish`_'s caching to speed up the rendering of the page.


Hows and Whys
-------------

ESI allows you to specify sections of the site that require different caching
strategies and can be sent to a smart caching layer for rendering.

For example, your site have duplicate content you are using frequently through
your site and you would like to make these items easier to render in templates,
leveraging `Varnish`_ to cache these pieces of your site, possibly even at different
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

This will produce something like this::

    <html>
        <body>
            <esi:include src="/esi/list/tags/tag/4/900/includes/lists/" /> 
            <esi:include src="/esi/list/tags/tag/5/900/includes/lists/" /> 
            <esi:include src="/esi/list/tags/tag/6/900/includes/lists/" /> 
            <esi:include src="/esi/blog/entries/4/1200/blog/entry_detail.html/" /> 
        </body>
    </html>



Loading without ESI
"""""""""""""""""""

The template tag reads the ``DEBUG`` settings value [#]_ and if set to ``True``
renders the view with the current request rather than including the
``<esi:include>`` tag.


Installation
------------

This software is still in beta. It may or may not perform as expected in production!

Recommending installation is through `pip`_::

    prompt> pip install -e git://github.com/mrfunyon/django-esi.git#egg=django-esi

Once installed, you must add the app to your ``INSTALLED_APPS`` inside your
settings::

    'esi',

add the url to your urls file::

    (r'^esi/', include('esi.urls')),


.. _edge side include (ESI): http://en.wikipedia.org/wiki/Edge_Side_Includes
.. _Wikipedia article: http://en.wikipedia.org/wiki/Edge_Side_Includes 
.. _pip: http://pip.openplans.org
.. _Varnish: http://www.varnish-cache.org/
.. _Issue Tracker: https://github.com/mrfunyon/django-esi/issues

.. rubric:: Footnotes
.. [#] http://docs.djangoproject.com/en/1.2/ref/settings/#debug