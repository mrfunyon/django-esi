"""
ESI URLs
URL:
  /esi/app_label/module_name/object_id[/timeout]/template_name
vars:
  app_label = 'news'
  module_name = 'story'
  object_id= 12345
  timeout = 300
  template_name = 'news/story_detail.html'

example URL:
  /esi/news/story/12345/300/news/story_detail.html

"""
from django.conf.urls.defaults import *

urlpatterns = patterns('esi.views',
    url(r'^(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/$', 'esi', name='esi'),
    url(r'^(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/(?P<timeout>\d+)/$', 'esi', name='esi'),
    url(r'^(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/(?P<timeout>\d+)/(?P<template>[\w\-\/\.]+)/$', 'esi', name='esi'),
    #url(r'^list/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/$', 'esi', name='esi_list'),
    #url(r'^list/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/(?P<timeout>\d+)/$', 'esi', name='esi_list'),
    # this url and the one above are exactly the same, and the url resolver doesn't understand this....  TIME FOR REFACTORING!
    #url(r'^list/(?P<app_label>[\w-]+)/(?P<model_name>[\w-]+)/(?P<object_id>\d+)/(?P<timeout>\d+)/(?P<template_dir>[\w\-\/\.]+)/$', 'esi', name='esi_list'),
)
