from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'library.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'library_app.views.home', name='home'),
    url(r'^about/$', 'library_app.views.about', name='about'),
    url(r'^sign_in/$', 'library_app.views.sign_in', name='sign_in'),
    url(r'^sign_up/$', 'library_app.views.sign_up', name='sign_up'),

    url(r'^admin/', include(admin.site.urls)),
)
