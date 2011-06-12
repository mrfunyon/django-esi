"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.test import TestCase, Client
from esi.views import esi, get_object


class EsiTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='testme', first_name='test',email='test@test.com', is_active=True)
        self.kwargs = {
            'app_label': self.user._meta.app_label,
            'model_name': self.user._meta.module_name,
            'object_id': self.user.pk,
            'timeout': 900,
            'template_name': 'includes/lists/auth.user.html'
        }
    
    def test_esi_templatetag(self):
        template = """
        {% load esi %}
        {% esi for object path 'includes/lists/' timeout 1200 %}
        """
        t = Template(template)
        c = Context({"object": self.user})
        rendered = t.render(c).strip()
        args = kwargs.copy()
        del(args['template_name'])
        args.update({'template_dir':'includes/lists/'})
        url = reverse('esi_list',kwargs=args)
        
        comparison = """<esi:include src="%s" />"""%(url)
        self.assertEqual(rendered, comparison)
    
    def test_get_object(self):
        """
        Tests that get_object returns an object and the correct model for that object.
        """
        object, model = get_object(kwargs['app_label'], kwargs['model_name'], kwargs['object_id'])
        self.assertEqual(object, self.user)
        self.assertEqual(model, User)
    
    def test_esi_view(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        esi(request, app_label=None, model_name=None, object_id=None, timeout=900, template_name=None, template_dir=None)
        """
        client = Client()
        url = reverse('esi',kwargs=self.kwargs)
        r = client.get(url)
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(timeout, age)
        
        # render the template and compare them.
        t = loader.select_template([kwargs['template'],])
        context = {
            'object': self.user,
        }
        c = RequestContext(c.request, context)
        rendered = t.render(c)
        
        self.assertEqual(r.content, rendered)
    
