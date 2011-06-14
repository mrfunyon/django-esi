# Create your views here.
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.xheaders import populate_xheaders
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from django.db.models import Model, get_model
from django.utils.cache import patch_cache_control

def get_object(app_label, model_name, object_id):
    model = get_model(app_label, model_name)
    if hasattr(model, 'live'):
        obj = get_object_or_404(model.live, pk=object_id)
    else:
        obj = get_object_or_404(model, pk=object_id)
    return obj, model

def get_template_list(obj, template):
    template_list = []
    if template is None:
        return []
    try:
        _ =  loader.get_template(template)
        template_list.append(template)
    except loader.TemplateDoesNotExist:
        if not template.endswith('/'):
            template.rstrip("/")
        # Consider all parent classes excluding Model.
        content_types = type(obj).mro()
        if Model in content_types:
            content_types.remove(Model)
        content_types = [ct for ct in content_types if hasattr(ct, '_meta')]
        ctype_strs = []
        for ctype in content_types:
            ctype_strs.append('%s.%s' % (ctype._meta.app_label, ctype._meta.module_name))
        
        tdirs = [template,]
        for tdir in tdirs:
            for ctype_str in ctype_strs:
                template_list.append('%s/%s.html' % (tdir, ctype_str))
            template_list.append('%s/default.html' % tdir)
    return template_list

def esi(request, app_label=None, model_name=None, object_id=None, timeout=900, template=None):
    """
    Using the app_label, module_name and object_id parameters create an object and render it using `template_name` or `template_dir`.
    
    Parameters:
        :app_label: `Name of a app (i.e. auth)`
        :model_name: `Name of a model (i.e. user)`
        :object_id: `This's objects primary key id`
        :timeout: `Time in secondsfor this objects max_age. [default 900]`
        :template: `a path to a template directory or a template`
        
    Context:
        `object`
            The object that was returned
        `model_name`
            If you are using a User object `user` will be in the context.
    
    Templates:
        if `template` is a directory:
            A file called `app_label`.`model_name`.html ,along with any other models'
            content types that the object extends, will be looked for in the `template`
            directory falling back to `template`/default.html 
            if none can be found.
        if `template` is a file:
            The file `template` will be loaded and rendered.
            
        If no template is provided `settings`.ESI_DEFAULT_TEMPLATE and `settings`.ESI_DEFAULT_DIRECTORY
        will be checked with the same logic as above.
        
    """
    default_template = getattr(settings, 'ESI_DEFAULT_TEMPLATE', None)
    default_template_dir = getattr(settings, 'ESI_DEFAULT_DIRECTORY', None)
    obj, model = get_object(app_label, model_name, object_id)
    template_list = []
    if template is not None:
        template_list.extend(get_template_list(obj, template))
    else:
        if default_template is not None:
            temp_t =  get_template_list(obj, default_template)
            if temp_t is not None:
                template_list.extend(get_template_list(obj, default_template))
        if default_template_dir is not None and len(template_list) == 0:
            temp_t =  get_template_list(obj, default_template_dir)
            if temp_t is not None:
                template_list.extend(get_template_list(obj, default_template_dir))
    if len(template_list) == 0:
        raise Http404
    t = loader.select_template(template_list)
    context = {
        'object': obj,
        model_name: obj
    }
    c = RequestContext(request, context)
    response = HttpResponse(t.render(c))
    populate_xheaders(request, response, model, getattr(obj, model._meta.pk.name))
    patch_cache_control(response, max_age=timeout)
    return response