from django import template

import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from .. import views as esi_views

register = template.Library()

class EsiNode(template.Node):
    def __init__(self, object=None, template_name=None, template_path=None, timeout=None):
        self.object = template.Variable(object)
        if template_name:
            self.url_name = 'esi'
            self.template = template_name
        if template_path:
            self.url_name = 'esi_list'
            self.template = template_path
        if timeout:
            self.timeout = timeout or settings.CACHE_MIDDLEWARE_SECONDS
    def render(self,context):
        try:
            object = self.object.resolve(context)
        except template.VariableDoesNotExist:
            return ''
        timeout = int(self.timeout)
        template = self.template.replace("'",'').rstrip("/")
        kwargs = {
            'app_label': object._meta.app_label,
            'model_name': object._meta.module_name,
            'object_id': object.pk,
            'timeout': timeout,
        }
        if 'list' in self.url_name:
            kwargs['template_dir'] = template
        else:
            kwargs['template_name'] = template
        if not settings.DEBUG:
            return '<esi:include src="%s" />' % reverse(self.url_name, kwargs=kwargs)
        else:
            # call the ESI view
            return esi_views.esi(context['request'], **kwargs)

def do_create_esi(parser, token):
    """
    Retrieves the content for a specified category for a given date, given either by a template variable or
    the slug-path of a category.
    
    Syntax::
    
        {% create_esi for [object] [[template <template_name>] or [path <template_path>]] [timeout <time_in_seconds>]%}
        
    For example::
    
        {% create_esi for object template 'news/story_detail.html' timeout 900 %}
        
        {% create_esi for object path 'includes/lists/' timeout 1200 %}
        
    [object]  and [[template template_name] or [path template_path]] are required, timeout is optional.
    """
    
    try:
        # split_contents() knows not to split quoted strings.
        args = token.split_contents()
        tag_name = args[0]
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires a single argument" % token.contents.split()[0])
    if args[1] != 'for':
        raise template.TemplateSyntaxError("%r tag must start with 'for'" % tag_name)
    kwargs = {
        'object': args[2],
    }
    for arg in args:
        if arg == 'path':
            kwargs.update({'template_path':args[args.index(arg)+1]})
        if arg == 'template':
            kwargs.update({'template_name':args[args.index(arg)+1]})
        if arg == 'timeout':
            kwargs.update({'timeout':args[args.index(arg)+1]})
        
    print kwargs
    return EsiNode(**kwargs)

register.tag('esi', do_create_esi)
