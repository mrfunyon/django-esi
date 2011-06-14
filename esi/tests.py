"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.template import RequestContext, loader
from django.test import TestCase, Client
from django.template import Template, Context, RequestContext
from esi.views import esi, get_object


class EsiTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='testme', first_name='test',email='test@test.com', is_active=True)
        self.kwargs = {
            'app_label': self.user._meta.app_label,
            'model_name': self.user._meta.module_name,
            'object_id': self.user.pk,
            'timeout': 1200,
            'template_name': 'includes/lists/auth.user.html'
        }
        self.old_setting = {}
    
    def set_setting(self, setting, value):
        try:
            if getattr(settings, setting):
                self.old_setting.update({setting: getattr(settings, setting)})
        except AttributeError:
            pass
        setattr(settings, setting, value)
    def restore_setting(self, setting):
        if setting in self.old_setting.keys():
            setattr(setting, setting, self.old_setting[setting])
    
    def test_esi_templatetag(self):
        template = """
        {% load esi %}
        {% esi for object path 'includes/lists' timeout 1200 %}
        """
        t = Template(template)
        c = Context({"object": self.user})
        rendered = t.render(c).strip()
        args = self.kwargs.copy()
        del(args['template_name'])
        args.update({'template_dir':'includes/lists'})
        url = reverse('esi',kwargs=args)
        
        comparison = """<esi:include src="%s" />"""%(url)
        self.assertEqual(rendered, comparison)
    
    def test_get_object(self):
        """
        Tests that get_object returns an object and the correct model for that object.
        """
        object, model = get_object(self.kwargs['app_label'], self.kwargs['model_name'], self.kwargs['object_id'])
        self.assertEqual(object, self.user)
        self.assertEqual(model, User)
    
    def test_esi_view(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        esi(request, app_label=None, model_name=None, object_id=None, timeout=1200, template_name=None, template_dir=None)
        """
        client = Client()
        url = reverse('esi',kwargs=self.kwargs)
        r = client.get(url)
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
        
        # render the template and compare them.
        t = loader.select_template([self.kwargs['template_name'],])
        context = {
            'object': self.user,
        }
        c = RequestContext(r.request, context)
        rendered = t.render(c)
        
        self.assertEqual(r.content, rendered)
    
    def test_esi_list_view(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        esi(request, app_label=None, model_name=None, object_id=None, timeout=1200, template_name=None, template_dir=None)
        """
        client = Client()
        args = self.kwargs.copy()
        del(args['template_name'])
        args.update({'template_dir':'includes/lists/'})
        
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
        
        #self.assertEqual(r.content, rendered)
    
    def test_esi_view_errors(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        esi(request, app_label=None, model_name=None, object_id=None, timeout=1200, template_name=None, template_dir=None)
        """
        client = Client()
        args = self.kwargs.copy()
        del(args['template_name'])
        self.set_setting('ESI_DEFAULT_TEMPLATE', 'esi_test/esi.html')
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        print r.content
        self.restore_setting('ESI_DEFAULT_TEMPLATE')
        self.set_setting('ESI_DEFAULT_DIRECTORY', 'includes/lists')
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        print r.content
        self.restore_setting('ESI_DEFAULT_DIRECTORY')
        #<a href='{{object.get_absolute_url}}'>{{object.username}}</a>
        #args.update({'template_dir':'includes/lists/'})
        
        
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
    
        #self.assertEqual(r.content, rendered)