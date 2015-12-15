from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'home.views.login', name='login'),
    url(r'^home$', 'home.views.home', name='home'),
    url(r'^profile', 'home.views.profile', name='profile'),
    url(r'^tweet', 'home.views.tweet', name='tweet'),
    url(r'^query', 'home.views.query', name='query'),
    url(r'^media/photo', 'home.views.media_photo', name='media_photo'),
    url(r'^media/video', 'home.views.media_video', name='media_video'),
    url(r'^media/inspector', 'home.views.media_inspector', name='media_inspector'),
    url(r'^media', 'home.views.media_video', name='media_video'),
    url(r'^logout$', 'home.views.logout', name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^admin/', include(admin.site.urls)),
)
