# Create your views here.
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.xheaders import populate_xheaders
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext, loader
from ellington.core.constants import LIVE_STATUS
from django.contrib.auth.decorators import permission_required
from django.utils.safestring import mark_safe
from django.db.models import Model, get_model
from django.utils.cache import patch_cache_control

def get_object(app_label, model_name, object_id):
    model = get_model(app_label, model_name)
    if hasattr(model, 'live'):
        obj = get_object_or_404(model.live, pk=object_id)
    else:
        obj = get_object_or_404(model, pk=object_id)
    return obj, model

def test_esi(request, app_label=None, model_name=None, object_id=None):
    obj, model = get_object(app_label, model_name, object_id)
    t = loader.select_template(['esi/esi_test.html',])
    context = {
        'object': obj,
    }
    c = RequestContext(request, context)
    response = HttpResponse(t.render(c))
    return response

def esi(request, app_label=None, model_name=None, object_id=None, timeout=900, template_name=None, template_dir=None):
    """
    Using the app_label, module_name and object_id parameters create an object and render it using `template_name` or `template_dir`.
    
    Parameters:
        :app_label: `Name of a app (i.e. auth)`
        :model_name: `Name of a model (i.e. user)`
        :object_id: `This's objects primary key id`
        :timeout: `Time in secondsfor this objects max_age.`
        :template_name: `full template path to the template to use to render the object`
        :template_dir: `Directory in which to render this object`
        
        `template_name` and `template_dir` are exclusive.
        
    Context:
        `object`
            The object that was returned
        `model_name`
            If you are using a User object `user` will be in the context.
    
    Templates:
        if `template_name` is used that template is used to render the object.
        
        if `template_dir` is used a file called `app_label`.`model_name`.html
        ,along with any other models' content types that the object extends,
        will be looked for in `template_dir` falling back to `template_dir`/default.html 
        if none can be found.
        
    """
    if template_name is None and template_dir is None:
        return Http404()
    if template_name is not None and template_dir is not None:
        return Http404()
    obj, model = get_object(app_label, model_name, object_id)
    template_list = []
    if template_name:
        template_list = [template_name,
            "includes/lists/%s.%s.html" % (obj._meta.app_label, obj._meta.module_name)
            ]
    if template_dir:
        # Consider all parent classes excluding Model.
        content_types = type(obj).mro()
        if Model in content_types:
            content_types.remove(Model)
        content_types = [ct for ct in content_types if hasattr(ct, '_meta')]
        
        ctype_strs = []
        for ctype in content_types:
            ctype_strs.append('%s.%s' % (ctype._meta.app_label, ctype._meta.module_name))
        
        tdirs = [template_dir,]
        for tdir in tdirs:
            for ctype_str in ctype_strs:
                template_list.append('%s/%s.html' % (tdir, ctype_str))
            template_list.append('%s/default.html' % tdir)
    if len(template_list) ==0:
        return Http404()
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