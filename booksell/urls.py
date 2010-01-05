from django.conf.urls.defaults import *
from django.conf import settings

handler500 # Pyflakes

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^booksell/', include('booksell.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/(.*)', admin.site.root),
    (r'^accounts/login/$', 'django.contrib.auth.views.login'),
)

urlpatterns += patterns('booksell.views',
    (r'logout/$', 'logout_view'),
)

urlpatterns += patterns('books.views',
    (r'^$','index'),
    (r'^add$','add'),
    (r'^asxml/(?P<id>.*)/$','asxml'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
