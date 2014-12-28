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
    url(r'^logout/$', 'library_app.views.logout_view', name='logout'),
    url(r'^books/$', 'library_app.views.books', name='books'),
    url(r'^books/show/(?P<book_id>\w{0,5})/$', 'library_app.views.books_show', name='books_show'),
    url(r'^authors/$', 'library_app.views.authors', name='authors'),
    url(r'^authors/show/(?P<author_id>\w{0,5})/$', 'library_app.views.authors_show', name='authors_show'),
    url(r'^publishers/$', 'library_app.views.publishers', name='publishers'),
    url(r'^publishers/show/(?P<publisher_id>\w{0,5})/$', 'library_app.views.publishers_show', name='publishers_show'),
    url(r'^periods/$', 'library_app.views.periods', name='periods'),
    url(r'^periods/show/(?P<period_id>\w{0,5})/$', 'library_app.views.periods_show', name='periods_show'),
    url(r'^authors/new$', 'library_app.views.new_author', name='new_author'),

    url(r'^change_password/$', 'library_app.views.change_password', name='change_password'),

    # url(r'^accounts/password_change/$',  # hijack password_change's url
    #     'django.contrib.auth.views.password_change',
    #     {'password_change_form': AdminPasswordChangeForm},
    #     name="password_change"),

    url(r'^my_quotations/$', 'library_app.views.user_quotations', name='user_quotations'),

    url(r'^users/(?P<username>\w{0,30})/$', 'library_app.views.user', name='user'),
    url(r'^useredit/$', 'library_app.views.useredit', name='useredit'),
    url(r'^books/borrow/(?P<book_id>\w{0,5})/$', 'library_app.views.borrow_book', name='borrow_book'),
    url(r'^books/return/(?P<book_id>\w{0,5})/$', 'library_app.views.return_book', name='return_book'),

    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.contrib.staticfiles.views',
        url(r'^static/(?P<path>.*)$', 'serve'),
    )
