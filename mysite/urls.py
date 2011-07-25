from django.conf.urls.defaults import *
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^mysite/', include('mysite.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', 'mysite.stockwatcher.views.index'),
    (r'^services/$', 'mysite.stockwatcher.views.service'),
    (r'^(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC}),
)
