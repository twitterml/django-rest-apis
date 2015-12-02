from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'home.views.login', name='login'),
    url(r'^home$', 'home.views.home', name='home'),
    url(r'^profile', 'home.views.profile', name='profile'),
    url(r'^tweet', 'home.views.tweet', name='tweet'),
    url(r'^query', 'home.views.query', name='query'),
    url(r'^media', 'home.views.media', name='media'),
    url(r'^logout$', 'home.views.logout', name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)
