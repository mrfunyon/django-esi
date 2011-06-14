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
            'template': template
        }
        if not settings.DEBUG:
            return '<esi:include src="%s" />' % reverse('esi', kwargs=kwargs)
        else:
            # call the ESI view
            print context
            return esi_views.esi(context['request'], **kwargs).content

def do_create_esi(parser, token):
    """
    Creates an esi out of an object.
    
    Syntax::
    
        {% create_esi for [object] [[template <template_name>] or [path <template_path>]] [timeout <time_in_seconds>]%}
        
    For example::
    
        {% create_esi for object template 'news/story_detail.html' timeout 900 %}
        
        {% create_esi for object path 'includes/lists' timeout 1200 %}
        
    [object]  and [[template template_name] or [path template_path]] are required, timeout is optional.
    """
    
        # split_contents() knows not to split quoted strings.
    args = token.split_contents()
    tag_name = args[0]
    if len(args) < 4:
        raise template.TemplateSyntaxError("%r tag requires a at least 4 arguments" % token.contents.split()[0])
    if args[1] != 'for':
        raise template.TemplateSyntaxError("%r tag must start with 'for'" % tag_name)
    if args[3] not in ['template', 'path']:
        raise template.TemplateSyntaxError("3rd argument of %r tag must start be 'template' or 'path'" % tag_name)
    kwargs = {
        'object': args[2],
    }
    for arg in args:
        try:
            if arg == 'path':
                kwargs.update({'template_path':args[args.index(arg)+1]})
            if arg == 'template':
                kwargs.update({'template_name':args[args.index(arg)+1]})
            if arg == 'timeout':
                kwargs.update({'timeout':args[args.index(arg)+1]})
        except IndexError:
            raise template.TemplateSyntaxError("%r in tag '%s' requires an arguement." % (arg, tag_name))
        
    return EsiNode(**kwargs)

register.tag('esi', do_create_esi)
