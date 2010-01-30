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
    (r'^sold$','index_sold'),
    (r'^add$','add'),
    (r'^update$','bulk_update'),
    (r'^asxml/(?P<id>.*)/$','asxml'),
    (r'^conditions$','conditions'),
    (r'^condition/(?P<id>.*)/edit$','condition_edit'),
    (r'^condition/(?P<id>.*)/(?P<status>.*)$','condition_status'),
    (r'^conditionignore/(?P<id>.*)$','condition_ignore'),
    (r'^edit/(?P<id>.*)$','editbook'),
    (r'^add_condition/(?P<bookid>\d+)/(?P<conditionid>\d+)$','add_condition'),
    (r'^move_condition/(?P<bookcondid>\d+)/(?P<dir>.+)$','move_condition'),
    (r'^remove_condition/(?P<bookcondid>\d+)$','remove_condition'),
    (r'^delete/(?P<id>.*)$','deletebook'),
    (r'^sold/(?P<id>.*)$','soldbook'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', 
         {'document_root': settings.MEDIA_ROOT}),
    )
