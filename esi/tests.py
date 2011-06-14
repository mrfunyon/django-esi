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
try:
    from django.test import RequestFactory
except:
    RequestFactory = None
from django.template import Template, Context, RequestContext, TemplateSyntaxError
from esi.views import esi, get_object


class EsiTest(TestCase):
    def setUp(self):
        self.user, created = User.objects.get_or_create(username='testme', first_name='test',email='test@test.com', is_active=True)
        self.kwargs = {
            'app_label': self.user._meta.app_label,
            'model_name': self.user._meta.module_name,
            'object_id': self.user.pk,
            'timeout': 1200,
            'template': 'includes/lists/auth.user.html'
        }
        self.old_setting = {}
    
    def set_setting(self, setting, value):
        try:
            if getattr(settings, setting):
                self.old_setting.update({setting: getattr(settings, setting)})
        except AttributeError:
            self.old_setting.update({setting: None})
        setattr(settings, setting, value)
    
    def restore_setting(self, setting, default=None):
        if setting in self.old_setting.keys():
            setattr(settings, setting, self.old_setting[setting])
        else:
            setattr(settings, setting, default)
    
    def test_esi_templatetag(self):
        template = """
        {% load esi %}
        {% esi for object path 'includes/lists' timeout 1200 %}
        """
        t = Template(template)
        c = Context({"object": self.user})
        rendered = t.render(c).strip()
        args = self.kwargs.copy()
        del(args['template'])
        args.update({'template':'includes/lists'})
        url = reverse('esi',kwargs=args)
        
        comparison = """<esi:include src="%s" />"""%(url)
        self.assertEqual(rendered, comparison)
    
    def test_esi_templatetag_debug(self):
        """TODO: Figure this out."""
        # template = """
        # {% load esi %}
        # {% esi for object path 'includes/lists' timeout 1200 %}
        # """
        # self.set_setting('DEBUG', True)
        # c = Context({"object": self.user})
        # rendered = t.render(c).strip()
        # args = self.kwargs.copy()
        # del(args['template'])
        # args.update({'template':'includes/lists'})
        # url = reverse('esi',kwargs=args)
        #     
        # comparison = """<esi:include src="%s" />"""%(url)
        # self.assertEqual(rendered, comparison)
        # self.restore_setting('DEBUG', False)
        pass
        
        
    
    def test_esi_templatetag_no_path_error(self):
        template = """
        {% load esi %}
        {% esi for object path %}
        """
        self.assertRaises(TemplateSyntaxError, Template, (template))
    
    def test_esi_templatetag_no_timeout_error(self):
        template = """
        {% load esi %}
        {% esi for object path 'whee/bleep' timeout %}
        """
        self.assertRaises(TemplateSyntaxError, Template, (template))
    
    def test_esi_templatetag_no_template_error(self):
        template = """
        {% load esi %}
        {% esi for object template  %}
        """
        self.assertRaises(TemplateSyntaxError, Template, (template))
    
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
        esi(request, app_label=None, model_name=None, object_id=None, timeout=1200, template=None)
        """
        client = Client()
        url = reverse('esi',kwargs=self.kwargs)
        r = client.get(url)
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
        
        # render the template and compare them.
        t = loader.select_template([self.kwargs['template'],])
        context = {
            'object': self.user,
        }
        c = RequestContext(r.request, context)
        rendered = t.render(c)
        
        self.assertEqual(r.content, rendered)
    
    def test_esi_list_view(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        esi(request, app_label=None, model_name=None, object_id=None, timeout=1200, template=None)
        """
        client = Client()
        args = self.kwargs.copy()
        args.update({'template':'includes/lists'})
        
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
        
    
    def test_esi_view_default_directory(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        """
        client = Client()
        args = self.kwargs.copy()
        del(args['template'])
        self.set_setting('ESI_DEFAULT_DIRECTORY', 'includes/lists')
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        self.restore_setting('ESI_DEFAULT_DIRECTORY')
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
        
    def test_esi_default_template(self):
        """
        tests that the esi view sets the timeout cache header properly and renders the template correctly.
        """
        client = Client()
        args = self.kwargs.copy()
        del(args['template'])
        self.set_setting('ESI_DEFAULT_TEMPLATE', 'esi_test/esi.html')
        url = reverse('esi',kwargs=args)
        r = client.get(url)
        self.restore_setting('ESI_DEFAULT_TEMPLATE')
        age = int(r._headers['cache-control'][1].split("=")[1])
        self.assertEqual(self.kwargs['timeout'], age)
    
        #self.assertEqual(r.content, rendered)